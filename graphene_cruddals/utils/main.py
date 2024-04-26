import re
import graphene
from typing import Any, List, OrderedDict, Dict, Literal, Tuple, Type, Union
from collections.abc import Iterable
from graphene_cruddals.utils.typing.custom_typing import FunctionType, NameCaseType, RootFieldsType, TypeRegistryForModel
from graphene_cruddals.registry.registry_global import RegistryGlobal

class Promise:
    """
    Base class for the proxy class created in the closure of the lazy function.
    It's used to recognize promises in code.
    """
    pass


def build_class(name: str, bases: tuple = (), attrs: Union[dict, None] = None) -> Any:
    """
    Dynamically builds a class with the given name, bases, and attributes.

    Args:
        name (str): The name of the class.
        bases (tuple, optional): The base classes of the class. Defaults to ().
        attrs (Union[dict, None], optional): The attributes of the class. Defaults to None.

    Returns:
        Any: The dynamically built class.
    """
    if attrs is None:
        attrs = {}
    return type(name, bases, attrs)


def delete_keys(obj: dict, keys: list[str]) -> dict:
    """
    Deletes the specified keys from the given dictionary.

    Args:
        obj (dict): The dictionary from which keys will be deleted.
        keys (list[str]): The list of keys to be deleted.

    Returns:
        dict: The modified dictionary with the specified keys removed.
    """
    for key in keys:
        if key in obj:
            del obj[key]
    return obj


def is_iterable(obj: Any, exclude_string=True) -> bool:
    """
    Check if an object is iterable.

    Args:
        obj (Any): The object to check.
        exclude_string (bool, optional): Whether to exclude strings from being considered iterable. Defaults to True.

    Returns:
        bool: True if the object is iterable, False otherwise.
    """
    if exclude_string:
        return isinstance(obj, Iterable) and not isinstance(obj, str)
    return isinstance(obj, Iterable)


def _camelize_django_str(string: str) -> str:
    """
    Converts a string to camel case if it is an instance of str.
    
    Parameters:
        string (str): The string to be converted.
        
    Returns:
        str: The converted string in camel case if it is an instance of str, otherwise returns the original string.
    """
    return transform_string(string, "camelCase") if isinstance(string, str) else string


def camelize(data):
    """
    Recursively converts the keys of a dictionary to camel case.

    Args:
        data (dict or iterable): The data to be camelized.

    Returns:
        dict or iterable: The camelized data.

    """
    if isinstance(data, dict):
        return {_camelize_django_str(k): camelize(v) for k, v in data.items()}
    if is_iterable(data) and not isinstance(data, (str, Promise)):
        return [camelize(d) for d in data]
    return data


def camel_to_snake(s: Union[str, bytes]) -> str:
    """
    Converts a camel case string to snake case.

    Args:
        s (Union[str, bytes]): The input string to be converted.

    Returns:
        str: The converted string in snake case.
    """
    s = str(s)
    s = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", s)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s).lower()


def get_separator(s: str) -> str:
    """
    Gets the separator from a string.

    Args:
        s (str): The input string.

    Returns:
        str: The separator.
    """
    if " " in s:
        return " "
    elif "_" in s:
        return "_"
    elif "-" in s:
        return "-"
    else:
        return ""


def transform_string_with_separator(s: str, type: Literal["PascalCase", "camelCase", "snake_case", "kebab-case", "lowercase"], actual_separator: str) -> str:
    """
    Transform the input string based on the specified type and actual separator.

    Args:
        s (str): The input string to be transformed.
        type (Literal["PascalCase", "camelCase", "snake_case", "kebab-case", "lowercase"]): 
            The type of transformation to be applied. Valid options are:
            - "PascalCase": Convert the string to PascalCase.
            - "camelCase": Convert the string to camelCase.
            - "snake_case": Convert the string to snake_case.
            - "kebab-case": Convert the string to kebab-case.
            - "lowercase": Convert the string to lowercase.
        actual_separator (str): The actual separator in the input string.

    Returns:
        str: The transformed string.
    """
    if actual_separator:
        if type == "PascalCase":
            return "".join(word.title() for word in s.split(actual_separator))
        elif type == "snake_case":
            return "_".join(word.lower() for word in s.split(actual_separator))
        elif type == "kebab-case":
            return "-".join(word.lower() for word in s.split(actual_separator))
        elif type == "lowercase":
            return "".join(word.lower() for word in s.split(actual_separator))
        elif type == "camelCase":
            return (
                s[0].lower() + "".join(word.title() for word in s.split(actual_separator))[1:]
            )
        else:
            return "".join(word for word in s.split(actual_separator))
    else:
        raise ValueError("actual_separator cannot be empty.")


def transform_string( s: Union[str, bytes], type: Literal["PascalCase", "camelCase", "snake_case", "kebab-case", "lowercase"], ) -> str:
    """
    Transform the input string based on the specified type.

    Args:
        s (Union[str, bytes]): The input string to be transformed.
        type (Literal["PascalCase", "camelCase", "snake_case", "kebab-case", "lowercase"]): 
            The type of transformation to be applied. Valid options are:
            - "PascalCase": Convert the string to PascalCase.
            - "camelCase": Convert the string to camelCase.
            - "snake_case": Convert the string to snake_case.
            - "kebab-case": Convert the string to kebab-case.
            - "lowercase": Convert the string to lowercase.

    Returns:
        str: The transformed string.
    """
    s = str(s)
    if not s:
        return s
    separator = get_separator(s)
    if separator:
        return transform_string_with_separator(s, type, separator)
    else:
        if type == "PascalCase":
            if s[0].islower():
                s = s[0].upper() + s[1:]
            return s
        elif type == "lowercase":
            return s.lower()
        elif type == "camelCase":
            return s[0].lower() + s[1:]
        elif type == "snake_case":
            return camel_to_snake(s)
        elif type == "kebab-case":
            return transform_string_with_separator(camel_to_snake(s), "kebab-case", "_")
        else:
            return s


def merge_dict(source: dict, destination: dict, overwrite: bool = False, keep_both: bool = False, path: Union[list[str], None] = None) -> Union[dict, OrderedDict]:
    """
    Merge two dictionaries recursively.

    Args:
        source (dict): The dictionary to merge from.
        destination (dict): The dictionary to merge into.
        overwrite (bool, optional): If True, overwrite values in destination with values from source. Defaults to False.
        keep_both (bool, optional): If True, keep both values from source and destination in case of conflicts. Defaults to False.
        path (Union[list[str], None], optional): The path to the current nested dictionary. Defaults to None.

    Returns:
        Union[dict, OrderedDict]: The merged dictionary.
    """
    if path is None:
        path = []

    new_destination = OrderedDict() if isinstance(destination, OrderedDict) else {}

    for key in destination:
        if key in source:
            new_destination[key] = merge_nested_dicts(source, destination, key, overwrite, keep_both, path)
        else:
            new_destination[key] = destination[key]

    for key in source:
        if key not in destination:
            new_destination[key] = source[key]

    return new_destination


def merge_nested_dicts(source: dict, destination: dict, key: str, overwrite: bool, keep_both: bool, path: list[str]) -> Any:
    """
    Merge nested dictionaries by recursively merging their key-value pairs.

    Args:
        source (dict): The source dictionary to merge.
        destination (dict): The destination dictionary to merge into.
        key (str): The key to merge.
        overwrite (bool): Flag indicating whether to overwrite the destination value with the source value if there is a conflict.
        keep_both (bool): Flag indicating whether to keep both values if there is a conflict.
        path (list[str]): The path of keys leading to the current key.

    Returns:
        Any: The merged value.

    Raises:
        ValueError: If there is a conflict and both `keep_both` and `overwrite` are False.

    """
    if isinstance(destination[key], dict) and isinstance(source[key], dict):
        return merge_dict(source[key], destination[key], overwrite, keep_both, path + [str(key)])
    elif destination[key] == source[key]:
        return destination[key]
    else:
        if keep_both:
            return merge_both_values(source[key], destination[key])
        elif overwrite:
            return destination[key]
        else:
            raise ValueError("Conflict at %s" % ".".join(path + [str(key)]))


def merge_both_values(value1: Any, value2: Any) -> List[Any]:
    """
    Merge two values into a list.

    Args:
        value1 (Any): The first value to merge.
        value2 (Any): The second value to merge.

    Returns:
        List[Any]: A list containing both values.

    """
    if isinstance(value1, (list, tuple, set)) and isinstance(value2, (list, tuple, set)):
        return list(value1) + list(value2)
    else:
        return [value1, value2]


def get_name_of_model_in_different_case(name_model:str, name_model_plural="", prefix="", suffix="") -> NameCaseType:
    """
    Get the name of a model in different cases.

    Args:
        name_model (str): The name of the model.
        name_model_plural (str): The plural form of the model name.
        prefix (str): The prefix to be added to the model name.
        suffix (str): The suffix to be added to the model name.

    Returns:
        dict: A dictionary containing the name of the model in different cases.
            - snake_case: The model name in snake_case.
            - plural_snake_case: The plural form of the model name in snake_case.
            - camel_case: The model name in camelCase.
            - plural_camel_case: The plural form of the model name in camelCase.
            - pascal_case: The model name in PascalCase.
            - plural_pascal_case: The plural form of the model name in PascalCase.
    """
    if not name_model:
        raise ValueError("name_model cannot be empty.")
    if not name_model_plural:
        name_model_plural = name_model + "s"
    
    camel_case_name_model = transform_string(name_model, "camelCase")
    camel_case_name_model_plural = transform_string(name_model_plural, "camelCase")

    pascal_case_name_model = transform_string(camel_case_name_model, "PascalCase")
    pascal_case_name_model_plural = transform_string(camel_case_name_model_plural, "PascalCase")

    prefix_lower = prefix.lower()
    prefix_capitalize = prefix.capitalize()

    suffix_lower = suffix.lower()
    suffix_capitalize = suffix.capitalize()

    snake_case = f"{prefix_lower}{'_' if prefix else ''}{camel_to_snake(camel_case_name_model)}{'_' if suffix else ''}{suffix_lower}"
    plural_snake_case = f"{prefix_lower}{'_' if prefix else ''}{camel_to_snake(camel_case_name_model_plural)}{'_' if suffix else ''}{suffix_lower}"

    camel_case = f"{prefix_lower}{pascal_case_name_model if prefix else camel_case_name_model}{suffix_capitalize}"
    plural_camel_case = f"{prefix_lower}{pascal_case_name_model_plural if prefix else camel_case_name_model_plural}{suffix_capitalize}"

    pascal_case = f"{prefix_capitalize}{pascal_case_name_model}{suffix_capitalize}"
    plural_pascal_case = f"{prefix_capitalize}{pascal_case_name_model_plural}{suffix_capitalize}"

    return {
        "snake_case": snake_case,
        "plural_snake_case": plural_snake_case,
        "camel_case": camel_case,
        "plural_camel_case": plural_camel_case,
        "pascal_case": pascal_case,
        "plural_pascal_case": plural_pascal_case,
    }


def exists_conversion_for_model(model: Dict[str, Any], registry: RegistryGlobal, type_of_registry: TypeRegistryForModel) -> bool:
    """
    Check if there exists a conversion for the given model in the registry.

    Args:
        model (Dict[str, Any]): The model to check for conversion.
        registry (RegistryGlobal): The global registry containing the conversions.
        type_of_registry (TypeRegistryForModel): The type of registry to check for.

    Returns:
        bool: True if a conversion exists, False otherwise.
    """
    registries_for_model = registry.get_registry_for_model(model)
    if registries_for_model is not None and type_of_registry in registries_for_model:
        return True
    return False


def get_converted_model(model: Dict[str, Any], registry: RegistryGlobal, type_of_registry: TypeRegistryForModel):
    """
    Get the converted model for a given registry and type.

    Args:
        model (Dict[str, Any]): The model to get the converted version of.
        registry (RegistryGlobal): The global registry containing the converted models.
        type_of_registry (TypeRegistryForModel): The type of registry to retrieve the converted model from.

    Returns:
        Any: The converted model for the given registry and type.

    Raises:
        ValueError: If the model has not been converted to the specified type of registry.
    """
    registries_for_model = registry.get_registry_for_model(model)
    if registries_for_model is not None and type_of_registry in registries_for_model:
        return registries_for_model[type_of_registry]
    else:
        raise ValueError(
            f"The model {model} has not been converted to {type_of_registry}"
        )


def validate_list_func_cruddals(
    functions: Tuple[FunctionType, ...], exclude_functions: Tuple[FunctionType, ...]
) -> bool:
    """
    Validates the provided list of functions for CRUDDALS operations.

    Args:
        functions (Tuple[FunctionType, ...]): A tuple of functions to be validated.
        exclude_functions (Tuple[FunctionType, ...]): A tuple of functions to be excluded from validation.

    Returns:
        bool: True if the validation is successful.

    Raises:
        ValueError: If both 'functions' and 'exclude_functions' are provided.
        ValueError: If any of the functions in the input list is not a valid CRUDDALS operation.

    """
    valid_values = [
        "create",
        "read",
        "update",
        "delete",
        "deactivate",
        "activate",
        "list",
        "search",
    ]

    if functions and exclude_functions:
        raise ValueError(
            "You cannot provide both 'functions' and 'exclude_functions'. Please provide only one."
        )
    else:
        name_input = "function" if functions else "exclude_function"
        input_list = functions if functions else exclude_functions

    invalid_values = [value for value in input_list if value not in valid_values]

    if invalid_values:
        raise ValueError(
            f"Expected in '{name_input}' a tuple with some of these values {valid_values}, but got these invalid values {invalid_values}"
        )

    return True


def get_schema_query_mutation(
    queries: Tuple[Type[graphene.ObjectType], ...] = (),
    attrs_for_query: Union[Dict[str, graphene.Field], None] = None,
    mutations: Tuple[Type[graphene.ObjectType], ...] = (),
    attrs_for_mutation: Union[Dict[str, graphene.Field], None] = None,
) -> Tuple[
    graphene.Schema, Type[graphene.ObjectType], Union[Type[graphene.ObjectType], None]
]:
    """
    Builds a GraphQL schema with query and mutation types.

    Args:
        queries (Tuple[Type[graphene.ObjectType], ...], optional): Tuple of query types to include in the schema. Defaults to ().
        attrs_for_query (Union[Dict[str, graphene.Field], None], optional): Additional attributes for the query type. Defaults to None.
        mutations (Tuple[Type[graphene.ObjectType], ...], optional): Tuple of mutation types to include in the schema. Defaults to ().
        attrs_for_mutation (Union[Dict[str, graphene.Field], None], optional): Additional attributes for the mutation type. Defaults to None.

    Returns:
        Tuple[graphene.Schema, Type[graphene.ObjectType], Union[Type[graphene.ObjectType], None]]: A tuple containing the GraphQL schema, the query type, and the mutation type (if any).
    """
    if attrs_for_query is None:
        attrs_for_query = {}
    if attrs_for_mutation is None:
        attrs_for_mutation = {}
    base = (graphene.ObjectType,)
    query: Type[graphene.ObjectType] = build_class(
        name="Query", bases=(queries + base), attrs=attrs_for_query
    )

    dict_for_schema: RootFieldsType = {"query": query, "mutation": None}

    mutation: Union[Type[graphene.ObjectType], None] = None
    if mutations or attrs_for_mutation:
        attrs_for_mutation = {} if attrs_for_mutation is None else attrs_for_mutation
        mutation = build_class(
            name="Mutation", bases=(mutations + base), attrs=attrs_for_mutation
        )
        dict_for_schema.update({"mutation": mutation})

    schema = graphene.Schema(**dict_for_schema)

    return schema, query, mutation
