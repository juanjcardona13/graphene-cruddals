from collections import OrderedDict
from typing import Any, Callable, Dict, List, Literal, Tuple, Type, Union

import graphene
from graphene.types.objecttype import ObjectTypeOptions
from graphene.types.utils import yank_fields_from_attrs
from graphene_cruddals.registry.registry_global import (
    RegistryGlobal,
    get_global_registry,
)
from graphene_cruddals.utils.typing.custom_typing import (
    GRAPHENE_TYPE,
    TypeRegistryForModelEnum,
    TypesMutation,
    TypesMutationEnum,
)

ALL_FIELDS = "__all__"


class PaginationInterface(graphene.Interface):
    """
    Defines a GraphQL Interface for pagination-related attributes.
    """

    total = graphene.Field(graphene.Int)
    page = graphene.Field(graphene.Int)
    pages = graphene.Field(graphene.Int)
    has_next = graphene.Field(graphene.Boolean)
    has_prev = graphene.Field(graphene.Boolean)
    index_start = graphene.Field(graphene.Int)
    index_end = graphene.Field(graphene.Int)


def construct_fields(
    model: Dict[str, Any],
    get_fields_function: Callable[[Dict[str, Any]], Dict[str, Any]],
    field_converter_function: Callable[[str, Any, RegistryGlobal], GRAPHENE_TYPE],
    registry: RegistryGlobal,
    only_fields: Union[List[str], Literal["__all__"], None] = None,
    exclude_fields: Union[List[str], None] = None,
):
    fields = OrderedDict()
    final_fields = get_fields_function(model)
    for name, field in final_fields.items():
        is_not_in_only = (
            only_fields is not None
            and only_fields != ALL_FIELDS
            and name not in only_fields
        )
        is_excluded = exclude_fields is not None and name in exclude_fields
        if is_not_in_only or is_excluded:
            continue

        converted = field_converter_function(name, field, registry)
        # TODO: (Critico) -> debo de guardar en el registry el campo con su conversión
        fields[name] = converted

    return fields


class ModelObjectTypeOptions(ObjectTypeOptions):
    model: Dict[str, Any]
    registry: RegistryGlobal


class ModelObjectType(graphene.ObjectType):
    @classmethod
    def __init_subclass_with_meta__(
        cls,
        interfaces: Tuple[Type[graphene.Interface], ...] = (),
        possible_types: Tuple[Type[graphene.ObjectType], ...] = (),
        default_resolver: Union[Callable, None] = None,
        _meta: Union[ModelObjectTypeOptions, None] = None,
        model: Dict[str, Any] = None,
        field_converter_function: Callable[
            [str, Any, RegistryGlobal], GRAPHENE_TYPE
        ] = lambda x, y, z: graphene.String(),
        get_fields_function: Callable[[Dict[str, Any]], Dict[str, Any]] = lambda x: x,
        registry: Union[RegistryGlobal, None] = None,
        only_fields: Union[List[str], Literal["__all__"], None] = None,
        exclude_fields: Union[List[str], None] = None,
        **options,
    ):
        if not registry:
            registry = get_global_registry()

        converted_fields = construct_fields(
            model,
            get_fields_function,
            field_converter_function,
            registry,
            only_fields,
            exclude_fields,
        )

        model_fields = yank_fields_from_attrs(converted_fields, _as=graphene.Field)

        if not _meta:
            _meta = ModelObjectTypeOptions(cls)

        _meta.model = model
        _meta.registry = registry
        _meta.fields = model_fields

        super().__init_subclass_with_meta__(
            interfaces=interfaces,
            possible_types=possible_types,
            default_resolver=default_resolver,
            _meta=_meta,
            **options,
        )

        registry.register_model(model, "object_type", cls)

    @classmethod
    def get_objects(cls, objects, info):
        return objects


class ModelPaginatedObjectType(graphene.ObjectType):
    @classmethod
    def __init_subclass_with_meta__(
        cls,
        interfaces: Tuple[Type[PaginationInterface], ...] = (PaginationInterface,),
        model_object_type: Union[ModelObjectType, None] = None,
        registry: Union[RegistryGlobal, None] = None,
        _meta: Union[ObjectTypeOptions, None] = None,
        **options,
    ):
        if not interfaces:
            interfaces = (PaginationInterface,)

        if PaginationInterface not in interfaces:
            interfaces = (PaginationInterface,) + interfaces

        if not registry:
            registry = get_global_registry()

        if model_object_type is None:
            raise ValueError("model_object_type is required")

        if not _meta:
            _meta = ObjectTypeOptions(cls)

        _meta.fields = {
            "objects": graphene.Field(
                graphene.List(model_object_type)
            ),  # TODO: Aca debe de ser el ModelListField
        }

        model = model_object_type._meta.model

        super().__init_subclass_with_meta__(
            interfaces=interfaces, _meta=_meta, **options
        )

        registry.register_model(model, "paginated_object_type", cls)


class ModelInputObjectType(graphene.InputObjectType):
    @classmethod
    def __init_subclass_with_meta__(
        cls,
        container=None,
        _meta: Union[ModelObjectTypeOptions, None] = None,
        model: Dict[str, Any] = None,
        type_mutation: TypesMutation = TypesMutationEnum.CREATE_UPDATE.value,
        get_fields_function: Callable[[Dict[str, Any]], Dict[str, Any]] = lambda x: x,
        field_converter_function: Callable[
            [str, Any, RegistryGlobal], GRAPHENE_TYPE
        ] = lambda x, y: graphene.String(),
        registry: Union[RegistryGlobal, None] = None,
        only_fields: Union[List[str], Literal["__all__"], None] = None,
        exclude_fields: Union[List[str], None] = None,
        **options,
    ):
        class_name = cls.__name__

        if type_mutation == TypesMutationEnum.CREATE_UPDATE.value:
            type_of_registry = (
                TypeRegistryForModelEnum.INPUT_OBJECT_TYPE.value
            )  # "input_object_type"
        elif type_mutation == TypesMutationEnum.CREATE.value:
            type_of_registry = (
                TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_CREATE.value
            )  # "input_object_type_for_create"
            if not class_name.startswith("Create"):
                class_name = f"Create{class_name}"
        elif type_mutation == TypesMutationEnum.UPDATE.value:
            type_of_registry = (
                TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_UPDATE.value
            )  # "input_object_type_for_update"
            if not class_name.startswith("Update"):
                class_name = f"Update{class_name}"

        if not registry:
            registry = get_global_registry()

        converted_fields = construct_fields(
            model,
            get_fields_function,
            field_converter_function,
            registry,
            only_fields,
            exclude_fields,
        )

        model_fields = yank_fields_from_attrs(converted_fields, _as=graphene.InputField)

        for name, field in model_fields.items():
            setattr(cls, name, field)

        super().__init_subclass_with_meta__(
            container=container, _meta=_meta, name=class_name, **options
        )

        registry.register_model(model, type_of_registry, cls)


class ModelSearchInputObjectType(graphene.InputObjectType):
    @classmethod
    def __init_subclass_with_meta__(
        cls,
        container=None,
        _meta: Union[ModelObjectTypeOptions, None] = None,
        model: Dict[str, Any] = None,
        get_fields_function: Callable[[Dict[str, Any]], Dict[str, Any]] = lambda x: x,
        field_converter_function: Callable[
            [str, Any, RegistryGlobal], GRAPHENE_TYPE
        ] = lambda x, y: graphene.String(),
        registry: Union[RegistryGlobal, None] = None,
        only_fields: Union[List[str], Literal["__all__"], None] = None,
        exclude_fields: Union[List[str], None] = None,
        **options,
    ):
        if not registry:
            registry = get_global_registry()
        converted_fields = construct_fields(
            model,
            get_fields_function,
            field_converter_function,
            registry,
            only_fields,
            exclude_fields,
        )
        converted_fields.update(
            {
                "AND": graphene.Dynamic(
                    lambda: graphene.InputField(graphene.List(cls))
                ),
                "OR": graphene.Dynamic(lambda: graphene.InputField(graphene.List(cls))),
                "NOT": graphene.Dynamic(lambda: graphene.InputField(cls)),
            }
        )
        model_fields = yank_fields_from_attrs(converted_fields, _as=graphene.InputField)
        for name, field in model_fields.items():
            setattr(cls, name, field)
        super().__init_subclass_with_meta__(container=container, _meta=_meta, **options)
        registry.register_model(model, "input_object_type_for_search", cls)


class ModelOrderByInputObjectType(graphene.InputObjectType):
    @classmethod
    def __init_subclass_with_meta__(
        cls,
        container=None,
        _meta: Union[ModelObjectTypeOptions, None] = None,
        model: Dict[str, Any] = None,
        get_fields_function: Callable[[Dict[str, Any]], Dict[str, Any]] = lambda x: x,
        field_converter_function: Callable[
            [str, Any, RegistryGlobal], GRAPHENE_TYPE
        ] = lambda x, y: graphene.String(),
        registry: Union[RegistryGlobal, None] = None,
        only_fields: Union[List[str], Literal["__all__"], None] = None,
        exclude_fields: Union[List[str], None] = None,
        **options,
    ):
        if not registry:
            registry = get_global_registry()
        converted_fields = construct_fields(
            model,
            get_fields_function,
            field_converter_function,
            registry,
            only_fields,
            exclude_fields,
        )
        model_fields = yank_fields_from_attrs(converted_fields, _as=graphene.InputField)
        for name, field in model_fields.items():
            setattr(cls, name, field)
        super().__init_subclass_with_meta__(container=container, _meta=_meta, **options)
        registry.register_model(model, "input_object_type_for_order_by", cls)
