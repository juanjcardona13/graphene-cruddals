from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, OrderedDict, Tuple, Type, Union

import graphene
from graphene.utils.subclass_with_meta import SubclassWithMeta
from graphene.utils.props import props as graphene_get_props
from graphene.utils.str_converters import to_snake_case

from graphene_cruddals.types.utils import (
    convert_model_to_model_filter_input_object_type,
    convert_model_to_model_mutate_input_object_type,
    convert_model_to_model_object_type,
    convert_model_to_model_order_by_input_object_type,
    convert_model_to_model_paginated_object_type,
)
from graphene_cruddals.utils.typing.custom_typing import (
    GRAPHENE_TYPE,
    FunctionType,
    ModifyArgument,
    NameCaseType,
    TypesMutationEnum,
    CruddalsInterfaceNames,
    MetaCruddalsInterfaceNames,
    INTERFACES_NAME_CRUDDALS,
    CLASS_INTERFACE_FIELDS_NAMES,
    CLASS_INTERFACE_TYPE_NAMES,
    TypeRegistryForModelEnum,
)
from graphene_cruddals.operation_fields.main import (
    ModelActivateField,
    ModelCreateUpdateField,
    ModelDeactivateField,
    ModelDeleteField,
    ModelListField,
    PaginationConfigInput,
    ModelReadField,
    ModelSearchField,
)
from graphene_cruddals.registry.registry_global import (
    RegistryGlobal,
    get_global_registry,
)
from graphene_cruddals.utils.main import (
    delete_keys,
    get_name_of_model_in_different_case,
    get_schema_query_mutation,
    merge_dict,
    validate_list_func_cruddals,
)


@dataclass
class CruddalsBuilderConfig:
    """
    Configuration class for building CRUDDALS models.

    Attributes:
        model (Dict[str, Any]): The model dictionary representing the data structure.
        pascal_case_name (str): The name of the model in PascalCase.
        output_field_converter_function (Callable): Function to convert model fields to GraphQL output fields.
        input_field_converter_function (Callable): Function to convert model fields to GraphQL input fields.
        create_input_field_converter_function (Callable): Function to convert model fields to GraphQL input fields, Specialized for create operation.
        update_input_field_converter_function (Callable): Function to convert model fields to GraphQL input fields, Specialized for update operation.
        filter_field_converter_function (Callable): Function to convert model fields to GraphQL input fields, Specialized for filtering.
        order_by_field_converter_function (Callable): Function to convert model fields to GraphQL input fields, Specialized for ordering.
        create_resolver (Callable): Resolver function for create operation.
        read_resolver (Callable): Resolver function for read operation.
        update_resolver (Callable): Resolver function for update operation.
        delete_resolver (Callable): Resolver function for delete operation.
        deactivate_resolver (Callable): Resolver function for deactivate operation.
        activate_resolver (Callable): Resolver function for activate operation.
        list_resolver (Callable): Resolver function for list operation.
        search_resolver (Callable): Resolver function for search operation.
        plural_pascal_case_name (Union[str, None]): Plural form of the PascalCase name, if not provided, it uses the PascalCase name with an 's' suffix.
        prefix (str): Prefix to be added to model name, defaults to an empty string.
        suffix (str): Suffix to be added to model name, defaults to an empty string.
        interfaces (Union[tuple[Type[Any], ...], None]): Tuple of CRUDDALS interfaces to extend the functionality of CRUDDALS, defaults to None.
        exclude_interfaces (Union[Tuple[str, ...], None]): Tuple of interface names to exclude, defaults to None.
        registry (Union[RegistryGlobal, None]): Global registry for models, defaults to None, if not provided, it uses the global registry.
    """

    model: Dict[str, Any]
    pascal_case_name: str
    output_field_converter_function: Callable[[Any], GRAPHENE_TYPE]
    input_field_converter_function: Callable[[Any], GRAPHENE_TYPE]
    create_input_field_converter_function: Callable[[Any], GRAPHENE_TYPE]
    update_input_field_converter_function: Callable[[Any], GRAPHENE_TYPE]
    filter_field_converter_function: Callable[[Any], GRAPHENE_TYPE]
    order_by_field_converter_function: Callable[[Any], GRAPHENE_TYPE]
    create_resolver: Callable[..., Any]
    read_resolver: Callable[..., Any]
    update_resolver: Callable[..., Any]
    delete_resolver: Callable[..., Any]
    deactivate_resolver: Callable[..., Any]
    activate_resolver: Callable[..., Any]
    list_resolver: Callable[..., Any]
    search_resolver: Callable[..., Any]
    plural_pascal_case_name: Union[str, None] = None
    prefix: str = ""
    suffix: str = ""
    interfaces: Union[tuple[Type[Any], ...], None] = None
    exclude_interfaces: Union[Tuple[str, ...], None] = None
    registry: Union[RegistryGlobal, None] = None

    def __post_init__(self):
        """
        Performs post-initialization checks for the configuration.
        """
        if self.model is None:
            raise ValueError("model is required")
        if not self.pascal_case_name:
            raise ValueError("pascal_case_name is required")
        if not self.plural_pascal_case_name:
            self.plural_pascal_case_name = f"{self.pascal_case_name}s"


class BaseCruddals:
    """
    Base class for build CRUDDALS operations.

    Attributes:
        model (Dict[str, Any]): The model dictionary.
        prefix (str): Prefix to be used in naming.
        suffix (str): Suffix to be used in naming.
        model_name_in_different_case (NameCaseType): Model names in various cases.
        registry (RegistryGlobal): Global registry instance.
        cruddals_config (CruddalsBuilderConfig): Configuration for CRUDDALS builder.
        model_as_object_type (Type[graphene.ObjectType]): model converted to GraphQL ObjectType.
        model_as_paginated_object_type (Type[graphene.ObjectType]): GraphQL ObjectType for paginated response including the model converted to ObjectType.
        model_as_input_object_type (Type[graphene.InputObjectType]): model converted to GraphQL InputObjectType for connect operations.
        model_as_create_input_object_type (Type[graphene.InputObjectType]): model converted to GraphQL InputObjectType for create operations.
        model_as_update_input_object_type (Type[graphene.InputObjectType]): model converted to GraphQL InputObjectType for update operations.
        model_as_filter_input_object_type (Type[graphene.InputObjectType]): model converted to GraphQL InputObjectType for filtering.
        model_as_order_by_input_object_type (Type[graphene.InputObjectType]): model converted to GraphQL InputObjectType for ordering.
        create_field (Union[ModelCreateUpdateField, None]): Graphene Field configuration for create operation.
        read_field (Union[ModelReadField, None]): Graphene Field configuration for read operation.
        update_field (Union[ModelCreateUpdateField, None]): Graphene Field configuration for update operation.
        delete_field (Union[ModelDeleteField, None]): Graphene Field configuration for delete operation.
        deactivate_field (Union[ModelDeactivateField, None]): Graphene Field configuration for deactivate operation.
        activate_field (Union[ModelActivateField, None]): Graphene Field configuration for activate operation.
        list_field (Union[ModelListField, None]): Graphene Field configuration for list operation.
        search_field (Union[ModelSearchField, None]): Graphene Field configuration for search operation.
    """

    model: Dict[str, Any]
    prefix: str = ""
    suffix: str = ""
    model_name_in_different_case: NameCaseType
    registry: RegistryGlobal
    cruddals_config: CruddalsBuilderConfig
    model_as_object_type: Type[graphene.ObjectType]
    model_as_paginated_object_type: Type[graphene.ObjectType]
    model_as_input_object_type: Type[graphene.InputObjectType]
    model_as_create_input_object_type: Type[graphene.InputObjectType]
    model_as_update_input_object_type: Type[graphene.InputObjectType]
    model_as_filter_input_object_type: Type[graphene.InputObjectType]
    model_as_order_by_input_object_type: Type[graphene.InputObjectType]
    create_field: Union[ModelCreateUpdateField, None] = None
    read_field: Union[ModelReadField, None] = None
    update_field: Union[ModelCreateUpdateField, None] = None
    delete_field: Union[ModelDeleteField, None] = None
    deactivate_field: Union[ModelDeactivateField, None] = None
    activate_field: Union[ModelActivateField, None] = None
    list_field: Union[ModelListField, None] = None
    search_field: Union[ModelSearchField, None] = None

    @staticmethod
    def add_cruddals_model_to_request(info, cruddals_model):
        """
        Attaches the CRUDDALS model to the GraphQL request context.

        Parameters:
            info (Any): GraphQL resolve information.
            cruddals_model (Any): The CRUDDALS model instance to attach.
        """
        if info.context is None:

            class Context:
                CruddalsModel = None

            info.context = Context()
        info.context.CruddalsModel = cruddals_model

    def get_function_lists(self, key, extra_pre_post_resolvers):
        """
        Retrieves a list of functions based on the specified key from the resolver configuration.

        Parameters:
            key (str): Key to look up in the resolver configuration.
            extra_pre_post_resolvers (Dict): Dictionary containing additional resolver configurations.

        Returns:
            List[Callable]: A list of functions associated with the specified key.
        """
        functions = extra_pre_post_resolvers.get(key, None)
        if functions is None:
            return []
        if not isinstance(functions, list):
            functions = [functions]
        return functions

    def get_pre_and_post_resolves(self, extra_pre_post_resolvers, name_function: str):
        """
        Retrieves pre and post resolver functions for a specific operation.

        Parameters:
            extra_pre_post_resolvers (Dict): Dictionary containing additional resolver configurations.
            name_function (str): Name of the function to retrieve resolvers for.

        Returns:
            Tuple[List[Callable], List[Callable]]: A tuple containing lists of pre and post resolver functions.
        """
        pre_resolves_model = self.get_function_lists(
            f"pre_{name_function}", extra_pre_post_resolvers
        )
        post_resolves_model = self.get_function_lists(
            f"post_{name_function}", extra_pre_post_resolvers
        )
        return pre_resolves_model, post_resolves_model

    def wrap_resolver_with_pre_post_resolvers(
        self, default_resolver, extra_pre_post_resolvers, name_function
    ):
        """
        Wraps a resolver function with pre and post resolver functions.

        Parameters:
            default_resolver (Callable): The default resolver function to wrap.
            extra_pre_post_resolvers (Dict): Dictionary containing additional resolver configurations.
            name_function (str): Name of the function to wrap resolvers for.

        Returns:
            Callable: The wrapped resolver function.
        """
        pre_resolves, post_resolves = self.get_pre_and_post_resolves(
            extra_pre_post_resolvers, name_function
        )
        default_resolver = self.get_last_element(
            name_function, extra_pre_post_resolvers, default_resolver
        )

        def default_final_resolver_with_pre_and_post(root, info, **kw):
            self.add_cruddals_model_to_request(info, self)
            for pre_resolve in pre_resolves:
                root, info, kw = pre_resolve(root, info, **kw)
            response = default_resolver(root, info, **kw)
            for post_resolve in post_resolves:
                kw["CRUDDALS_RESPONSE"] = (
                    response  # TODa: Check if leave in kw, info, or new argument
                )
                response = post_resolve(root, info, **kw)
            return response

        return self.get_last_element(
            f"override_total_{name_function}",
            extra_pre_post_resolvers,
            default_final_resolver_with_pre_and_post,
        )

    def get_interface_attrs(self, interface, include_meta_attrs=True):
        """
        Retrieves attributes from a Cruddals interface.

        Parameters:
            interface (Type[Any]): The interface to retrieve attributes from.
            include_meta_attrs (bool): Whether to include meta attributes from the interface.

        Returns:
            Dict: A dictionary containing the attributes of the interface.
        """
        if interface is not None:
            attrs_internal_cls_meta = {}
            if getattr(interface, "Meta", None) is not None and include_meta_attrs:
                attrs_internal_cls_meta = graphene_get_props(interface.Meta)
            props_function = delete_keys(graphene_get_props(interface), ["Meta"])
            return {**props_function, **attrs_internal_cls_meta}
        return {}

    def get_interface_meta_attrs(self, interface_type):
        """
        Retrieves meta attributes from a Cruddals interface type.

        Parameters:
            interface_type (Type[Any]): The interface type to retrieve meta attributes from.

        Returns:
            Dict: A dictionary containing the meta attributes of the interface type.
        """
        if interface_type is not None:
            if getattr(interface_type, "Meta", None) is not None:
                props = graphene_get_props(interface_type.Meta)
                fields = props.get(
                    "fields", props.get("only_fields", props.get("only", []))
                )
                exclude = props.get(
                    "exclude", props.get("exclude_fields", props.get("exclude", []))
                )
                assert not (
                    fields and exclude
                ), f"Cannot set both 'fields' and 'exclude' options on Type {self.model_name_in_different_case['pascal_case']}."
                return props
        return {}

    def validate_attrs(self, props, function_name, operation_name, class_name=None):
        """
        Validates the attributes of a function configuration.

        Parameters:
            props (Dict): Properties to validate.
            function_name (str): Name of the function whose properties are being validated.
            operation_name (str): Name of the operation associated with the function.
            class_name (str): Name of the class, defaults to None.

        Raises:
            AssertionError: If invalid configuration is detected.
        """
        class_name = class_name or self.model_name_in_different_case["pascal_case"]
        function_name_without = function_name.replace("override_total_", "")
        model_pre = props.get(f"pre_{function_name_without}")
        model_function = props.get(f"{function_name_without}")
        model_override_function = props.get(f"{function_name}")
        model_post = props.get(f"post_{function_name_without}")
        assert not (
            model_pre and model_override_function
        ), f"Cannot set both 'pre_{function_name_without}' and '{function_name}' options on {operation_name} {class_name}."
        assert not (
            model_function and model_override_function
        ), f"Cannot set both '{function_name_without}' and '{function_name}' options on {operation_name} {class_name}."
        assert not (
            model_post and model_override_function
        ), f"Cannot set both 'post_{function_name_without}' and '{function_name}' options on {operation_name} {class_name}."

    def get_last_element(self, key, obj, default=None) -> Any:
        """
        Retrieves the last element associated with a key from a dictionary, or a default value if the key is not found.

        Parameters:
            key (str): Key to look up in the dictionary.
            obj (Dict): Dictionary to search.
            default (Any): Default value to return if key is not found.

        Returns:
            Any: The last element associated with the key, or the default value.
        """
        if key in obj:
            element = obj[key]
            if isinstance(element, list):
                return element[-1]
            return element
        return default

    def save_pre_post_how_list(self, kwargs):
        """
        Ensures that 'pre' and 'post' attributes in a dictionary are stored as lists.

        Parameters:
            kwargs (Dict): Dictionary containing 'pre' and 'post' attributes.
        """
        for attr, value in kwargs.items():
            if "pre" in attr or "post" in attr:
                if not isinstance(kwargs[attr], list):
                    kwargs[attr] = [value]


class CreateBuilder(BaseCruddals):
    """
    A class that represents a builder for creating GraphQL create fields.

    This class provides methods for validating properties, building create fields,
    and returning the create field object.

    Inherits from BaseCruddals.

    Methods:
        validate_props_create_field: Validates the properties for the create field.
        build_create: Builds a create field for a GraphQL schema.

    """

    def validate_props_create_field(self, props, name=None):
        """
        Validates the properties for the create field.

        Args:
            props (List[str]): The list of properties to validate.
            name (str, optional): The name of the field. Defaults to None.

        """

        self.validate_attrs(props, "override_total_mutate", "Create", name)

    def build_create(
        self,
        resolve: Callable[..., Any],
        extra_arguments: Union[Dict[str, GRAPHENE_TYPE], None] = None,
        **extra_pre_post_resolvers,
    ) -> ModelCreateUpdateField:
        """
        Builds the create field object.

        Args:
            resolve (Callable[..., Any]): The resolver function for the create field.
            extra_arguments (Union[Dict[str, GRAPHENE_TYPE], None], optional): The extra arguments for the create field. Defaults to None.
            **extra_pre_post_resolvers: Additional pre and post resolvers for the create field.

        Returns:
            ModelCreateUpdateField: The create field object.

        """
        extra_arguments = extra_arguments or {}
        name_function = "mutate"
        resolver = self.wrap_resolver_with_pre_post_resolvers(
            resolve, extra_pre_post_resolvers, name_function
        )

        return ModelCreateUpdateField(
            plural_model_name=self.model_name_in_different_case["plural_pascal_case"],
            type_operation="Create",
            model=self.model,
            registry=self.registry,
            resolver=resolver,
            **extra_arguments,
        )


class ReadBuilder(BaseCruddals):
    """
    A class that represents a builder for creating GraphQL read fields.

    Inherits from BaseCruddals.

    Methods:
        validate_props_read_field: Validates the properties of a read field.
        build_read: Builds a read field for a GraphQL schema.
    """

    def validate_props_read_field(self, props, name=None):
        """
        Validates the properties of a read field.

        Args:
            props: The properties to validate.
            name: The name of the field (optional).

        Returns:
            None
        """

        self.validate_attrs(props, "override_total_read", "Read", name)

    def build_read(
        self,
        resolve: Callable[..., Any],
        extra_arguments: Union[Dict[str, GRAPHENE_TYPE], None] = None,
        **extra_pre_post_resolvers,
    ) -> ModelReadField:
        """
        Builds a read field for a GraphQL schema.

        Args:
            resolve: The resolver function for the read field.
            extra_arguments: Extra arguments for the read field (optional).
            **extra_pre_post_resolvers: Extra pre and post resolvers for the read field.

        Returns:
            The built ModelReadField object.
        """

        extra_arguments = extra_arguments or {}
        name_function = "resolve"
        resolver = self.wrap_resolver_with_pre_post_resolvers(
            resolve, extra_pre_post_resolvers, name_function
        )

        return ModelReadField(
            singular_model_name=self.model_name_in_different_case["pascal_case"],
            model=self.model,
            registry=self.registry,
            resolver=resolver,
            **extra_arguments,
        )


class UpdateBuilder(BaseCruddals):
    """
    A class that provides methods to build an update field for a GraphQL schema.

    Inherits from BaseCruddals.
    """

    def validate_props_update_field(self, props, name=None):
        """
        Validates the properties of the update field.

        Args:
            props: The properties to validate.
            name: The name of the field (optional).

        Raises:
            ValidationError: If the properties are invalid.
        """
        self.validate_attrs(props, "override_total_mutate", "Update", name)

    def build_update(
        self,
        resolve: Callable[..., Any],
        extra_arguments: Union[Dict[str, GRAPHENE_TYPE], None] = None,
        **extra_pre_post_resolvers,
    ) -> ModelCreateUpdateField:
        """
        Builds an update field for a GraphQL schema.

        Args:
            resolve: The resolver function for the update field.
            extra_arguments: Extra arguments for the update field (optional).
            **extra_pre_post_resolvers: Extra pre and post resolvers for the update field.

        Returns:
            The created update field.

        """
        extra_arguments = extra_arguments or {}
        name_function = "mutate"
        resolver = self.wrap_resolver_with_pre_post_resolvers(
            resolve, extra_pre_post_resolvers, name_function
        )
        return ModelCreateUpdateField(
            plural_model_name=self.model_name_in_different_case["plural_pascal_case"],
            type_operation="Update",
            model=self.model,
            registry=self.registry,
            resolver=resolver,
            **extra_arguments,
        )


class DeleteBuilder(BaseCruddals):
    """
    A class that builds a delete field for GraphQL mutations.

    This class provides methods to validate properties and build a delete field
    for GraphQL mutations. It inherits from the `BaseCruddals` class.

    Attributes:
        model_as_object_type (ObjectType): The model as an object type.
        model_name_in_different_case (Dict[str, str]): The model name in different cases.

    Methods:
        validate_props_delete_field: Validates the properties of the delete field.
        build_delete: Builds the delete field for GraphQL mutations.

    """

    def validate_props_delete_field(self, props, name=None):
        """
        Validates the properties of the delete field.

        Args:
            props (List[str]): The properties to validate.
            name (str, optional): The name of the field. Defaults to None.

        """

        self.validate_attrs(props, "override_total_delete", "Delete", name)

    def build_delete(
        self,
        resolve: Callable[..., Any],
        extra_arguments: Union[Dict[str, GRAPHENE_TYPE], None] = None,
        **extra_pre_post_resolvers,
    ) -> ModelDeleteField:
        """
        Builds the delete field for GraphQL mutations.

        Args:
            resolve (Callable): The resolver function for the delete field.
            extra_arguments (Dict[str, GRAPHENE_TYPE], optional): Extra arguments for the delete field. Defaults to None.
            **extra_pre_post_resolvers: Additional pre and post resolvers for the delete field.

        Returns:
            ModelDeleteField: The built delete field.

        """

        extra_arguments = extra_arguments or {}
        name_function = "mutate"
        resolver = self.wrap_resolver_with_pre_post_resolvers(
            resolve, extra_pre_post_resolvers, name_function
        )
        return ModelDeleteField(
            plural_model_name=self.model_name_in_different_case["plural_pascal_case"],
            model=self.model,
            registry=self.registry,
            resolver=resolver,
            **extra_arguments,
        )


class DeactivateBuilder(BaseCruddals):
    """
    A builder class for creating a ModelDeactivateField object.

    This class provides methods for validating properties and building a ModelDeactivateField object
    with the necessary arguments and resolver.

    Args:
        BaseCruddals: The base class for the DeactivateBuilder.

    Attributes:
        model_as_object_type (ObjectType): The model object type.
        model_name_in_different_case (Dict[str, str]): The model name in different cases.

    Methods:
        validate_props_deactivate_field: Validates the properties for the deactivate field.
        build_deactivate: Builds a ModelDeactivateField object with the specified arguments and resolver.
    """

    def validate_props_deactivate_field(self, props, name=None):
        """
        Validates the properties for the deactivate field.

        Args:
            props (List[str]): The list of properties to validate.
            name (str, optional): The name of the field being validated.

        Returns:
            None
        """
        self.validate_attrs(props, "override_total_deactivate", "Deactivate", name)

    def build_deactivate(
        self,
        resolve: Callable[..., Any],
        field_for_activate_deactivate: Union[str, None] = None,
        extra_arguments: Union[Dict[str, GRAPHENE_TYPE], None] = None,
        **extra_pre_post_resolvers,
    ) -> ModelDeactivateField:
        """
        Builds a ModelDeactivateField object with the specified arguments and resolver.

        Args:
            resolve (Callable): The resolver function for the deactivate field.
            extra_arguments (Dict[str, GRAPHENE_TYPE], optional): Extra arguments for the deactivate field.
            **extra_pre_post_resolvers: Additional pre and post resolvers.

        Returns:
            ModelDeactivateField: The built ModelDeactivateField object.
        """
        extra_arguments = extra_arguments or {}
        name_function = "mutate"
        resolver = self.wrap_resolver_with_pre_post_resolvers(
            resolve, extra_pre_post_resolvers, name_function
        )
        return ModelDeactivateField(
            plural_model_name=self.model_name_in_different_case["plural_pascal_case"],
            model=self.model,
            registry=self.registry,
            state_controller_field=field_for_activate_deactivate,
            resolver=resolver,
            **extra_arguments,
        )


class ActivateBuilder(BaseCruddals):
    """
    A builder class for creating an ModelActivateField object.

    This class provides methods for validating properties and building an ModelActivateField object
    with the necessary arguments and resolver.

    Args:
        BaseCruddals: The base class for the ActivateBuilder.

    Attributes:
        Inherits attributes from the BaseCruddals class.

    Methods:
        validate_props_activate_field: Validates the properties of the ModelActivateField.
        build_activate: Builds an ModelActivateField object with the specified arguments and resolver.

    """

    def validate_props_activate_field(self, props, name=None):
        """
        Validates the properties of the ModelActivateField.

        Args:
            props (dict): The properties to be validated.
            name (str, optional): The name of the field. Defaults to None.

        Returns:
            None

        """

        self.validate_attrs(props, "override_total_activate", "Activate", name)

    def build_activate(
        self,
        resolve: Callable[..., Any],
        field_for_activate_deactivate: Union[str, None] = None,
        extra_arguments: Union[Dict[str, GRAPHENE_TYPE], None] = None,
        **extra_pre_post_resolvers,
    ) -> ModelActivateField:
        """
        Builds an ModelActivateField object with the specified arguments and resolver.

        Args:
            resolve (Callable): The resolver function for the ModelActivateField.
            extra_arguments (dict, optional): Extra arguments for the ModelActivateField. Defaults to None.
            **extra_pre_post_resolvers: Additional pre and post resolvers for the ModelActivateField.

        Returns:
            ModelActivateField: The built ModelActivateField object.

        """
        extra_arguments = extra_arguments or {}
        name_function = "mutate"
        resolver = self.wrap_resolver_with_pre_post_resolvers(
            resolve, extra_pre_post_resolvers, name_function
        )
        return ModelActivateField(
            plural_model_name=self.model_name_in_different_case["plural_pascal_case"],
            model=self.model,
            registry=self.registry,
            state_controller_field=field_for_activate_deactivate,
            resolver=resolver,
            **extra_arguments,
        )


class ListBuilder(BaseCruddals):
    """
    A class that builds a list field for GraphQL queries.

    Inherits from BaseCruddals.
    """

    def validate_props_list_field(self, props, name=None):
        """
        Validates the properties of a list field.

        Args:
            props: The properties of the list field.
            name: The name of the list field (optional).
        """
        self.validate_attrs(props, "override_total_list", "List", name)

    def build_list(
        self,
        resolve: Callable[..., Any],
        extra_arguments=None,
        **extra_pre_post_resolvers,
    ) -> ModelListField:
        """
        Builds a list field for GraphQL queries.

        Args:
            resolve: The resolver function for the list field.
            extra_arguments: Extra arguments for the list field (optional).
            **extra_pre_post_resolvers: Extra pre and post resolvers for the list field.

        Returns:
            The built list field.
        """
        extra_arguments = extra_arguments or {}
        name_function = "resolve"
        resolver = self.wrap_resolver_with_pre_post_resolvers(
            resolve, extra_pre_post_resolvers, name_function
        )
        return ModelListField(
            plural_model_name=self.model_name_in_different_case["plural_pascal_case"],
            model=self.model,
            registry=self.registry,
            resolver=resolver,
            **extra_arguments,
        )


class SearchBuilder(BaseCruddals):
    """
    A class that builds search functionality for a GraphQL API.

    Inherits from BaseCruddals.
    """

    def validate_props_search_field(self, props, name=None):
        self.validate_attrs(props, "override_total_search", "Search", name)

    def build_search(
        self,
        resolve: Callable[..., Any],
        extra_arguments: Union[Dict[str, GRAPHENE_TYPE], None] = None,
        **extra_pre_post_resolvers,
    ) -> ModelSearchField:
        """
        Builds a search field for a GraphQL API.

        Args:
            resolve: A callable that resolves the search field.
            modify_where_argument: An argument to modify the 'where' argument of the search field.
            modify_order_by_argument: An argument to modify the 'order_by' argument of the search field.
            modify_pagination_config_argument: An argument to modify the pagination configuration of the search field.
            extra_arguments: Extra arguments to include in the search field.
            **extra_pre_post_resolvers: Extra pre and post resolvers to include in the search field.

        Returns:
            A ModelSearchField object representing the search field.

        """
        extra_arguments = extra_arguments or {}
        name_function = "resolve"
        resolver = self.wrap_resolver_with_pre_post_resolvers(
            resolve, extra_pre_post_resolvers, name_function
        )
        return ModelSearchField(
            plural_model_name=self.model_name_in_different_case["plural_pascal_case"],
            model=self.model,
            registry=self.registry,
            resolver=resolver,
            **extra_arguments,
        )


class BuilderCruddalsModel(
    CreateBuilder,
    ReadBuilder,
    UpdateBuilder,
    DeleteBuilder,
    DeactivateBuilder,
    ActivateBuilder,
    ListBuilder,
    SearchBuilder,
):
    """
    A class that represents a builder for creating CRUD operations for a specific model.

    Args:
        config (CruddalsBuilderConfig): The configuration object for the builder.

    Attributes:
        model: The model associated with the builder.
        pascal_case_name: The name of the model in PascalCase.
        plural_pascal_case_name: The plural name of the model in PascalCase.
        prefix: The prefix to be added to the model name.
        suffix: The suffix to be added to the model name.
        model_name_in_different_case: The name of the model in a different case.
        registry: The registry for the model.
        model_as_object_type: The model represented as a GraphQL object type.
        model_as_paginated_object_type: The model represented as a paginated GraphQL object type.
        model_as_input_object_type: The model represented as a GraphQL input object type.
        model_as_filter_input_object_type: The model represented as a GraphQL filter input object type.
        model_as_order_by_input_object_type: The model represented as a GraphQL order by input object type.
        read_field: The read operation field.
        list_field: The list operation field.
        search_field: The search operation field.
        create_field: The create operation field.
        update_field: The update operation field.
        activate_field: The activate operation field.
        deactivate_field: The deactivate operation field.
        delete_field: The delete operation field.
    """

    def __init__(self, config: CruddalsBuilderConfig) -> None:
        """
        Initializes a new instance of the BuilderCruddalsModel class.

        Args:
            config (CruddalsBuilderConfig): The configuration object for the builder.
        """
        attrs_for_child = [
            "model",
            "pascal_case_name",
            "plural_pascal_case_name",
            "prefix",
            "suffix",
            "model_name_in_different_case",
            "registry",
            "model_as_object_type",
            "model_as_paginated_object_type",
            "model_as_input_object_type",
            "model_as_filter_input_object_type",
            "model_as_order_by_input_object_type",
            "read_field",
            "list_field",
            "search_field",
            "create_field",
            "update_field",
            "activate_field",
            "deactivate_field",
            "delete_field",
        ]
        [setattr(self, attr, None) for attr in attrs_for_child]

        if not config.registry:
            self.registry = get_global_registry(f"{config.prefix}{config.suffix}")
        else:
            self.registry = config.registry

        if not config.plural_pascal_case_name:
            config.plural_pascal_case_name = f"{config.pascal_case_name}s"

        self.model = config.model
        self.prefix = config.prefix
        self.suffix = config.suffix
        self.cruddals_config = config
        self.model_name_in_different_case = get_name_of_model_in_different_case(
            name_model=config.pascal_case_name,
            name_model_plural=config.plural_pascal_case_name,
            prefix=config.prefix,
            suffix=config.suffix,
        )

        assert isinstance(
            config.interfaces, (tuple,)
        ), f"'interfaces' should be tuple received {type(config.interfaces)}"
        assert isinstance(
            config.exclude_interfaces, (tuple,)
        ), f"'exclude_interfaces' should be tuple received {type(config.exclude_interfaces)}"

        dict_of_interface_attr = self.get_dict_of_interface_attr(
            config.interfaces, config.exclude_interfaces
        )

        self.model_as_object_type = self._get_model_object_type(dict_of_interface_attr)
        self.model_as_paginated_object_type = self._get_model_paginated_object_type()
        self.model_as_input_object_type = self._get_model_input_object_type(
            dict_of_interface_attr
        )
        self.model_as_create_input_object_type = (
            self._get_model_create_input_object_type(dict_of_interface_attr)
        )
        self.model_as_update_input_object_type = (
            self._get_model_update_input_object_type(dict_of_interface_attr)
        )
        self.model_as_filter_input_object_type = (
            self._get_model_filter_input_object_type(dict_of_interface_attr)
        )
        self.model_as_order_by_input_object_type = (
            self._get_model_order_by_input_object_type(dict_of_interface_attr)
        )

        self.create_field = self._build_create_field(config, dict_of_interface_attr)
        self.read_field = self._build_read_field(config, dict_of_interface_attr)
        self.update_field = self._build_update_field(config, dict_of_interface_attr)
        self.delete_field = self._build_delete_field(config, dict_of_interface_attr)
        self.deactivate_field = self._build_deactivate_field(
            config, dict_of_interface_attr
        )
        self.activate_field = self._build_activate_field(config, dict_of_interface_attr)
        self.list_field = self._build_list_field(config, dict_of_interface_attr)
        self.search_field = self._build_search_field(config, dict_of_interface_attr)

    def _get_model_object_type(
        self, dict_of_interface_attr
    ) -> Type[graphene.ObjectType]:
        return convert_model_to_model_object_type(
            model=self.model,
            pascal_case_name=self.model_name_in_different_case["pascal_case"],
            registry=self.registry,
            field_converter_function=self.cruddals_config.output_field_converter_function,
            meta_attrs=dict_of_interface_attr.pop(
                MetaCruddalsInterfaceNames.META_OBJECT_TYPE.value, None
            ),
            extra_fields=dict_of_interface_attr.pop(
                CruddalsInterfaceNames.OBJECT_TYPE.value, None
            ),
        )

    def _get_model_paginated_object_type(self) -> Type[graphene.ObjectType]:
        return convert_model_to_model_paginated_object_type(
            model=self.model,
            pascal_case_name=self.model_name_in_different_case["pascal_case"],
            registry=self.registry,
            model_object_type=self.model_as_object_type,
            extra_fields=None,
        )

    def _get_model_input_object_type(
        self, dict_of_interface_attr
    ) -> Type[graphene.InputObjectType]:
        return convert_model_to_model_mutate_input_object_type(
            model=self.model,
            pascal_case_name=self.model_name_in_different_case["pascal_case"],
            registry=self.registry,
            field_converter_function=self.cruddals_config.input_field_converter_function,
            type_mutation=TypesMutationEnum.CREATE_UPDATE.value,
            meta_attrs=dict_of_interface_attr.pop(
                MetaCruddalsInterfaceNames.META_INPUT_OBJECT_TYPE.value, None
            ),
            extra_fields=dict_of_interface_attr.pop(
                CruddalsInterfaceNames.INPUT_OBJECT_TYPE.value, None
            ),
        )

    def _get_model_create_input_object_type(
        self, dict_of_interface_attr
    ) -> Type[graphene.InputObjectType]:
        return convert_model_to_model_mutate_input_object_type(
            model=self.model,
            pascal_case_name=self.model_name_in_different_case["pascal_case"],
            registry=self.registry,
            field_converter_function=self.cruddals_config.create_input_field_converter_function,
            type_mutation=TypesMutationEnum.CREATE.value,
            meta_attrs=dict_of_interface_attr.pop(
                MetaCruddalsInterfaceNames.META_CREATE_INPUT_OBJECT_TYPE.value, None
            ),
            extra_fields=dict_of_interface_attr.pop(
                CruddalsInterfaceNames.CREATE_INPUT_OBJECT_TYPE.value, None
            ),
        )

    def _get_model_update_input_object_type(
        self, dict_of_interface_attr
    ) -> Type[graphene.InputObjectType]:
        return convert_model_to_model_mutate_input_object_type(
            model=self.model,
            pascal_case_name=self.model_name_in_different_case["pascal_case"],
            registry=self.registry,
            field_converter_function=self.cruddals_config.update_input_field_converter_function,
            type_mutation=TypesMutationEnum.UPDATE.value,
            meta_attrs=dict_of_interface_attr.pop(
                MetaCruddalsInterfaceNames.META_UPDATE_INPUT_OBJECT_TYPE.value, None
            ),
            extra_fields=dict_of_interface_attr.pop(
                CruddalsInterfaceNames.UPDATE_INPUT_OBJECT_TYPE.value, None
            ),
        )

    def _get_model_filter_input_object_type(
        self, dict_of_interface_attr
    ) -> Type[graphene.InputObjectType]:
        return convert_model_to_model_filter_input_object_type(
            model=self.model,
            pascal_case_name=self.model_name_in_different_case["pascal_case"],
            registry=self.registry,
            field_converter_function=self.cruddals_config.filter_field_converter_function,
            meta_attrs=dict_of_interface_attr.pop(
                MetaCruddalsInterfaceNames.META_FILTER_INPUT_OBJECT_TYPE.value, None
            ),
            extra_fields=dict_of_interface_attr.pop(
                CruddalsInterfaceNames.FILTER_INPUT_OBJECT_TYPE.value, None
            ),
        )

    def _get_model_order_by_input_object_type(
        self, dict_of_interface_attr
    ) -> Type[graphene.InputObjectType]:
        return convert_model_to_model_order_by_input_object_type(
            model=self.model,
            pascal_case_name=self.model_name_in_different_case["pascal_case"],
            registry=self.registry,
            field_converter_function=self.cruddals_config.order_by_field_converter_function,
            meta_attrs=dict_of_interface_attr.pop(
                MetaCruddalsInterfaceNames.META_ORDER_BY_INPUT_OBJECT_TYPE.value, None
            ),
            extra_fields=dict_of_interface_attr.pop(
                CruddalsInterfaceNames.ORDER_BY_INPUT_OBJECT_TYPE.value, None
            ),
        )

    def _build_create_field(
        self, config: CruddalsBuilderConfig, dict_of_interface_attr
    ) -> ModelCreateUpdateField:
        return self.build_create(
            resolve=config.create_resolver,
            extra_arguments=dict_of_interface_attr.get(
                CruddalsInterfaceNames.CREATE_FIELD.value, {}
            ).pop("extra_arguments", None),
            **dict_of_interface_attr.get(CruddalsInterfaceNames.CREATE_FIELD.value, {}),
        )

    def _build_read_field(
        self, config: CruddalsBuilderConfig, dict_of_interface_attr
    ) -> ModelReadField:
        return self.build_read(
            resolve=config.read_resolver,
            extra_arguments=dict_of_interface_attr.get(
                CruddalsInterfaceNames.READ_FIELD.value, {}
            ).pop("extra_arguments", None),
            **dict_of_interface_attr.get(CruddalsInterfaceNames.READ_FIELD.value, {}),
        )

    def _build_update_field(
        self, config: CruddalsBuilderConfig, dict_of_interface_attr
    ) -> ModelCreateUpdateField:
        return self.build_update(
            resolve=config.update_resolver,
            extra_arguments=dict_of_interface_attr.get(
                CruddalsInterfaceNames.UPDATE_FIELD.value, {}
            ).pop("extra_arguments", None),
            **dict_of_interface_attr.get(CruddalsInterfaceNames.UPDATE_FIELD.value, {}),
        )

    def _build_delete_field(
        self, config: CruddalsBuilderConfig, dict_of_interface_attr
    ) -> ModelDeleteField:
        return self.build_delete(
            resolve=config.delete_resolver,
            extra_arguments=dict_of_interface_attr.get(
                CruddalsInterfaceNames.DELETE_FIELD.value, {}
            ).pop("extra_arguments", None),
            **dict_of_interface_attr.get(CruddalsInterfaceNames.DELETE_FIELD.value, {}),
        )

    def _build_deactivate_field(
        self, config: CruddalsBuilderConfig, dict_of_interface_attr
    ) -> ModelDeactivateField:
        return self.build_deactivate(
            resolve=config.deactivate_resolver,
            extra_arguments=dict_of_interface_attr.get(
                CruddalsInterfaceNames.DEACTIVATE_FIELD.value, {}
            ).pop("extra_arguments", None),
            **dict_of_interface_attr.get(
                CruddalsInterfaceNames.DEACTIVATE_FIELD.value, {}
            ),
        )

    def _build_activate_field(
        self, config: CruddalsBuilderConfig, dict_of_interface_attr
    ) -> ModelActivateField:
        return self.build_activate(
            resolve=config.activate_resolver,
            extra_arguments=dict_of_interface_attr.get(
                CruddalsInterfaceNames.ACTIVATE_FIELD.value, {}
            ).pop("extra_arguments", None),
            **dict_of_interface_attr.get(
                CruddalsInterfaceNames.ACTIVATE_FIELD.value, {}
            ),
        )

    def _build_list_field(
        self, config: CruddalsBuilderConfig, dict_of_interface_attr
    ) -> ModelListField:
        return self.build_list(
            resolve=config.list_resolver,
            extra_arguments=dict_of_interface_attr.get(
                CruddalsInterfaceNames.LIST_FIELD.value, {}
            ).pop("extra_arguments", None),
            **dict_of_interface_attr.get(CruddalsInterfaceNames.LIST_FIELD.value, {}),
        )

    def _build_search_field(
        self, config: CruddalsBuilderConfig, dict_of_interface_attr
    ) -> ModelSearchField:
        return self.build_search(
            resolve=config.search_resolver,
            extra_arguments=dict_of_interface_attr.get(
                CruddalsInterfaceNames.SEARCH_FIELD.value, {}
            ).pop("extra_arguments", None),
            **dict_of_interface_attr.get(CruddalsInterfaceNames.SEARCH_FIELD.value, {}),
        )

    def get_dict_of_interface_attr(
        self,
        interfaces: Union[tuple[Type[Any], ...], None] = None,
        exclude_interfaces: Union[Tuple[str, ...], None] = None,
    ) -> Dict[str, OrderedDict[str, Any]]:
        if not interfaces:
            return {}
        exclude_interfaces = exclude_interfaces or ()
        dict_of_interface_attr = {
            interface_name: OrderedDict() for interface_name in INTERFACES_NAME_CRUDDALS
        }
        for interface in interfaces:
            if interface.__name__ in exclude_interfaces:
                continue
            for interface_field_name in CLASS_INTERFACE_FIELDS_NAMES:
                interface_attrs = OrderedDict()
                current_interface = getattr(interface, interface_field_name, None)
                if current_interface is not None:
                    interface_attrs = self.get_interface_attrs(current_interface)
                    self.save_pre_post_how_list(interface_attrs)
                    validation_func = getattr(
                        self, f"validate_props_{to_snake_case(interface_field_name)}"
                    )
                    validation_func(interface_attrs, interface.__name__)
                dict_of_interface_attr[interface_field_name] = OrderedDict(
                    merge_dict(
                        destination=dict_of_interface_attr[interface_field_name],
                        source=interface_attrs,
                        keep_both=True,
                    )
                )
            for interface_type_name in CLASS_INTERFACE_TYPE_NAMES:
                interface_attrs = {}
                current_interface = getattr(interface, interface_type_name, None)
                if current_interface is not None:
                    interface_attrs = self.get_interface_attrs(current_interface, False)
                    interface_meta_attrs = self.get_interface_meta_attrs(
                        current_interface
                    )
                    dict_of_interface_attr[f"Meta{interface_type_name}"] = OrderedDict(
                        merge_dict(
                            destination=dict_of_interface_attr[
                                f"Meta{interface_type_name}"
                            ],
                            source=interface_meta_attrs,
                            keep_both=True,
                        )
                    )
                dict_of_interface_attr[interface_type_name] = OrderedDict(
                    merge_dict(
                        destination=dict_of_interface_attr[interface_type_name],
                        source=interface_attrs,
                        keep_both=True,
                    )
                )

        return dict_of_interface_attr


class CruddalsModel(SubclassWithMeta):
    """
    A base class for creating CRUD-based GraphQL models using CRUDDALS.

    Attributes:
        Query (Type[graphene.ObjectType]): The query object type.
        Mutation (Union[Type[graphene.ObjectType], None]): The mutation object type.
        schema (graphene.Schema): The GraphQL schema.
        operation_fields_for_queries (Dict[str, Union[graphene.Field, ModelReadField, ModelListField, ModelSearchField]]):
            The operation fields for queries.
        operation_fields_for_mutations (Union[Dict[str, Union[graphene.Field, ModelCreateUpdateField, ModelDeleteField, ModelDeactivateField, ModelActivateField]], None]]):
            The operation fields for mutations.
        meta (BuilderCruddalsModel): The metadata for the CRUDDALS model.

    Methods:
        __init_subclass_with_meta__: Initializes the subclass with metadata.
        _initialize_attributes: Initializes the attributes of the subclass.
        _build_cruddals_model: Builds the CRUDDALS model.
        _build_dict_for_operation_fields: Builds the dictionary for operation fields.
        _build_schema_query_mutation: Builds the schema, query, and mutation.

    """

    Query: Type[graphene.ObjectType]
    Mutation: Union[Type[graphene.ObjectType], None] = None
    schema: graphene.Schema
    operation_fields_for_queries: Dict[
        str, graphene.Field | ModelReadField | ModelListField | ModelSearchField
    ]
    operation_fields_for_mutations: Union[
        Dict[
            str,
            graphene.Field
            | ModelCreateUpdateField
            | ModelDeleteField
            | ModelDeactivateField
            | ModelActivateField,
        ],
        None,
    ] = None
    meta: BuilderCruddalsModel

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        config: Optional[CruddalsBuilderConfig] = None,
        functions: Optional[Tuple[FunctionType, ...]] = None,
        exclude_functions: Optional[Tuple[FunctionType, ...]] = None,
        **kwargs,
    ):
        if config is None:
            raise ValueError("config is required")
        if not functions:
            functions = ()
        if not exclude_functions:
            exclude_functions = ()

        validate_list_func_cruddals(functions, exclude_functions)

        if not config.registry:
            config.registry = get_global_registry(f"{config.prefix}{config.suffix}")

        cls._initialize_attributes()
        cls._build_cruddals_model(config)
        cls._build_dict_for_operation_fields(functions, exclude_functions)
        cls._build_schema_query_mutation()
        config.registry.register_model(
            config.model, TypeRegistryForModelEnum.CRUDDALS.value, cls
        )

        super().__init_subclass_with_meta__(**kwargs)

    @classmethod
    def _initialize_attributes(cls):
        attrs_for_child = [
            "Query",
            "Mutation",
            "schema",
            "operation_fields_for_queries",
            "operation_fields_for_mutations",
            "meta",
        ]
        [setattr(cls, attr, None) for attr in attrs_for_child]

    @classmethod
    def _build_cruddals_model(cls, config):
        cruddals_of_model = BuilderCruddalsModel(config)
        cls.meta = cruddals_of_model

    @classmethod
    def _build_dict_for_operation_fields(cls, functions, exclude_functions):
        functions_type_query = ("read", "list", "search")
        functions_type_mutation = (
            "create",
            "update",
            "activate",
            "deactivate",
            "delete",
        )
        final_functions = (
            functions
            if functions
            else tuple(
                set(functions_type_query + functions_type_mutation)
                - set(exclude_functions)
            )
        )

        if not any(function in functions_type_query for function in final_functions):
            raise ValueError(
                f"Expected at least one of these values {functions_type_query} in 'functions', but got {final_functions}"
            )

        cls.operation_fields_for_queries = {}
        cls.operation_fields_for_mutations = {}

        for function in final_functions:
            key = f"{function}_{cls.meta.model_name_in_different_case['plural_snake_case']}"
            if function == "read":
                key = (
                    f"{function}_{cls.meta.model_name_in_different_case['snake_case']}"
                )
            attr_field: Dict[str, graphene.Field] = {
                key: getattr(cls.meta, f"{function}_field")
            }
            if function in functions_type_query:
                cls.operation_fields_for_queries.update(attr_field)
            elif function in functions_type_mutation:
                cls.operation_fields_for_mutations.update(attr_field)

    @classmethod
    def _build_schema_query_mutation(cls):
        cls.schema, cls.Query, cls.Mutation = get_schema_query_mutation(
            (), cls.operation_fields_for_queries, (), cls.operation_fields_for_mutations
        )
