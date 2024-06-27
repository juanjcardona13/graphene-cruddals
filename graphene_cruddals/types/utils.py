from typing import (
    Any,
    Callable,
    Dict,
    OrderedDict,
    Type,
    Union,
)

import graphene
from graphene_cruddals.registry.registry_global import (
    RegistryGlobal,
    get_global_registry,
)
from graphene_cruddals.types.main import (
    ModelInputObjectType,
    ModelObjectType,
    ModelOrderByInputObjectType,
    ModelPaginatedObjectType,
    ModelSearchInputObjectType,
)
from graphene_cruddals.utils.main import (
    build_class,
    exists_conversion_for_model,
    get_converted_model,
)
from graphene_cruddals.utils.typing.custom_typing import (
    GRAPHENE_TYPE,
    MetaAttrs,
    TypeRegistryForModelEnum,
    TypesMutation,
    TypesMutationEnum,
)


def get_resolvers(dictionary):
    return {
        k: v
        for k, v in dictionary.items()
        if k.startswith("resolver_") or k.startswith("resolve_")
    }


def convert_model_to_model_object_type(
    model: Type,
    pascal_case_name: str,
    registry: RegistryGlobal,
    get_fields_function: Callable[[Type], Dict[str, Any]],
    field_converter_function: Callable[
        [str, Any, Type[Any], RegistryGlobal], GRAPHENE_TYPE
    ],
    meta_attrs: Union[OrderedDict[str, Any], MetaAttrs, None] = None,
    extra_fields: Union[Dict[str, GRAPHENE_TYPE], None] = None,
) -> Type[ModelObjectType]:
    """
    Converts a model into a GraphQL ObjectType, registering it with a global registry.

    :param model: Dictionary representing the model fields and their types.
    :param pascal_case_name: The name of the resulting ObjectType in PascalCase.
    :param registry: The global registry for managing GraphQL types.
    :param field_converter_function: Function to convert model field types to GraphQL types.
    :param meta_attrs: Metadata attributes which may contain field specifications.
    :param extra_fields: Additional fields to include in the ObjectType.
    :return: The constructed ObjectType.
    """
    if not model:
        raise ValueError("Model is empty in convert_model_to_model_object_type")
    if not registry:
        registry = get_global_registry()
    if exists_conversion_for_model(
        model, registry, TypeRegistryForModelEnum.OBJECT_TYPE.value
    ):
        return get_converted_model(
            model, registry, TypeRegistryForModelEnum.OBJECT_TYPE.value
        )
    if not pascal_case_name:
        raise ValueError("Name is empty in convert_model_to_model_object_type")
    if not field_converter_function:
        raise ValueError(
            "Field converter function is empty in convert_model_to_model_object_type"
        )
    if not callable(field_converter_function):
        raise ValueError(
            "Field converter function is not callable in convert_model_to_model_object_type"
        )
    if not extra_fields:
        extra_fields = {}
    if not meta_attrs:
        meta_attrs = {"only_fields": "__all__", "exclude_fields": []}

    class_meta_type = build_class(
        name="Meta",
        attrs={
            "model": model,
            "get_fields_function": get_fields_function,
            "field_converter_function": field_converter_function,
            "registry": registry,
            "extra_fields": extra_fields,
            **meta_attrs,
        },
    )
    class_model_object_type = build_class(
        name=f"{pascal_case_name}Type",
        bases=(ModelObjectType,),
        attrs={
            "Meta": class_meta_type,
            **extra_fields,
        },
    )
    return class_model_object_type


def convert_model_to_model_paginated_object_type(
    model: Type,
    pascal_case_name: str,
    registry: RegistryGlobal,
    model_object_type: Type[graphene.ObjectType],
    extra_fields: Union[Dict[str, GRAPHENE_TYPE], None] = None,
) -> Type[ModelPaginatedObjectType]:
    """
    Converts a model into a paginated GraphQL ObjectType, extending an existing ObjectType.

    :param model: Dictionary representing the model fields and their types.
    :param pascal_case_name: The name of the resulting ObjectType in PascalCase.
    :param registry: The global registry for managing GraphQL types.
    :param model_object_type: The base ObjectType to extend for pagination.
    :param extra_fields: Additional fields to include in the paginated ObjectType.
    :return: The constructed paginated ObjectType.
    """
    if not model:
        raise ValueError(
            "Model is empty in convert_model_to_model_paginated_object_type"
        )
    if not registry:
        registry = get_global_registry()
    if exists_conversion_for_model(
        model, registry, TypeRegistryForModelEnum.PAGINATED_OBJECT_TYPE.value
    ):
        return get_converted_model(
            model, registry, TypeRegistryForModelEnum.PAGINATED_OBJECT_TYPE.value
        )
    if not pascal_case_name:
        raise ValueError(
            "Pascal case name is empty in convert_model_to_model_paginated_object_type"
        )
    if not model_object_type:
        raise ValueError(
            "Model object type is empty in convert_model_to_model_paginated_object_type"
        )
    if not extra_fields:
        extra_fields = {}

    class_meta_paginated_type = build_class(
        name="Meta",
        attrs={
            "model_object_type": model_object_type,
            "registry": registry,
            "name": f"{pascal_case_name}PaginatedType",
        },
    )
    class_model_paginated_object_type = build_class(
        name=f"{pascal_case_name}PaginatedType",
        bases=(ModelPaginatedObjectType,),
        attrs={
            "Meta": class_meta_paginated_type,
            **extra_fields,
        },
    )
    return class_model_paginated_object_type


def convert_model_to_model_mutate_input_object_type(
    model: Type,
    pascal_case_name: str,
    registry: RegistryGlobal,
    get_fields_function: Callable[[Type], Dict[str, Any]],
    field_converter_function: Callable[
        [str, Any, Type[Any], RegistryGlobal], GRAPHENE_TYPE
    ],
    type_mutation: TypesMutation = TypesMutationEnum.CREATE_UPDATE.value,
    meta_attrs: Union[OrderedDict[str, Any], MetaAttrs, None] = None,
    extra_fields: Union[Dict[str, GRAPHENE_TYPE], None] = None,
) -> Type[ModelInputObjectType]:
    """
    Converts a model into a GraphQL InputObjectType for mutation purposes, based on the specified mutation type.

    :param model: Dictionary representing the model fields and their types.
    :param pascal_case_name: The name of the resulting InputObjectType in PascalCase.
    :param registry: The global registry for managing GraphQL types.
    :param field_converter_function: Function to convert model field types to GraphQL types.
    :param type_mutation: The type of mutation (create, update, or both) for which the InputObjectType is intended.
    :param meta_attrs: Metadata attributes which may contain field specifications.
    :param extra_fields: Additional fields to include in the InputObjectType.
    :return: The constructed InputObjectType.
    """
    if not registry:
        registry = get_global_registry()
    if not pascal_case_name:
        raise ValueError(
            "Pascal case name is empty in convert_model_to_model_mutate_input_object_type"
        )
    if type_mutation == "create_update":
        type_of_registry = (
            TypeRegistryForModelEnum.INPUT_OBJECT_TYPE.value
        )  # "input_object_type"
        name_input_object_type = f"{pascal_case_name}Input"
    elif type_mutation == "create":
        type_of_registry = (
            TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_CREATE.value
        )  # "input_object_type_for_create"
        name_input_object_type = f"Create{pascal_case_name}Input"
    elif type_mutation == "update":
        type_of_registry = (
            TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_UPDATE.value
        )  # "input_object_type_for_update"
        name_input_object_type = f"Update{pascal_case_name}Input"
    if not model:
        raise ValueError(
            "Model is empty in convert_model_to_model_mutate_input_object_type"
        )
    if exists_conversion_for_model(model, registry, type_of_registry):
        return get_converted_model(model, registry, type_of_registry)
    if not field_converter_function:
        raise ValueError(
            "Field converter function is empty in convert_model_to_model_mutate_input_object_type"
        )
    if not callable(field_converter_function):
        raise ValueError(
            "Field converter function is not callable in convert_model_to_model_mutate_input_object_type"
        )
    if not extra_fields:
        extra_fields = {}
    if not meta_attrs:
        meta_attrs = {"only_fields": "__all__", "exclude_fields": []}

    class_meta_input_type = build_class(
        name="Meta",
        attrs={
            "model": model,
            "get_fields_function": get_fields_function,
            "field_converter_function": field_converter_function,
            "type_mutation": type_mutation,
            "registry": registry,
            "extra_fields": extra_fields,
            **meta_attrs,
        },
    )
    class_model_input_object_type = build_class(
        name=name_input_object_type,
        bases=(ModelInputObjectType,),
        attrs={
            "Meta": class_meta_input_type,
            **extra_fields,
        },
    )
    return class_model_input_object_type


def convert_model_to_model_filter_input_object_type(
    model: Type,
    pascal_case_name: str,
    registry: RegistryGlobal,
    get_fields_function: Callable[[Type], Dict[str, Any]],
    field_converter_function: Callable[
        [str, Any, Type[Any], RegistryGlobal], GRAPHENE_TYPE
    ],
    meta_attrs: Union[OrderedDict[str, Any], MetaAttrs, None] = None,
    extra_fields: Union[Dict[str, GRAPHENE_TYPE], None] = None,
) -> Type[ModelSearchInputObjectType]:
    """
    Converts a model into a GraphQL InputObjectType for filtering purposes, extending the capabilities for complex queries.

    :param model: Dictionary representing the model fields and their types.
    :param pascal_case_name: The name of the resulting InputObjectType in PascalCase.
    :param registry: The global registry for managing GraphQL types.
    :param field_converter_function: Function to convert model field types to GraphQL types.
    :param meta_attrs: Metadata attributes which may contain field specifications.
    :param extra_fields: Additional fields to include in the InputObjectType.
    :return: The constructed filter InputObjectType.
    """
    if not registry:
        registry = get_global_registry()
    if not model:
        raise ValueError(
            "Model is empty in convert_model_to_model_filter_input_object_type"
        )
    if not pascal_case_name:
        raise ValueError(
            "Name is empty in convert_model_to_model_filter_input_object_type"
        )
    if exists_conversion_for_model(
        model, registry, TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_SEARCH.value
    ):
        return get_converted_model(
            model, registry, TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_SEARCH.value
        )
    if not field_converter_function:
        raise ValueError(
            "Field converter function is empty in convert_model_to_model_filter_input_object_type"
        )
    if not callable(field_converter_function):
        raise ValueError(
            "Field converter function is not callable in convert_model_to_model_filter_input_object_type"
        )
    if not extra_fields:
        extra_fields = {}
    if not meta_attrs:
        meta_attrs = {"only_fields": "__all__", "exclude_fields": []}

    class_meta_search_type = build_class(
        name="Meta",
        attrs={
            "model": model,
            "get_fields_function": get_fields_function,
            "field_converter_function": field_converter_function,
            "registry": registry,
            "extra_fields": extra_fields,
            **meta_attrs,
        },
    )
    class_model_filter_input_object_type = build_class(
        name=f"Filter{pascal_case_name}Input",
        bases=(ModelSearchInputObjectType,),
        attrs={
            "Meta": class_meta_search_type,
            **extra_fields,
        },
    )
    return class_model_filter_input_object_type


def convert_model_to_model_order_by_input_object_type(
    model: Type,
    pascal_case_name: str,
    registry: RegistryGlobal,
    get_fields_function: Callable[[Type], Dict[str, Any]],
    field_converter_function: Callable[
        [str, Any, Type[Any], RegistryGlobal], GRAPHENE_TYPE
    ],
    meta_attrs: Union[OrderedDict[str, Any], MetaAttrs, None] = None,
    extra_fields: Union[Dict[str, GRAPHENE_TYPE], None] = None,
) -> Type[ModelOrderByInputObjectType]:
    """
    Converts a model into a GraphQL InputObjectType for specifying order by criteria.

    :param model: Dictionary representing the model fields and their types.
    :param pascal_case_name: The name of the resulting InputObjectType in PascalCase.
    :param registry: The global registry for managing GraphQL types.
    :param field_converter_function: Function to convert model field types to GraphQL types.
    :param meta_attrs: Metadata attributes which may contain field specifications.
    :param extra_fields: Additional fields to include in the InputObjectType.
    :return: The constructed order by InputObjectType.
    """
    if not registry:
        registry = get_global_registry()
    if not model:
        raise ValueError(
            "Model is empty in convert_model_to_model_order_by_input_object_type"
        )
    if not pascal_case_name:
        raise ValueError(
            "Name is empty in convert_model_to_model_order_by_input_object_type"
        )
    if exists_conversion_for_model(
        model, registry, TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_ORDER_BY.value
    ):
        return get_converted_model(
            model,
            registry,
            TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_ORDER_BY.value,
        )
    if not field_converter_function:
        raise ValueError(
            "Field converter function is empty in convert_model_to_model_order_by_input_object_type"
        )
    if not callable(field_converter_function):
        raise ValueError(
            "Field converter function is not callable in convert_model_to_model_order_by_input_object_type"
        )
    if not extra_fields:
        extra_fields = {}
    if not meta_attrs:
        meta_attrs = {"only_fields": "__all__", "exclude_fields": []}

    class_meta_order_by_type = build_class(
        name="Meta",
        attrs={
            "model": model,
            "get_fields_function": get_fields_function,
            "field_converter_function": field_converter_function,
            "registry": registry,
            "extra_fields": extra_fields,
            **meta_attrs,
        },
    )
    class_model_order_by_input_object_type = build_class(
        name=f"OrderBy{pascal_case_name}Input",
        bases=(ModelOrderByInputObjectType,),
        attrs={
            "Meta": class_meta_order_by_type,
            **extra_fields,
        },
    )
    return class_model_order_by_input_object_type
