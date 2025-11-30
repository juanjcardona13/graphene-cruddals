import inspect
from collections import OrderedDict
from typing import Any, Callable, Dict, Literal, Optional, Type, Union

from graphql import Undefined

import graphene
from graphene.types.generic import GenericScalar
from graphene_cruddals.registry.registry_global import RegistryGlobal
from graphene_cruddals.types.error_types import ErrorCollectionType
from graphene_cruddals.utils.main import (
    build_class,
    exists_conversion_for_model,
    get_converted_model,
)
from graphene_cruddals.utils.typing.custom_typing import (
    TypeRegistryForModelEnum,
)

_ARGUMENT_SUPPORTS_DEPRECATION = (
    "deprecation_reason" in inspect.signature(graphene.Argument.__init__).parameters
)


def get_object_type_payload(
    model: Type,
    registry: RegistryGlobal,
    name_for_output_type: str,
    plural_model_name: str,
    include_success=False,
):
    """
    Returns a dynamically generated GraphQL ObjectType class that represents the payload for a specific object type.

    Args:
        model_object_type (Type[graphene.ObjectType]): The object type to be included in the payload.
        name_for_output_type (str): The name for the output type.
        plural_model_name (str): The plural name for the model.
        include_success (bool, optional): Whether to include a success field in the payload. Defaults to False.

    Returns:
        type: The dynamically generated GraphQL ObjectType class representing the payload.
    """
    model_object_type = get_converted_model(
        model, registry, TypeRegistryForModelEnum.OBJECT_TYPE.value
    )
    output_fields: Dict[str, Union[ModelListField, graphene.Field]] = OrderedDict(
        {
            "objects": graphene.Field(graphene.List(model_object_type)),
            "errors_report": graphene.Field(graphene.List(ErrorCollectionType)),
        }
    )
    if include_success:
        output_fields["success"] = graphene.Field(graphene.Boolean)

    return build_class(
        name=name_for_output_type, bases=(graphene.ObjectType,), attrs=output_fields
    )


class CruddalsRelationField:
    """Mark to field for convert field to relation field"""


class IntOrAll(GenericScalar):
    class Meta:
        description = "The page size can be int or 'All'"


class PaginationConfigInput(graphene.InputObjectType):
    page = graphene.InputField(graphene.Int, default_value=1)  # type: ignore
    items_per_page = graphene.InputField(IntOrAll, default_value="All")  # type: ignore


def build_argument_from_modification(
    modify_config: Optional[Dict[str, Any]],
    default_type: Any,
    default_name: str,
    default_required: bool = True,
    default_description: Optional[str] = None,
    default_default_value: Any = Undefined,
    default_deprecation_reason: Optional[str] = None,
) -> Optional[graphene.Argument]:
    """
    Builds a graphene.Argument from a modification configuration.

    Args:
        modify_config: Dictionary with argument modifications (can be None)
        default_type: Default GraphQL type of the argument
        default_name: Default name of the argument
        default_required: Whether the argument is required by default
        default_description: Default description of the argument
        default_default_value: Default value of the argument
        default_deprecation_reason: Default deprecation reason

    Returns:
        Configured graphene.Argument or None if modify_config is None or hidden=True
    """
    if not modify_config:
        kwargs = {
            "type_": default_type,
            "default_value": default_default_value,
            "description": default_description,
            "name": default_name,
            "required": default_required,
        }
        if default_deprecation_reason is not None and _ARGUMENT_SUPPORTS_DEPRECATION:
            kwargs["deprecation_reason"] = default_deprecation_reason
        return graphene.Argument(**kwargs)

    if modify_config.get("hidden", False):
        return None

    kwargs = {
        "type_": modify_config.get("type_", default_type),
        "default_value": modify_config.get("default_value", default_default_value),
        "description": modify_config.get("description", default_description),
        "name": modify_config.get("name", default_name),
        "required": modify_config.get("required", default_required),
    }
    deprecation_reason = modify_config.get(
        "deprecation_reason", default_deprecation_reason
    )
    if deprecation_reason is not None and _ARGUMENT_SUPPORTS_DEPRECATION:
        kwargs["deprecation_reason"] = deprecation_reason
    return graphene.Argument(**kwargs)


class ModelCreateUpdateField(graphene.Field):
    def __init__(
        self,
        plural_model_name: str,
        type_operation: Literal["Create", "Update"],
        model: Type,
        registry: RegistryGlobal,
        resolver: Union[Callable[..., Any], None] = None,
        modify_input_argument: Optional[Dict[str, Any]] = None,
        **extra_args,
    ):
        type_registry = (
            TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_CREATE.value
            if type_operation == "Create"
            else TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_UPDATE.value
        )
        if not exists_conversion_for_model(model, registry, type_registry):
            raise ValueError(
                f"The model does not have a ModelInputObjectType registered for {type_operation.lower()} operation"
            )

        model_as_input_object_type = get_converted_model(model, registry, type_registry)

        args = {}
        default_type = graphene.List(graphene.NonNull(model_as_input_object_type))
        default_name = "input"
        default_required = True

        input_arg = build_argument_from_modification(
            modify_config=modify_input_argument,
            default_type=default_type,
            default_name=default_name,
            default_required=default_required,
        )

        if input_arg:
            args[input_arg.name] = input_arg

        payload_type = get_object_type_payload(
            model=model,
            registry=registry,
            name_for_output_type=f"{type_operation}{plural_model_name}Payload",
            plural_model_name=plural_model_name,
            include_success=False,
        )

        super().__init__(
            payload_type,
            name=f"{type_operation.lower()}{plural_model_name}",
            args=args,
            resolver=resolver,
            **extra_args,
        )

    def wrap_resolve(self, parent_resolver):
        resolver = super().wrap_resolve(parent_resolver)
        if resolver is not None:
            return resolver
        else:
            raise ValueError("resolver is None for ModelCreateUpdateField")


class ModelReadField(graphene.Field):
    def __init__(
        self,
        singular_model_name: str,
        model: Type,
        registry: RegistryGlobal,
        resolver: Union[Callable[..., Any], None] = None,
        modify_where_argument: Optional[Dict[str, Any]] = None,
        **extra_args,
    ):
        if not exists_conversion_for_model(
            model, registry, TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_SEARCH.value
        ):
            raise ValueError(
                "The model does not have a ModelSearchInputObjectType registered and it is required for the read operation"
            )

        model_object_type = get_converted_model(
            model, registry, TypeRegistryForModelEnum.OBJECT_TYPE.value
        )
        model_as_search_input_object_type = get_converted_model(
            model, registry, TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_SEARCH.value
        )

        args = {}
        default_type = model_as_search_input_object_type
        default_name = "where"
        default_required = True

        where_arg = build_argument_from_modification(
            modify_config=modify_where_argument,
            default_type=default_type,
            default_name=default_name,
            default_required=default_required,
        )

        if where_arg:
            args[where_arg.name] = where_arg

        super().__init__(
            model_object_type,
            name=f"read{singular_model_name}",
            args=args,
            resolver=resolver,
            **extra_args,
        )

    def wrap_resolve(self, parent_resolver):
        resolver = super().wrap_resolve(parent_resolver)
        if resolver is not None:
            return resolver
        else:
            raise ValueError("resolver is None for ModelReadField")


class ModelDeleteField(graphene.Field):
    def __init__(
        self,
        plural_model_name: str,
        model: Type,
        registry: RegistryGlobal,
        resolver: Union[Callable[..., Any], None] = None,
        modify_where_argument: Optional[Dict[str, Any]] = None,
        **extra_args,
    ):
        if not exists_conversion_for_model(
            model, registry, TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_SEARCH.value
        ):
            raise ValueError(
                "The model does not have a ModelSearchInputObjectType registered and it is required for the delete operation"
            )

        model_as_search_input_object_type = get_converted_model(
            model, registry, TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_SEARCH.value
        )

        args = {}
        default_type = model_as_search_input_object_type
        default_name = "where"
        default_required = True

        where_arg = build_argument_from_modification(
            modify_config=modify_where_argument,
            default_type=default_type,
            default_name=default_name,
            default_required=default_required,
        )

        if where_arg:
            args[where_arg.name] = where_arg

        payload_type = get_object_type_payload(
            model=model,
            registry=registry,
            plural_model_name=plural_model_name,
            name_for_output_type=f"Delete{plural_model_name}Payload",
            include_success=True,
        )

        super().__init__(
            payload_type,
            name=f"delete{plural_model_name}",
            args=args,
            resolver=resolver,
            **extra_args,
        )

    def wrap_resolve(self, parent_resolver):
        resolver = super().wrap_resolve(parent_resolver)
        if resolver is not None:
            return resolver
        else:
            raise ValueError("resolver is None for ModelDeleteField")


class ModelDeactivateField(graphene.Field):
    def __init__(
        self,
        plural_model_name: str,
        model: Type,
        registry: RegistryGlobal,
        state_controller_field: Union[str, None] = None,
        resolver: Union[Callable[..., Any], None] = None,
        modify_where_argument: Optional[Dict[str, Any]] = None,
        **extra_args,
    ):
        if not exists_conversion_for_model(
            model, registry, TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_SEARCH.value
        ):
            raise ValueError(
                "The model does not have a ModelSearchInputObjectType registered and it is required for the deactivate operation"
            )

        model_as_search_input_object_type = get_converted_model(
            model, registry, TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_SEARCH.value
        )

        args = {}
        default_type = model_as_search_input_object_type
        default_name = "where"
        default_required = True

        where_arg = build_argument_from_modification(
            modify_config=modify_where_argument,
            default_type=default_type,
            default_name=default_name,
            default_required=default_required,
        )

        if where_arg:
            args[where_arg.name] = where_arg

        payload_type = get_object_type_payload(
            model=model,
            registry=registry,
            plural_model_name=plural_model_name,
            name_for_output_type=f"Deactivate{plural_model_name}Payload",
        )

        super().__init__(
            payload_type,
            name=f"deactivate{plural_model_name}",
            args=args,
            resolver=resolver,
            **extra_args,
        )

    def wrap_resolve(self, parent_resolver):
        resolver = super().wrap_resolve(parent_resolver)
        if resolver is not None:
            return resolver
        else:
            raise ValueError("resolver is None for ModelDeactivateField")


class ModelActivateField(graphene.Field):
    def __init__(
        self,
        plural_model_name: str,
        model: Type,
        registry: RegistryGlobal,
        state_controller_field: Union[str, None] = None,
        resolver: Union[Callable[..., Any], None] = None,
        modify_where_argument: Optional[Dict[str, Any]] = None,
        **extra_args,
    ):
        if not exists_conversion_for_model(
            model, registry, TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_SEARCH.value
        ):
            raise ValueError(
                "The model does not have a ModelSearchInputObjectType registered and it is required for the activate operation"
            )

        model_as_search_input_object_type = get_converted_model(
            model, registry, TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_SEARCH.value
        )

        args = {}
        default_type = model_as_search_input_object_type
        default_name = "where"
        default_required = True

        where_arg = build_argument_from_modification(
            modify_config=modify_where_argument,
            default_type=default_type,
            default_name=default_name,
            default_required=default_required,
        )

        if where_arg:
            args[where_arg.name] = where_arg

        payload_type = get_object_type_payload(
            model=model,
            registry=registry,
            plural_model_name=plural_model_name,
            name_for_output_type=f"Activate{plural_model_name}Payload",
        )

        super().__init__(
            payload_type,
            name=f"activate{plural_model_name}",
            args=args,
            resolver=resolver,
            **extra_args,
        )

    def wrap_resolve(self, parent_resolver):
        resolver = super().wrap_resolve(parent_resolver)
        if resolver is not None:
            return resolver
        else:
            raise ValueError("resolver is None for ModelActivateField")


class ModelListField(graphene.Field):
    def __init__(
        self,
        plural_model_name: str,
        model: Type,
        registry: RegistryGlobal,
        resolver: Union[Callable[..., Any], None] = None,
        **extra_args,
    ):
        model_object_type = get_converted_model(
            model, registry, TypeRegistryForModelEnum.OBJECT_TYPE.value
        )
        name = (
            f"list{plural_model_name}" if plural_model_name != "objects" else "objects"
        )
        super().__init__(
            graphene.List(graphene.NonNull(model_object_type)),
            name=name,
            resolver=resolver,
            **extra_args,
        )

    def wrap_resolve(self, parent_resolver):
        resolver = super().wrap_resolve(parent_resolver)
        if resolver is not None and not hasattr(resolver, "func"):
            return resolver
        else:
            raise ValueError("resolver is None for ModelListField")


class ModelSearchField(graphene.Field):
    def __init__(
        self,
        plural_model_name: str,
        model: Type,
        registry: RegistryGlobal,
        resolver: Union[Callable[..., Any], None] = None,
        modify_where_argument: Optional[Dict[str, Any]] = None,
        modify_order_by_argument: Optional[Dict[str, Any]] = None,
        modify_pagination_config_argument: Optional[Dict[str, Any]] = None,
        **extra_args,
    ):
        if not exists_conversion_for_model(
            model, registry, TypeRegistryForModelEnum.PAGINATED_OBJECT_TYPE.value
        ):
            raise ValueError(
                "The model does not have a ModelPaginatedObjectType registered and it is required for the search operation"
            )

        if not exists_conversion_for_model(
            model, registry, TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_SEARCH.value
        ):
            raise ValueError(
                "The model does not have a ModelSearchInputObjectType registered and it is required for the search operation"
            )

        if not exists_conversion_for_model(
            model,
            registry,
            TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_ORDER_BY.value,
        ):
            raise ValueError(
                "The model does not have a ModelOrderByInputObjectType registered and it is required for the search operation"
            )

        model_as_paginated_object_type = get_converted_model(
            model, registry, TypeRegistryForModelEnum.PAGINATED_OBJECT_TYPE.value
        )
        model_as_search_input_object_type = get_converted_model(
            model, registry, TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_SEARCH.value
        )
        model_as_order_by_input_object_type = get_converted_model(
            model,
            registry,
            TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_ORDER_BY.value,
        )

        args = {}

        where_arg = build_argument_from_modification(
            modify_config=modify_where_argument,
            default_type=model_as_search_input_object_type,
            default_name="where",
            default_required=False,
        )
        if where_arg:
            args[where_arg.name] = where_arg

        order_by_arg = build_argument_from_modification(
            modify_config=modify_order_by_argument,
            default_type=model_as_order_by_input_object_type,
            default_name="orderBy",
            default_required=False,
        )
        if order_by_arg:
            args[order_by_arg.name] = order_by_arg

        pagination_arg = build_argument_from_modification(
            modify_config=modify_pagination_config_argument,
            default_type=PaginationConfigInput,
            default_name="paginationConfig",
            default_required=False,
        )
        if pagination_arg:
            args[pagination_arg.name] = pagination_arg

        name = (
            f"search{plural_model_name}"
            if "name" not in extra_args
            else extra_args.pop("name")
        )

        super().__init__(
            model_as_paginated_object_type,
            name=name,
            args=args,
            resolver=resolver,
            **extra_args,
        )

    def wrap_resolve(self, parent_resolver):
        resolver = super().wrap_resolve(parent_resolver)
        if resolver is not None:
            return resolver
        else:
            raise ValueError("resolver is None for ModelSearchField")
