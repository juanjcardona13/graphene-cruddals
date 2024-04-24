import re
import graphene
from typing import Any, OrderedDict, Dict, Literal, Tuple, Type, Union
from collections.abc import Iterable
from cruddals.utils.typing.custom_typing import FunctionType, NameCaseType, RootFieldsType, TypeRegistryForModel
from cruddals.registry.registry_global import RegistryGlobal

class Promise:
    """
    Base class for the proxy class created in the closure of the lazy function.
    It's used to recognize promises in code.
    """
    pass

def build_class(name: str, bases: tuple = (), attrs: dict = None) -> Any:
    if attrs is None:
        attrs = {}
    return type(name, bases, attrs)


def delete_keys(obj: dict, keys: list[str]) -> dict:
    for key in keys:
        if key in obj:
            del obj[key]
    return obj


def is_iterable(obj: Any, exclude_string=True) -> bool:
    if exclude_string:
        return isinstance(obj, Iterable) and not isinstance(obj, str)
    return isinstance(obj, Iterable)


def _camelize_django_str(string: str) -> str:
    # if isinstance(string, Promise):
    #     string = force_str(string) # force_str is a function of Django
    return transform_string(string, "camelCase") if isinstance(string, str) else string


def camelize(data):
    if isinstance(data, dict):
        return {_camelize_django_str(k): camelize(v) for k, v in data.items()}
    if is_iterable(data) and not isinstance(data, (str, Promise)):
        return [camelize(d) for d in data]
    return data


def camel_to_snake(s: Union[str, bytes]) -> str:
    s = str(s)
    s = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", s)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s).lower()


def transform_string(
    s: Union[str, bytes],
    type: Literal["PascalCase", "camelCase", "snake_case", "kebab-case", "lowercase"],
) -> str:
    """Type: PascalCase, camelCase, snake_case, kebab-case, lowercase"""
    s = str(s)
    if " " in s or "_" in s or "-" in s:
        separator = " " if " " in s else "_" if "_" in s else "-"
        if type == "PascalCase":
            return "".join(word.title() for word in s.split(separator))
        elif type == "snake_case":
            return "_".join(word.lower() for word in s.split(separator))
        elif type == "kebab-case":
            return "-".join(word.lower() for word in s.split(separator))
        elif type == "lowercase":
            return "".join(word.lower() for word in s.split(separator))
        elif type == "camelCase":
            return (
                s[0].lower() + "".join(word.title() for word in s.split(separator))[1:]
            )
        else:
            return "".join(word for word in s.split(separator))
    else:
        if type == "PascalCase":
            if s[0] == s.title()[0]:
                return s
            else:
                return s.title()
        elif type == "lowercase":
            return s.lower()
        elif type == "camelCase":
            return s[0].lower() + s[1:]
        else:
            return s


def merge_dict(
    source: dict,
    destination: dict,
    overwrite: bool = False,
    keep_both: bool = False,
    path: Union[list[str], None] = None,
) -> Union[dict, OrderedDict]:
    "Merges source into destination"

    if path is None:
        path = []

    new_destination = OrderedDict() if isinstance(destination, OrderedDict) else {}

    for key in destination:
        if key in source:
            if isinstance(destination[key], dict) and isinstance(source[key], dict):
                new_destination[key] = merge_dict(
                    source[key], destination[key], overwrite, keep_both, path + [str(key)]
                )
            elif destination[key] == source[key]:
                new_destination[key] = destination[key]
            else:
                if keep_both:
                    if isinstance( destination[key], (list, tuple, set), ) and isinstance( source[key], (list, tuple, set), ):
                        new_destination[key] = destination[key] + source[key]
                    else:
                        new_destination[key] = [destination[key], source[key]]
                elif overwrite:
                    new_destination[key] = destination[key]
                else:
                    raise ValueError("Conflict at %s" % ".".join(path + [str(key)]))
        else:
            new_destination[key] = destination[key]

    for key in source:
        if key not in destination:
            new_destination[key] = source[key]

    return new_destination


def get_name_of_model_in_different_case( name_model="", name_model_plural="", prefix="", suffix="" ) -> NameCaseType:
    # snake_case
    # kebab-case
    # camelCase
    # PascalCase

    name_model = transform_string(name_model, "camelCase")
    name_model_plural = transform_string(name_model_plural, "camelCase")

    prefix_lower = prefix.lower()
    prefix_capitalize = prefix.capitalize()

    suffix_lower = suffix.lower()
    suffix_capitalize = suffix.capitalize()

    snake_case = f"{prefix_lower}{'_' if prefix else ''}{camel_to_snake(name_model)}{'_' if suffix else ''}{suffix_lower}"
    plural_snake_case = f"{prefix_lower}{'_' if prefix else ''}{camel_to_snake(name_model_plural)}{'_' if suffix else ''}{suffix_lower}"

    camel_case = f"{prefix_capitalize}{name_model}{suffix_capitalize}"
    plural_camel_case = f"{prefix_lower}{name_model_plural}{suffix_capitalize}"

    pascal_case = f"{prefix_capitalize}{transform_string(name_model, 'PascalCase')}{suffix_capitalize}"
    plural_pascal_case = f"{prefix_capitalize}{transform_string(name_model_plural, 'PascalCase')}{suffix_capitalize}"

    return {
        "snake_case": snake_case,
        "plural_snake_case": plural_snake_case,
        "camel_case": camel_case,
        "plural_camel_case": plural_camel_case,
        "pascal_case": pascal_case,
        "plural_pascal_case": plural_pascal_case,
    }


def exists_conversion_for_model( model: Dict[str, Any], registry: RegistryGlobal, type_of_registry: TypeRegistryForModel ) -> bool:
    registries_for_model = registry.get_registry_for_model(model)
    if registries_for_model is not None and type_of_registry in registries_for_model:
        return True
    return False


def get_converted_model( model: Dict[str, Any], registry: RegistryGlobal, type_of_registry: TypeRegistryForModel ):
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
