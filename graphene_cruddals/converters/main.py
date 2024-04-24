import graphene
from typing import Any, Dict, Literal, OrderedDict, Type, Callable, List, Union, Any, Callable
from cruddals.operation_fields.main import ListField
from cruddals.utils.main import build_class, exists_conversion_for_model, get_converted_model
from cruddals.utils.typing.custom_typing import GRAPHENE_TYPE, MetaAttrs, TypesMutation, TypesMutationEnum, TypeRegistryForModelEnum
from cruddals.registry.registry_global import RegistryGlobal, get_global_registry


class PaginationInterface(graphene.Interface):
    total = graphene.Field(graphene.Int)
    page = graphene.Field(graphene.Int)
    pages = graphene.Field(graphene.Int)
    has_next = graphene.Field(graphene.Boolean)
    has_prev = graphene.Field(graphene.Boolean)
    index_start_obj = graphene.Field(graphene.Int)
    index_end_obj = graphene.Field(graphene.Int)


def get_final_exclude_fields(meta_attrs: Union[OrderedDict[str, Any], MetaAttrs, None] = None,) -> Union[List[str], None]:
    if meta_attrs:
        if meta_attrs.get("exclude"):
            return meta_attrs.get("exclude")
        if meta_attrs.get("exclude_fields"):
            return meta_attrs.get("exclude_fields")
    return None


def get_final_fields(model: Dict[str, Any], meta_attrs: Union[OrderedDict[str, Any], MetaAttrs, None] = None,) -> Union[List[str], Literal["__all__"]]:
    final_fields = list(model.keys())
    final_exclude_fields = get_final_exclude_fields(meta_attrs)
    if meta_attrs:
        if meta_attrs.get("only"):
            final_fields = meta_attrs.get("only")
        elif meta_attrs.get("only_fields"):
            final_fields = meta_attrs.get("only_fields")
        elif meta_attrs.get("fields"):
            final_fields = meta_attrs.get("fields")
        elif final_exclude_fields:
            final_fields = [field for field in final_fields if field not in final_exclude_fields]
    return final_fields or []


def get_converted_fields(
        model: Dict[str, Any], 
        field_converter_function: Callable[[Any], GRAPHENE_TYPE],
        meta_attrs: Union[OrderedDict[str, Any], MetaAttrs, None] = None,
    ) -> Dict[str, GRAPHENE_TYPE]:
    final_fields = get_final_fields(model, meta_attrs)
    converted_fields = {}
    for field_name, field_type in model.items():
        if final_fields == "__all__" or field_name in final_fields:
            converted_fields[field_name] = field_converter_function(field_type)
    return converted_fields


def convert_model_to_object_type(
        model: Dict[str, Any], 
        pascal_case_name:str, 
        registry: RegistryGlobal, 
        field_converter_function: Callable[[Any], GRAPHENE_TYPE],
        meta_attrs: Union[OrderedDict[str, Any], MetaAttrs, None] = None,
        extra_fields:Union[Dict[str, GRAPHENE_TYPE], None] = None
    ) -> Type[graphene.ObjectType]:
    if not model:
        raise ValueError("Model is empty in convert_model_to_object_type")

    if exists_conversion_for_model( model, registry, TypeRegistryForModelEnum.OBJECT_TYPE.value ):
        return get_converted_model( model, registry, TypeRegistryForModelEnum.OBJECT_TYPE.value )
    
    if not pascal_case_name:
        raise ValueError("Name is empty in convert_model_to_object_type")
    if not field_converter_function:
        raise ValueError("Field converter function is empty in convert_model_to_object_type")
    if not callable(field_converter_function):
        raise ValueError("Field converter function is not callable in convert_model_to_object_type")
    
    if not registry:
        registry = get_global_registry()
    if not extra_fields:
        extra_fields = {}

    converted_fields = get_converted_fields(model, field_converter_function, meta_attrs)

    class_model_object_type = build_class(
        name=f"{pascal_case_name}Type", 
        bases=(graphene.ObjectType,), 
        attrs={**converted_fields, **extra_fields}
    )

    registry.register_model(model, TypeRegistryForModelEnum.OBJECT_TYPE.value, class_model_object_type)

    return class_model_object_type
    

def convert_model_to_paginated_object_type(
        model: Dict[str, Any],
        pascal_case_name:str,
        registry: RegistryGlobal,
        model_object_type: Type[graphene.ObjectType],
        extra_fields:Union[Dict[str, GRAPHENE_TYPE], None] = None
    ) -> Type[graphene.ObjectType]:
    if not model:
        raise ValueError("Model is empty in convert_model_to_paginated_object_type")

    if exists_conversion_for_model( model, registry, TypeRegistryForModelEnum.PAGINATED_OBJECT_TYPE.value ):
        return get_converted_model( model, registry, TypeRegistryForModelEnum.PAGINATED_OBJECT_TYPE.value )

    if not pascal_case_name:
        raise ValueError("Name is empty in convert_model_to_paginated_object_type")
    if not model_object_type:
        raise ValueError("Model object type is empty in convert_model_to_paginated_object_type")
    if not registry:
        registry = get_global_registry()
    if extra_fields is None:
        extra_fields = {}

    class_meta_paginated_type = build_class(
        name="Meta",
        attrs={
            "interfaces": (PaginationInterface,),
            "name": f"{pascal_case_name}PaginatedType",
        }
    )
    class_model_paginated_object_type = build_class(
        name=f"{pascal_case_name}PaginatedType",
        bases=(graphene.ObjectType,),
        attrs={
            "Meta": class_meta_paginated_type,
            "objects": ListField(model_object_type, "objects"),
            **extra_fields
        }
    )
    
    registry.register_model(model, TypeRegistryForModelEnum.PAGINATED_OBJECT_TYPE.value, class_model_paginated_object_type)

    return class_model_paginated_object_type


def convert_model_to_mutate_input_object_type(
        model: Dict[str, Any],
        pascal_case_name:str,
        registry: RegistryGlobal,
        field_converter_function: Callable[[Any], GRAPHENE_TYPE],
        type_mutation: TypesMutation = TypesMutationEnum.CREATE_UPDATE.value,
        meta_attrs: Union[OrderedDict[str, Any], MetaAttrs, None] = None,
        extra_fields:Union[Dict[str, GRAPHENE_TYPE], None] = None
    ) -> Type[graphene.InputObjectType]:
    if not pascal_case_name:
        raise ValueError("Name is empty in convert_model_to_mutate_input_object_type")
    
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
        raise ValueError("Model is empty in convert_model_to_mutate_input_object_type")

    if exists_conversion_for_model( model, registry, type_of_registry ):
        return get_converted_model( model, registry, type_of_registry )
    
    if not field_converter_function:
        raise ValueError("Field converter function is empty in convert_model_to_mutate_input_object_type")
    if not callable(field_converter_function):
        raise ValueError("Field converter function is not callable in convert_model_to_mutate_input_object_type")
    
    if not registry:
        registry = get_global_registry()
    if not extra_fields:
        extra_fields = {}

    converted_fields = get_converted_fields(model, field_converter_function, meta_attrs)

    class_model_input_object_type = build_class(
        name=name_input_object_type, 
        bases=(graphene.InputObjectType,), 
        attrs={**converted_fields, **extra_fields}
    )

    registry.register_model(model, type_of_registry, class_model_input_object_type)

    return class_model_input_object_type


def convert_model_to_filter_input_object_type(
        model: Dict[str, Any],
        pascal_case_name:str,
        registry: RegistryGlobal,
        field_converter_function: Callable[[Any], GRAPHENE_TYPE],
        meta_attrs: Union[OrderedDict[str, Any], MetaAttrs, None] = None,
        extra_fields:Union[Dict[str, GRAPHENE_TYPE], None] = None
    ) -> Type[graphene.InputObjectType]:
    if not model:
        raise ValueError("Model is empty in convert_model_to_filter_input_object_type")

    if not pascal_case_name:
        raise ValueError("Name is empty in convert_model_to_filter_input_object_type")
    
    if exists_conversion_for_model( model, registry, TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_SEARCH.value ):
        return get_converted_model( model, registry, TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_SEARCH.value )
    
    if not field_converter_function:
        raise ValueError("Field converter function is empty in convert_model_to_filter_input_object_type")
    if not callable(field_converter_function):
        raise ValueError("Field converter function is not callable in convert_model_to_filter_input_object_type")
    
    if not registry:
        registry = get_global_registry()
    if not extra_fields:
        extra_fields = {}

    converted_fields = get_converted_fields(model, field_converter_function, meta_attrs)

    converted_fields.update(
        {
            "AND": graphene.Dynamic(
                lambda: graphene.InputField(
                    graphene.List(
                        convert_model_to_filter_input_object_type(
                            model, pascal_case_name, registry, field_converter_function
                        )
                    )
                )
            ),
            "OR": graphene.Dynamic(
                lambda: graphene.InputField(
                    graphene.List(
                        convert_model_to_filter_input_object_type(
                            model, pascal_case_name, registry, field_converter_function
                        )
                    )
                )
            ),
            "NOT": graphene.Dynamic(
                lambda: graphene.InputField(
                    convert_model_to_filter_input_object_type(
                        model, pascal_case_name, registry, field_converter_function
                    )
                )
            ),
        }
    )

    class_model_filter_input_object_type = build_class(
        name=f"Filter{pascal_case_name}Input", 
        bases=(graphene.InputObjectType,), 
        attrs={**converted_fields, **extra_fields}
    )

    registry.register_model(model, TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_SEARCH.value, class_model_filter_input_object_type)

    return class_model_filter_input_object_type


def convert_model_to_order_by_input_object_type(
        model: Dict[str, Any],
        pascal_case_name:str,
        registry: RegistryGlobal,
        field_converter_function: Callable[[Any], GRAPHENE_TYPE],
        meta_attrs: Union[OrderedDict[str, Any], MetaAttrs, None] = None,
        extra_fields:Union[Dict[str, GRAPHENE_TYPE], None] = None
    ) -> Type[graphene.InputObjectType]:
    if not model:
        raise ValueError("Model is empty in convert_model_to_order_by_input_object_type")

    if not pascal_case_name:
        raise ValueError("Name is empty in convert_model_to_order_by_input_object_type")

    if exists_conversion_for_model( model, registry, TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_ORDER_BY.value ):
        return get_converted_model( model, registry, TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_ORDER_BY.value )
    
    if not field_converter_function:
        raise ValueError("Field converter function is empty in convert_model_to_order_by_input_object_type")
    if not callable(field_converter_function):
        raise ValueError("Field converter function is not callable in convert_model_to_order_by_input_object_type")
    
    if not registry:
        registry = get_global_registry()
    if not extra_fields:
        extra_fields = {}

    converted_fields = get_converted_fields(model, field_converter_function, meta_attrs)

    class_model_order_by_input_object_type = build_class(
        name=f"OrderBy{pascal_case_name}Input", 
        bases=(graphene.InputObjectType,), 
        attrs={**converted_fields, **extra_fields}
    )

    registry.register_model(model, TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_ORDER_BY.value, class_model_order_by_input_object_type)

    return class_model_order_by_input_object_type

