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
    TypeRegistryForField,
    TypeRegistryForFieldEnum,
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
    model: Type,
    get_fields_function: Callable[[Type], Dict[str, Any]],
    field_converter_function: Callable[
        [str, Any, Type[Any], RegistryGlobal], GRAPHENE_TYPE
    ],
    registry: RegistryGlobal,
    only_fields: Union[List[str], Literal["__all__"], None] = None,
    exclude_fields: Union[List[str], None] = None,
    extra_fields: Union[Dict[str, Union[GRAPHENE_TYPE, Any]], None] = None,
    type_of_registry: TypeRegistryForField = TypeRegistryForFieldEnum.OUTPUT.value,
) -> Dict[str, GRAPHENE_TYPE]:
    fields = OrderedDict()
    final_fields = get_fields_function(model)
    if extra_fields:
        final_fields.update(extra_fields)
    for name, field in final_fields.items():
        is_not_in_only = (
            only_fields is not None
            and only_fields != ALL_FIELDS
            and name not in only_fields
        )
        is_excluded = exclude_fields is not None and name in exclude_fields
        if is_not_in_only or is_excluded:
            continue

        if name.startswith("resolve_"):
            continue
        elif isinstance(field, graphene.Scalar):
            fields[name] = field
            # registry.register_field(field, type_of_registry, field) #TODO: Revisar como guardo esta conversion
        else:
            converted = field_converter_function(name, field, model, registry)
            fields[name] = converted
            registry.register_field(field, type_of_registry, converted)

    return fields


def convert_class_to_dict(cls: Type) -> Dict[str, Any]:
    try:
        return cls.__annotations__
    except AttributeError:
        return {
            name: field
            for name, field in cls.__dict__.items()
            if not name.startswith("__") and not callable(field)
        }


class ModelObjectTypeOptions(ObjectTypeOptions):
    model: Type
    registry: RegistryGlobal


class ModelObjectType(graphene.ObjectType):
    @classmethod
    def __init_subclass_with_meta__(
        cls,
        interfaces: Tuple[Type[graphene.Interface], ...] = (),
        possible_types: Tuple[Type[graphene.ObjectType], ...] = (),
        default_resolver: Union[Callable, None] = None,
        _meta: Union[ModelObjectTypeOptions, None] = None,
        model: Type = None,
        field_converter_function: Callable[
            [str, Any, Type[Any], RegistryGlobal], GRAPHENE_TYPE
        ] = lambda w, x, y, z: graphene.String(),
        get_fields_function: Callable[[Type], Dict[str, Any]] = convert_class_to_dict,
        registry: Union[RegistryGlobal, None] = None,
        only_fields: Union[List[str], Literal["__all__"], None] = None,
        exclude_fields: Union[List[str], None] = None,
        extra_fields: Union[Dict[str, Union[GRAPHENE_TYPE, Any]], None] = None,
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
            extra_fields,
            TypeRegistryForFieldEnum.OUTPUT.value,
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
        model: Type = None,
        type_mutation: TypesMutation = TypesMutationEnum.CREATE_UPDATE.value,
        get_fields_function: Callable[[Type], Dict[str, Any]] = convert_class_to_dict,
        field_converter_function: Callable[
            [str, Any, Type[Any], RegistryGlobal], GRAPHENE_TYPE
        ] = lambda w, x, y, z: graphene.String(),
        registry: Union[RegistryGlobal, None] = None,
        only_fields: Union[List[str], Literal["__all__"], None] = None,
        exclude_fields: Union[List[str], None] = None,
        extra_fields: Union[Dict[str, Union[GRAPHENE_TYPE, Any]], None] = None,
        **options,
    ):
        class_name = cls.__name__

        if type_mutation == TypesMutationEnum.CREATE_UPDATE.value:
            type_of_registry = (
                TypeRegistryForModelEnum.INPUT_OBJECT_TYPE.value
            )  # "input_object_type"
            type_of_registry_for_field = (
                TypeRegistryForFieldEnum.INPUT_FOR_CREATE_UPDATE.value
            )
        elif type_mutation == TypesMutationEnum.CREATE.value:
            type_of_registry = (
                TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_CREATE.value
            )  # "input_object_type_for_create"
            type_of_registry_for_field = TypeRegistryForFieldEnum.INPUT_FOR_CREATE.value
            if not class_name.startswith("Create"):
                class_name = f"Create{class_name}"
        elif type_mutation == TypesMutationEnum.UPDATE.value:
            type_of_registry = (
                TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_UPDATE.value
            )  # "input_object_type_for_update"
            type_of_registry_for_field = TypeRegistryForFieldEnum.INPUT_FOR_UPDATE.value
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
            extra_fields,
            type_of_registry_for_field,
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
        model: Type = None,
        get_fields_function: Callable[[Type], Dict[str, Any]] = convert_class_to_dict,
        field_converter_function: Callable[
            [str, Any, Type[Any], RegistryGlobal], GRAPHENE_TYPE
        ] = lambda w, x, y, z: graphene.String(),
        registry: Union[RegistryGlobal, None] = None,
        only_fields: Union[List[str], Literal["__all__"], None] = None,
        exclude_fields: Union[List[str], None] = None,
        extra_fields: Union[Dict[str, Union[GRAPHENE_TYPE, Any]], None] = None,
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
            extra_fields,
            TypeRegistryForFieldEnum.INPUT_FOR_SEARCH.value,
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
        model: Type = None,
        get_fields_function: Callable[[Type], Dict[str, Any]] = convert_class_to_dict,
        field_converter_function: Callable[
            [str, Any, Type[Any], RegistryGlobal], GRAPHENE_TYPE
        ] = lambda w, x, y, z: graphene.String(),
        registry: Union[RegistryGlobal, None] = None,
        only_fields: Union[List[str], Literal["__all__"], None] = None,
        exclude_fields: Union[List[str], None] = None,
        extra_fields: Union[Dict[str, Union[GRAPHENE_TYPE, Any]], None] = None,
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
            extra_fields,
            TypeRegistryForFieldEnum.INPUT_FOR_ORDER_BY.value,
        )
        model_fields = yank_fields_from_attrs(converted_fields, _as=graphene.InputField)
        for name, field in model_fields.items():
            setattr(cls, name, field)
        super().__init_subclass_with_meta__(container=container, _meta=_meta, **options)
        registry.register_model(model, "input_object_type_for_order_by", cls)
