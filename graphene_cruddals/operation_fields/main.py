from collections import OrderedDict
from typing import Any, Callable, Dict, Literal, Union

import graphene
from graphene.types.generic import GenericScalar
from graphene_cruddals.registry.registry_global import RegistryGlobal
from graphene_cruddals.utils.error_handling.error_types import ErrorCollectionType
from graphene_cruddals.utils.main import (
    build_class,
    exists_conversion_for_model,
    get_converted_model,
)
from graphene_cruddals.utils.typing.custom_typing import (
    TypeRegistryForModelEnum,
)


def get_object_type_payload(
    model: Dict[str, Any],
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
    output_fields: Dict[str, Union[ModelListField, graphene.Field]] = OrderedDict(
        {
            "objects": ModelListField(
                "objects", model, registry
            ),  # TODa: If I want that the name of the field is the plural_model_name, I need to change the name of the field to plural_model_name, Missing check impact
            "errors_report": graphene.Field(graphene.List(ErrorCollectionType)),
        }
    )
    if include_success:
        output_fields["success"] = graphene.Field(graphene.Boolean)

    return build_class(
        name=name_for_output_type, bases=(graphene.ObjectType,), attrs=output_fields
    )


class IntOrAll(GenericScalar):
    class Meta:
        description = "The page size can be int or 'All'"


class PaginationConfigInput(graphene.InputObjectType):
    page = graphene.InputField(graphene.Int, default_value=1)  # type: ignore
    items_per_page = graphene.InputField(IntOrAll, default_value="All")  # type: ignore


class PaginationInterface(graphene.Interface):
    """
    Defines a GraphQL Interface for pagination-related attributes.
    """

    total = graphene.Field(graphene.Int)
    page = graphene.Field(graphene.Int)
    pages = graphene.Field(graphene.Int)
    has_next = graphene.Field(graphene.Boolean)
    has_prev = graphene.Field(graphene.Boolean)
    index_start_obj = graphene.Field(graphene.Int)
    index_end_obj = graphene.Field(graphene.Int)


class ModelCreateUpdateField(graphene.Field):
    def __init__(
        self,
        plural_model_name: str,
        type_operation: Literal["Create", "Update"],
        model: Dict[str, Any],
        registry: RegistryGlobal,
        resolver: Union[Callable[..., Any], None] = None,
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

        args = {
            "input": graphene.Argument(
                graphene.List(graphene.NonNull(model_as_input_object_type)),
                required=True,
            )
        }

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


class ModelReadField(graphene.Field):
    def __init__(
        self,
        singular_model_name: str,
        model: Dict[str, Any],
        registry: RegistryGlobal,
        resolver: Union[Callable[..., Any], None] = None,
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

        args = {
            "where": graphene.Argument(
                model_as_search_input_object_type, required=True
            ),
        }
        super().__init__(
            model_object_type,
            name=f"read{singular_model_name}",
            args=args,
            resolver=resolver,
            **extra_args,
        )


class ModelDeleteField(graphene.Field):
    def __init__(
        self,
        plural_model_name: str,
        model: Dict[str, Any],
        registry: RegistryGlobal,
        resolver: Union[Callable[..., Any], None] = None,
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

        args = {
            "where": graphene.Argument(
                model_as_search_input_object_type, required=True
            ),
        }

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


class ModelDeactivateField(graphene.Field):
    def __init__(
        self,
        plural_model_name: str,
        model: Dict[str, Any],
        registry: RegistryGlobal,
        state_controller_field: Union[str, None] = None,
        resolver: Union[Callable[..., Any], None] = None,
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

        args = {
            "where": graphene.Argument(
                model_as_search_input_object_type, required=True
            ),
        }

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


class ModelActivateField(graphene.Field):
    def __init__(
        self,
        plural_model_name: str,
        model: Dict[str, Any],
        registry: RegistryGlobal,
        state_controller_field: Union[str, None] = None,
        resolver: Union[Callable[..., Any], None] = None,
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

        args = {
            "where": graphene.Argument(
                model_as_search_input_object_type, required=True
            ),
        }

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


class ModelListField(graphene.Field):
    def __init__(
        self,
        plural_model_name: str,
        model: Dict[str, Any],
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
        # TODa: Check if is List(NonNull(ModelObjectType)) or List(ModelObjectType)
        super().__init__(
            graphene.List(graphene.NonNull(model_object_type)),
            name=name,
            resolver=resolver,
            **extra_args,
        )


class ModelSearchField(graphene.Field):
    def __init__(
        self,
        plural_model_name: str,
        model: Dict[str, Any],
        registry: RegistryGlobal,
        resolver: Union[Callable[..., Any], None] = None,
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

        args = {
            "where": graphene.Argument(model_as_search_input_object_type),
            "order_by": graphene.Argument(
                model_as_order_by_input_object_type, name="orderBy"
            ),
            "pagination_config": graphene.Argument(
                PaginationConfigInput, name="paginationConfig"
            ),
        }

        super().__init__(
            model_as_paginated_object_type,
            name=f"search{plural_model_name}",
            args=args,
            resolver=resolver,
            **extra_args,
        )
