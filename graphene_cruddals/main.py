from enum import Enum
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, OrderedDict, Tuple, Type, Union

import graphene
from graphene.types.generic import GenericScalar
from graphene.utils.subclass_with_meta import SubclassWithMeta
from graphene.utils.props import props as graphene_get_props
from graphene.utils.str_converters import to_snake_case

from cruddals.converters.main import convert_model_to_filter_input_object_type, convert_model_to_mutate_input_object_type, convert_model_to_object_type, convert_model_to_order_by_input_object_type, convert_model_to_paginated_object_type
from cruddals.utils.typing.custom_typing import GRAPHENE_TYPE, FunctionType, ModifyArgument, NameCaseType, TypesMutationEnum, CruddalsInterfaceNames, MetaCruddalsInterfaceNames, INTERFACES_NAME_CRUDDALS, CLASS_INTERFACE_FIELDS_NAMES, CLASS_INTERFACE_TYPE_NAMES, TypeRegistryForModelEnum
from cruddals.operation_fields.main import ActivateField, CreateUpdateField, DeactivateField, DeleteField, ListField, ReadField, SearchField
from cruddals.registry.registry_global import RegistryGlobal, get_global_registry
from cruddals.utils.main import delete_keys, get_name_of_model_in_different_case, get_schema_query_mutation, merge_dict, validate_list_func_cruddals


""" 
Cuándo usar:
    Método de Instancia (self):
        Cuando necesitas acceder a los datos de una instancia específica de la clase.
        Cuando los métodos operan en los atributos de la instancia.
    Método de Clase (cls):
        Cuando necesitas operar con la clase en lugar de con una instancia específica.
        Cuando necesitas crear una nueva instancia basada en algún tipo de entrada que no sea una instancia de la clase. 
"""

@dataclass
class CruddalsBuilderConfig:
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
        if self.model is None:
            raise ValueError("model is required")
        if not self.pascal_case_name:
            raise ValueError("pascal_case_name is required")
        if not self.plural_pascal_case_name:
            self.plural_pascal_case_name = f"{self.pascal_case_name}s"


class BaseCruddals:
    """
    A base class providing common methods for building resolvers and managing interfaces.

    Attributes:
        model_as_object_type: The GraphQL object type for the model.
        model_as_paginated_object_type: The GraphQL paginated object type for the model.
        model_as_input_object_type: The GraphQL input object type for the model.
        model_as_create_input_object_type: The GraphQL input object type for create operations.
        model_as_update_input_object_type: The GraphQL input object type for update operations.
        model_as_filter_input_object_type: The GraphQL input object type for filtering operations.
        model_as_order_by_input_object_type: The GraphQL input object type for ordering operations.

        read_field: The read field (or also called operation) for the model.
        list_field: The list field (or also called operation) for the model.
        search_field: The search field (or also called operation) for the model.
        create_field: The create field (or also called operation) for the model.
        update_field: The update field (or also called operation) for the model.
        activate_field: The activate field (or also called operation) for the model.
        deactivate_field: The deactivate field (or also called operation) for the model.
        delete_field: The delete field (or also called operation) for the model.

    Methods:
        wrap_resolver_with_pre_post_resolvers: Wrap resolver with pre and post resolvers.
        wrap_resolver_with_pre_post_resolvers: Get the resolver for an operation field.
        get_interface_attrs: Get attributes for an interface.
        get_interface_meta_attrs: Get meta attributes for an interface.
        validate_attrs: Validate attributes for a function.
        get_function_lists: Get lists of functions.
        get_last_element: Get the last element from a list or a default value.
        save_pre_post_how_list: Save pre and post functions as lists.
        get_pre_and_post_resolves: Get pre and post resolves.

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

    create_field: Union[CreateUpdateField, None] = None
    read_field: Union[ReadField, None] = None
    update_field: Union[CreateUpdateField, None] = None
    delete_field: Union[DeleteField, None] = None
    deactivate_field: Union[DeactivateField, None] = None
    activate_field: Union[ActivateField, None] = None
    list_field: Union[ListField, None] = None
    search_field: Union[SearchField, None] = None

    @classmethod
    def get_where_arg(cls, modify_where_argument:Union[ModifyArgument, Dict, None]=None, default_required=False ):
        modify_where_argument = modify_where_argument or {}
        default_values_for_where = {
            "type_": cls.model_as_filter_input_object_type,
            "name": "where",
            "required": default_required,
            "description": "",
        }
        for key in default_values_for_where.keys():
            if key in modify_where_argument:
                default_values_for_where[key] = modify_where_argument[key]
        return {"where": graphene.Argument(default_values_for_where.pop("type_"), **default_values_for_where)}


    @classmethod
    def get_input_arg(cls, modify_input_argument:Union[ModifyArgument, Dict, None]=None):
        modify_input_argument = modify_input_argument or {}
        default_values_for_input = {
            "type_": graphene.List(graphene.NonNull(cls.model_as_input_object_type)),
            "name": "input",
            "required": False,
            "description": "",
        }
        for key in default_values_for_input.keys():
            if key in modify_input_argument:
                default_values_for_input[key] = modify_input_argument[key]
        return {"input": graphene.Argument(default_values_for_input.pop("type_"), **default_values_for_input)}
    

    @classmethod
    def get_order_by_arg(cls, modify_order_by_argument:Union[ModifyArgument, Dict, None]=None):
        modify_order_by_argument = modify_order_by_argument or {}
        default_values_for_order_by = {
            "type_": cls.model_as_order_by_input_object_type,
            "name": "orderBy",
            "required": False,
            "description": "",
        }
        for key in default_values_for_order_by.keys():
            if key in modify_order_by_argument:
                default_values_for_order_by[key] = modify_order_by_argument[key]
        return {"order_by": graphene.Argument(default_values_for_order_by.pop("type_"), **default_values_for_order_by)}


    @classmethod
    def get_pagination_config_arg(cls, modify_pagination_config_argument:Union[ModifyArgument, Dict, None]=None):
        modify_pagination_config_argument = modify_pagination_config_argument or {}
        default_values_for_pagination_config = {
            "type_": PaginationConfigInput,
            "name": "paginationConfig",
            "required": False,
            "description": "",
        }
        for key in default_values_for_pagination_config.keys():
            if key in modify_pagination_config_argument:
                default_values_for_pagination_config[key] = modify_pagination_config_argument[key]
        return {"pagination_config": graphene.Argument(default_values_for_pagination_config.pop("type_"), **default_values_for_pagination_config)}


    @staticmethod
    def add_cruddals_model_to_request(info, cruddals_model):
        if info.context is None:

            class Context:
                CruddalsModel = None

            info.context = Context()
        info.context.CruddalsModel = cruddals_model


    def get_function_lists(self, key, extra_pre_post_resolvers):
        functions = extra_pre_post_resolvers.get(key, None)
        if functions is None:
            return []
        if not isinstance(functions, list):
            functions = [functions]
        return functions


    def get_pre_and_post_resolves(self, extra_pre_post_resolvers, name_function: str):
        pre_resolves_model = self.get_function_lists( f"pre_{name_function}", extra_pre_post_resolvers )
        post_resolves_model = self.get_function_lists( f"post_{name_function}", extra_pre_post_resolvers )
        return pre_resolves_model, post_resolves_model


    def wrap_resolver_with_pre_post_resolvers( self, default_resolver, extra_pre_post_resolvers, name_function):
        pre_resolves, post_resolves = self.get_pre_and_post_resolves( extra_pre_post_resolvers, name_function )
        default_resolver = self.get_last_element( name_function, extra_pre_post_resolvers, default_resolver )

        def default_final_resolver_with_pre_and_post(root, info, **kw):
            self.add_cruddals_model_to_request(info, self)
            for pre_resolve in pre_resolves:
                root, info, kw = pre_resolve(root, info, **kw)
            response = default_resolver(root, info, **kw)
            for post_resolve in post_resolves:
                kw["CRUDDALS_RESPONSE"] = response # TODa: Check if leave in kw, info, or new argument
                response = post_resolve(root, info, **kw)
            return response

        return self.get_last_element(
            f"override_total_{name_function}",
            extra_pre_post_resolvers,
            default_final_resolver_with_pre_and_post,
        )


    def get_interface_attrs(self, interface, include_meta_attrs=True):
        if interface is not None:
            attrs_internal_cls_meta = {}
            if getattr(interface, "Meta", None) is not None and include_meta_attrs:
                attrs_internal_cls_meta = graphene_get_props(interface.Meta)
            props_function = delete_keys(graphene_get_props(interface), ["Meta"])
            return {**props_function, **attrs_internal_cls_meta}
        return {}


    def get_interface_meta_attrs(self, interface_type):
        if interface_type is not None:
            if getattr(interface_type, "Meta", None) is not None:
                props = graphene_get_props(interface_type.Meta)

                fields = props.get("fields", props.get("only_fields", props.get("only", [])))
                exclude = props.get(
                    "exclude", props.get("exclude_fields", props.get("exclude", []))
                )
                assert not (
                    fields and exclude
                ), f"Cannot set both 'fields' and 'exclude' options on Type {self.model_name_in_different_case['pascal_case']}."
                return props
        return {}


    def validate_attrs(self, props, function_name, operation_name, class_name=None):
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
        if key in obj:
            element = obj[key]
            if isinstance(element, list):
                return element[-1]
            return element
        return default


    def save_pre_post_how_list(self, kwargs):
        for attr, value in kwargs.items():
            if "pre" in attr or "post" in attr:
                if not isinstance(kwargs[attr], list):
                    kwargs[attr] = [value]


    def get_state_controller_field(self, kwargs) -> str:
        return self.get_last_element(
            "state_controller_field", kwargs, "is_active"
        )  # TODa: Debo de mirar esto donde lo voy a cuadrar para que sea global


class CreateBuilder(BaseCruddals):
    def validate_props_create_field(self, props, name=None):
        self.validate_attrs(props, "override_total_mutate", "Create", name)
    
    def build_create(self, resolve:Callable[..., Any], modify_input_argument:Union[ModifyArgument, Dict, None]=None, extra_arguments:Union[Dict[str, GRAPHENE_TYPE], None]=None, **extra_pre_post_resolvers) -> CreateUpdateField:
        
        input_arg = self.get_input_arg(modify_input_argument)
        extra_arguments = extra_arguments or {}

        name_function = "mutate"
        resolver = self.wrap_resolver_with_pre_post_resolvers( resolve, extra_pre_post_resolvers, name_function )

        create_field = CreateUpdateField(
            model_object_type=self.model_as_object_type,
            plural_model_name=self.model_name_in_different_case["plural_pascal_case"],
            type_operation="Create",
            args={**input_arg, **extra_arguments},
            resolver=resolver
        )
        return create_field


class ReadBuilder(BaseCruddals):
    def validate_props_read_field(self, props, name=None):
        self.validate_attrs(props, "override_total_read", "Read", name)

    def build_read(self, resolve:Callable[..., Any], modify_where_argument=None, extra_arguments:Union[Dict[str, GRAPHENE_TYPE], None]=None, **extra_pre_post_resolvers) -> ReadField:
        
        where_arg = self.get_where_arg(modify_where_argument, True)
        extra_arguments = extra_arguments or {}

        name_function = "resolve"
        resolver = self.wrap_resolver_with_pre_post_resolvers( resolve, extra_pre_post_resolvers, name_function )

        read_field = ReadField(
            model_object_type=self.model_as_object_type,
            singular_model_name=self.model_name_in_different_case["pascal_case"],
            args={**where_arg, **extra_arguments},
            resolver=resolver
        )
        return read_field


class UpdateBuilder(BaseCruddals):
    def validate_props_update_field(self, props, name=None):
        self.validate_attrs(props, "override_total_mutate", "Update", name)

    def build_update(self, resolve:Callable[..., Any], modify_input_argument:Union[ModifyArgument, Dict, None]=None, extra_arguments:Union[Dict[str, GRAPHENE_TYPE], None]=None, **extra_pre_post_resolvers) -> CreateUpdateField:
        input_arg = self.get_input_arg(modify_input_argument)
        extra_arguments = extra_arguments or {}

        name_function = "mutate"
        resolver = self.wrap_resolver_with_pre_post_resolvers( resolve, extra_pre_post_resolvers, name_function )

        update_field = CreateUpdateField(
            model_object_type=self.model_as_object_type,
            plural_model_name=self.model_name_in_different_case["plural_pascal_case"],
            type_operation="Update",
            args={**input_arg, **extra_arguments},
            resolver=resolver
        )
        return update_field


class DeleteBuilder(BaseCruddals):
    def validate_props_delete_field(self, props, name=None):
        self.validate_attrs(props, "override_total_delete", "Delete", name)

    def build_delete(self, resolve:Callable[..., Any], modify_where_argument=None, extra_arguments:Union[Dict[str, GRAPHENE_TYPE], None]=None, **extra_pre_post_resolvers) -> DeleteField:
        where_arg = self.get_where_arg(modify_where_argument, True)
        extra_arguments = extra_arguments or {}

        name_function = "mutate"
        resolver = self.wrap_resolver_with_pre_post_resolvers( resolve, extra_pre_post_resolvers, name_function )

        delete_field = DeleteField(
            model_object_type=self.model_as_object_type,
            plural_model_name=self.model_name_in_different_case["plural_pascal_case"],
            args={**where_arg, **extra_arguments},
            resolver=resolver
        )
        return delete_field


class DeactivateBuilder(BaseCruddals):
    def validate_props_deactivate_field(self, props, name=None):
        self.validate_attrs(props, "override_total_deactivate", "Deactivate", name)

    def build_deactivate(self, resolve:Callable[..., Any], modify_where_argument=None, extra_arguments:Union[Dict[str, GRAPHENE_TYPE], None]=None, **extra_pre_post_resolvers) -> DeactivateField:
        where_arg = self.get_where_arg(modify_where_argument, True)
        extra_arguments = extra_arguments or {}

        name_function = "mutate"
        resolver = self.wrap_resolver_with_pre_post_resolvers( resolve, extra_pre_post_resolvers, name_function )
        # TODa: field_for_activate_deactivate

        deactivate_field = DeactivateField(
            model_object_type=self.model_as_object_type,
            plural_model_name=self.model_name_in_different_case["plural_pascal_case"],
            args={**where_arg, **extra_arguments},
            resolver=resolver
        )
        return deactivate_field


class ActivateBuilder(BaseCruddals):
    def validate_props_activate_field(self, props, name=None):
        self.validate_attrs(props, "override_total_activate", "Activate", name)

    def build_activate(self, resolve:Callable[..., Any], modify_where_argument=None, extra_arguments:Union[Dict[str, GRAPHENE_TYPE], None]=None, **extra_pre_post_resolvers) -> ActivateField:
        where_arg = self.get_where_arg(modify_where_argument, True)
        extra_arguments = extra_arguments or {}

        name_function = "mutate"
        resolver = self.wrap_resolver_with_pre_post_resolvers( resolve, extra_pre_post_resolvers, name_function )
        # TODa: field_for_activate_deactivate

        activate_field = ActivateField(
            model_object_type=self.model_as_object_type,
            plural_model_name=self.model_name_in_different_case["plural_pascal_case"],
            args={**where_arg, **extra_arguments},
            resolver=resolver
        )
        return activate_field


class ListBuilder(BaseCruddals):
    def validate_props_list_field(self, props, name=None):
        self.validate_attrs(props, "override_total_list", "List", name)

    def build_list(self, resolve:Callable[..., Any], extra_arguments=None, **extra_pre_post_resolvers) -> ListField:
        extra_arguments = extra_arguments or {}

        name_function = "resolve"
        resolver = self.wrap_resolver_with_pre_post_resolvers( resolve, extra_pre_post_resolvers, name_function )

        list_field = ListField(
            model_object_type=self.model_as_object_type,
            plural_model_name=self.model_name_in_different_case["plural_pascal_case"],
            args=extra_arguments,
            resolver=resolver
        )
        return list_field


class IntOrAll(GenericScalar):
    class Meta:
        description = "The page size can be int or 'All'"


class PaginationConfigInput(graphene.InputObjectType):
    page = graphene.InputField(graphene.Int, default_value=1)
    items_per_page = graphene.InputField(IntOrAll, default_value="All")


class SearchBuilder(BaseCruddals):
    def validate_props_search_field(self, props, name=None):
        self.validate_attrs(props, "override_total_search", "Search", name)

    def build_search(self, resolve:Callable[..., Any], modify_where_argument:Union[ModifyArgument, Dict, None]=None, modify_order_by_argument:Union[ModifyArgument, Dict, None]=None, modify_pagination_config_argument:Union[ModifyArgument, Dict, None]=None, extra_arguments:Union[Dict[str, GRAPHENE_TYPE], None]=None, **extra_pre_post_resolvers) -> SearchField:
        where_arg = self.get_where_arg(modify_where_argument, False)
        order_by_arg = self.get_order_by_arg(modify_order_by_argument)
        pagination_config_arg = self.get_pagination_config_arg(modify_pagination_config_argument)
        extra_arguments = extra_arguments or {}

        name_function = "resolve"
        resolver = self.wrap_resolver_with_pre_post_resolvers( resolve, extra_pre_post_resolvers, name_function )

        search_field = SearchField(
            model_as_paginated_object_type=self.model_as_paginated_object_type,
            plural_model_name=self.model_name_in_different_case["plural_pascal_case"],
            args={**where_arg, **order_by_arg, **pagination_config_arg, **extra_arguments},
            resolver=resolver
        )
        return search_field


class BuilderCruddalsModel( CreateBuilder, ReadBuilder, UpdateBuilder, DeleteBuilder, DeactivateBuilder, ActivateBuilder, ListBuilder, SearchBuilder, ):

    def __init__(self, config: CruddalsBuilderConfig) -> None:

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
        self.model_name_in_different_case = get_name_of_model_in_different_case(name_model=config.pascal_case_name, name_model_plural=config.plural_pascal_case_name, prefix=config.prefix, suffix=config.suffix)

        assert isinstance( config.interfaces, (tuple,) ), f"'interfaces' should be tuple received {type(config.interfaces)}"
        assert isinstance( config.exclude_interfaces, (tuple,) ), f"'exclude_interfaces' should be tuple received {type(config.exclude_interfaces)}"

        dict_of_interface_attr = self.get_dict_of_interface_attr( config.interfaces, config.exclude_interfaces )

        self.model_as_object_type = self._get_model_object_type(dict_of_interface_attr)
        self.model_as_paginated_object_type = self._get_model_paginated_object_type()
        self.model_as_input_object_type = self._get_model_input_object_type(dict_of_interface_attr)
        self.model_as_create_input_object_type = self._get_model_create_input_object_type(dict_of_interface_attr)
        self.model_as_update_input_object_type = self._get_model_update_input_object_type(dict_of_interface_attr)
        self.model_as_filter_input_object_type = self._get_model_filter_input_object_type(dict_of_interface_attr)
        self.model_as_order_by_input_object_type = self._get_model_order_by_input_object_type(dict_of_interface_attr)


        create_operation_field = self.build_create(
            resolve=config.create_resolver,
            modify_input_argument=dict_of_interface_attr.get(CruddalsInterfaceNames.CREATE_FIELD.value, {}).pop("modify_input_argument", None),
            extra_arguments=dict_of_interface_attr.get(CruddalsInterfaceNames.CREATE_FIELD.value, {}).pop("extra_arguments", None),
            **dict_of_interface_attr.get(CruddalsInterfaceNames.CREATE_FIELD.value, {})
        )
        setattr(self, "create_field", create_operation_field)

        read_operation_field = self.build_read(
            resolve=config.read_resolver,
            modify_where_argument=dict_of_interface_attr.get(CruddalsInterfaceNames.READ_FIELD.value, {}).pop("modify_where_argument", None),
            extra_arguments=dict_of_interface_attr.get(CruddalsInterfaceNames.READ_FIELD.value, {}).pop("extra_arguments", None),
            **dict_of_interface_attr.get(CruddalsInterfaceNames.READ_FIELD.value, {})
        )
        setattr(self, "read_field", read_operation_field)

        update_operation_field = self.build_update(
            resolve=config.update_resolver,
            modify_input_argument=dict_of_interface_attr.get(CruddalsInterfaceNames.UPDATE_FIELD.value, {}).pop("modify_input_argument", None),
            extra_arguments=dict_of_interface_attr.get(CruddalsInterfaceNames.UPDATE_FIELD.value, {}).pop("extra_arguments", None),
            **dict_of_interface_attr.get(CruddalsInterfaceNames.UPDATE_FIELD.value, {})
        )
        setattr(self, "update_field", update_operation_field)

        delete_operation_field = self.build_delete(
            resolve=config.delete_resolver,
            modify_where_argument=dict_of_interface_attr.get(CruddalsInterfaceNames.DELETE_FIELD.value, {}).pop("modify_where_argument", None),
            extra_arguments=dict_of_interface_attr.get(CruddalsInterfaceNames.DELETE_FIELD.value, {}).pop("extra_arguments", None),
            **dict_of_interface_attr.get(CruddalsInterfaceNames.DELETE_FIELD.value, {})
        )
        setattr(self, "delete_field", delete_operation_field)

        deactivate_operation_field = self.build_deactivate(
            resolve=config.deactivate_resolver,
            modify_where_argument=dict_of_interface_attr.get(CruddalsInterfaceNames.DEACTIVATE_FIELD.value, {}).pop("modify_where_argument", None),
            extra_arguments=dict_of_interface_attr.get(CruddalsInterfaceNames.DEACTIVATE_FIELD.value, {}).pop("extra_arguments", None),
            **dict_of_interface_attr.get(CruddalsInterfaceNames.DEACTIVATE_FIELD.value, {})
        )
        setattr(self, "deactivate_field", deactivate_operation_field)

        activate_operation_field = self.build_activate(
            resolve=config.activate_resolver,
            modify_where_argument=dict_of_interface_attr.get(CruddalsInterfaceNames.ACTIVATE_FIELD.value, {}).pop("modify_where_argument", None),
            extra_arguments=dict_of_interface_attr.get(CruddalsInterfaceNames.ACTIVATE_FIELD.value, {}).pop("extra_arguments", None),
            **dict_of_interface_attr.get(CruddalsInterfaceNames.ACTIVATE_FIELD.value, {})
        )
        setattr(self, "activate_field", activate_operation_field)

        list_operation_field = self.build_list(
            resolve=config.list_resolver,
            modify_input_argument=dict_of_interface_attr.get(CruddalsInterfaceNames.LIST_FIELD.value, {}).pop("modify_input_argument", None),
            extra_arguments=dict_of_interface_attr.get(CruddalsInterfaceNames.LIST_FIELD.value, {}).pop("extra_arguments", None),
            **dict_of_interface_attr.get(CruddalsInterfaceNames.LIST_FIELD.value, {})
        )
        setattr(self, "list_field", list_operation_field)

        search_operation_field = self.build_search(
            resolve=config.search_resolver,
            modify_where_argument=dict_of_interface_attr.get(CruddalsInterfaceNames.SEARCH_FIELD.value, {}).pop("modify_where_argument", None),
            modify_order_by_argument=dict_of_interface_attr.get(CruddalsInterfaceNames.SEARCH_FIELD.value, {}).pop("modify_order_by_argument", None),
            modify_pagination_config_argument=dict_of_interface_attr.get(CruddalsInterfaceNames.SEARCH_FIELD.value, {}).pop("modify_pagination_config_argument", None),
            extra_arguments=dict_of_interface_attr.get(CruddalsInterfaceNames.SEARCH_FIELD.value, {}).pop("extra_arguments", None),
            **dict_of_interface_attr.get(CruddalsInterfaceNames.SEARCH_FIELD.value, {})
        )
        setattr(self, "search_field", search_operation_field)

    @classmethod
    def _get_model_object_type(cls, dict_of_interface_attr) -> Type[graphene.ObjectType]:
        return convert_model_to_object_type(
            model=cls.model,
            pascal_case_name=cls.model_name_in_different_case["pascal_case"],
            registry=cls.registry,
            field_converter_function=cls.cruddals_config.output_field_converter_function,
            meta_attrs=dict_of_interface_attr.pop(MetaCruddalsInterfaceNames.META_OBJECT_TYPE.value, None),
            extra_fields=dict_of_interface_attr.pop(CruddalsInterfaceNames.OBJECT_TYPE.value, None),
        )

    @classmethod
    def _get_model_paginated_object_type(cls) -> Type[graphene.ObjectType]:
        return convert_model_to_paginated_object_type(
            model=cls.model,
            pascal_case_name=cls.model_name_in_different_case["pascal_case"],
            registry=cls.registry,
            model_object_type=cls.model_as_object_type,
            extra_fields=None,
        )

    @classmethod
    def _get_model_input_object_type(cls, dict_of_interface_attr) -> Type[graphene.InputObjectType]:
        return convert_model_to_mutate_input_object_type(
            model=cls.model,
            pascal_case_name=cls.model_name_in_different_case["pascal_case"],
            registry=cls.registry,
            field_converter_function=cls.cruddals_config.input_field_converter_function,
            type_mutation=TypesMutationEnum.CREATE_UPDATE.value,
            meta_attrs=dict_of_interface_attr.pop(MetaCruddalsInterfaceNames.META_INPUT_OBJECT_TYPE.value, None),
            extra_fields=dict_of_interface_attr.pop(CruddalsInterfaceNames.INPUT_OBJECT_TYPE.value, None),
        )

    @classmethod
    def _get_model_create_input_object_type(cls, dict_of_interface_attr) -> Type[graphene.InputObjectType]:
        return convert_model_to_mutate_input_object_type(
            model=cls.model,
            pascal_case_name=cls.model_name_in_different_case["pascal_case"],
            registry=cls.registry,
            field_converter_function=cls.cruddals_config.create_input_field_converter_function,
            type_mutation=TypesMutationEnum.CREATE.value,
            meta_attrs=dict_of_interface_attr.pop(MetaCruddalsInterfaceNames.META_CREATE_INPUT_OBJECT_TYPE.value, None),
            extra_fields=dict_of_interface_attr.pop(CruddalsInterfaceNames.CREATE_INPUT_OBJECT_TYPE.value, None),
        )

    @classmethod
    def _get_model_update_input_object_type(cls, dict_of_interface_attr) -> Type[graphene.InputObjectType]:
        return convert_model_to_mutate_input_object_type(
            model=cls.model,
            pascal_case_name=cls.model_name_in_different_case["pascal_case"],
            registry=cls.registry,
            field_converter_function=cls.cruddals_config.update_input_field_converter_function,
            type_mutation=TypesMutationEnum.UPDATE.value,
            meta_attrs=dict_of_interface_attr.pop(MetaCruddalsInterfaceNames.META_UPDATE_INPUT_OBJECT_TYPE.value, None),
            extra_fields=dict_of_interface_attr.pop(CruddalsInterfaceNames.UPDATE_INPUT_OBJECT_TYPE.value, None),
        )

    @classmethod
    def _get_model_filter_input_object_type(cls, dict_of_interface_attr) -> Type[graphene.InputObjectType]:
        return convert_model_to_filter_input_object_type(
            model=cls.model,
            pascal_case_name=cls.model_name_in_different_case["pascal_case"],
            registry=cls.registry,
            field_converter_function=cls.cruddals_config.filter_field_converter_function,
            meta_attrs=dict_of_interface_attr.pop(MetaCruddalsInterfaceNames.META_FILTER_INPUT_OBJECT_TYPE.value, None),
            extra_fields=dict_of_interface_attr.pop(CruddalsInterfaceNames.FILTER_INPUT_OBJECT_TYPE.value, None),
        )
    
    @classmethod
    def _get_model_order_by_input_object_type(cls, dict_of_interface_attr) -> Type[graphene.InputObjectType]:
        return convert_model_to_order_by_input_object_type(
            model=cls.model,
            pascal_case_name=cls.model_name_in_different_case["pascal_case"],
            registry=cls.registry,
            field_converter_function=cls.cruddals_config.order_by_field_converter_function,
            meta_attrs=dict_of_interface_attr.pop(MetaCruddalsInterfaceNames.META_ORDER_BY_INPUT_OBJECT_TYPE.value, None),
            extra_fields=dict_of_interface_attr.pop(CruddalsInterfaceNames.ORDER_BY_INPUT_OBJECT_TYPE.value, None),
        )
    

    def get_dict_of_interface_attr( self, interfaces: Union[tuple[Type[Any], ...], None] = None, exclude_interfaces: Union[Tuple[str, ...], None] = None ) -> Dict[str, OrderedDict[str, Any]]:
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
    Query: Type[graphene.ObjectType]
    Mutation: Union[Type[graphene.ObjectType], None] = None
    schema: graphene.Schema
    operation_fields_for_queries: Dict[
        str, graphene.Field | ReadField | ListField | SearchField
    ]
    operation_fields_for_mutations: Union[
        Dict[
            str,
            graphene.Field
            | CreateUpdateField
            | DeleteField
            | DeactivateField
            | ActivateField,
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
        cls._build_cruddals_model( config )
        cls._build_dict_for_operation_fields(functions, exclude_functions)
        cls._build_schema_query_mutation()
        config.registry.register_model(config.model, TypeRegistryForModelEnum.CRUDDALS.value, cls)

        super().__init_subclass_with_meta__(**kwargs)

    @classmethod
    def _initialize_attributes(cls):
        """
        Initialize attributes to None for the child class.
        """
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
    def _build_cruddals_model( cls, config ):
        """
        Build the CruddalsModel using BuilderCruddalsModel.

        Args:
            model (Model): The  model for which the schema is to be generated.
            prefix (str): Prefix for the model's schema.
            suffix (str): Suffix for the model's schema.
            interfaces (Tuple[InterfaceStructure, ...]): Additional GraphQL interfaces to include in the schema.
            exclude_interfaces (Tuple[str, ...]): Interfaces to exclude from the schema.
            registry (Union[RegistryGlobal, None]): The registry to use for schema registration.
        """
        cruddals_of_model = BuilderCruddalsModel( config )
        cls.meta = cruddals_of_model

    @classmethod
    def _build_dict_for_operation_fields(cls, functions, exclude_functions):
        """
        Build dictionaries for query and mutation operation fields based on the given functions and exclude_functions..

        Args:
            functions (Tuple[FunctionType, ...]): Functions to include in the schema.
            exclude_functions (Tuple[FunctionType, ...]): Functions to exclude from the schema.
        """
        functions_type_query = ("read", "list", "search")
        functions_type_mutation = ( "create", "update", "activate", "deactivate", "delete", )
        final_functions = ( functions if functions else tuple( set(functions_type_query + functions_type_mutation) - set(exclude_functions) ) )

        if not any( function in functions_type_query for function in final_functions ):
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
            attr_field: Dict[str, graphene.Field] = { key: getattr(cls.meta, f"{function}_field") }
            if function in functions_type_query:
                cls.operation_fields_for_queries.update(attr_field)
            elif function in functions_type_mutation:
                cls.operation_fields_for_mutations.update(attr_field)

    @classmethod
    def _build_schema_query_mutation(cls):
        """
        Build the schema, Query, and Mutation objects.
        """
        cls.schema, cls.Query, cls.Mutation = get_schema_query_mutation(
            (), cls.operation_fields_for_queries, (), cls.operation_fields_for_mutations
        )
