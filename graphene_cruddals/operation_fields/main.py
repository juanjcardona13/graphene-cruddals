import graphene
from graphene.types.generic import GenericScalar
from typing import Dict, Literal, Type, Union
from collections import OrderedDict
from graphene_cruddals.utils.error_handling.error_types import ErrorCollectionType
from graphene_cruddals.utils.main import build_class


def get_object_type_payload(model_object_type: Type[graphene.ObjectType], name_for_output_type: str, plural_model_name: str, include_success=False):
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
    output_fields: Dict[str, Union[ListField, graphene.Field]] = OrderedDict(
        {
            "objects": ListField(model_object_type, "objects"),  # TODa: If I want that the name of the field is the plural_model_name, I need to change the name of the field to plural_model_name, Missing check impact
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
    page = graphene.InputField(graphene.Int, default_value=1)
    items_per_page = graphene.InputField(IntOrAll, default_value="All")


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


class CreateUpdateField(graphene.Field):
    def __init__(self, model_object_type: Type[graphene.ObjectType], plural_model_name:str, type_operation:Literal["Create", "Update"], args=None, resolver=None, **extra_args):
        

        payload_type = get_object_type_payload( 
            model_object_type=model_object_type,
            name_for_output_type=f"{type_operation}{plural_model_name}Payload",
            plural_model_name=plural_model_name 
        )

        super().__init__(payload_type, name=f"{type_operation.lower()}{plural_model_name}", args=args, resolver=resolver, **extra_args)


class ReadField(graphene.Field):
    def __init__(self, model_object_type:Type[graphene.ObjectType], singular_model_name:str, args=None, resolver=None, **extra_args):
        super().__init__(model_object_type, name=f"read{singular_model_name}", args=args, resolver=resolver, **extra_args)


class DeleteField(graphene.Field):
    def __init__(self, model_object_type:Type[graphene.ObjectType], plural_model_name:str, args=None, resolver=None, **extra_args):

        payload_type = get_object_type_payload(
            model_object_type=model_object_type,
            plural_model_name=plural_model_name,
            name_for_output_type=f"Delete{plural_model_name}Payload",
            include_success=True,
        )

        super().__init__(payload_type, name=f"delete{plural_model_name}", args=args, resolver=resolver, **extra_args)


class DeactivateField(graphene.Field):
    def __init__(self, model_object_type:Type[graphene.ObjectType], plural_model_name:str, args=None, resolver=None, **extra_args):

        payload_type = get_object_type_payload(
            model_object_type=model_object_type, 
            plural_model_name=plural_model_name,
            name_for_output_type=f"Deactivate{plural_model_name}Payload"
        )

        super().__init__(payload_type, name=f"deactivate{plural_model_name}", args=args, resolver=resolver, **extra_args)


class ActivateField(graphene.Field):
    def __init__(self, model_object_type:Type[graphene.ObjectType], plural_model_name:str, args=None, resolver=None, **extra_args):

        payload_type = get_object_type_payload(
            model_object_type=model_object_type, 
            plural_model_name=plural_model_name,
            name_for_output_type=f"Activate{plural_model_name}Payload"
        )

        super().__init__(payload_type, name=f"activate{plural_model_name}", args=args, resolver=resolver, **extra_args)


class ListField(graphene.Field):
    def __init__(self, model_object_type:Type[graphene.ObjectType], plural_model_name:str, args=None, resolver=None, **extra_args):

        name = f"list{plural_model_name}" if plural_model_name != "objects" else "objects"
        #TODa: Check if is List(NonNull(ModelObjectType)) or List(ModelObjectType)
        super().__init__(graphene.List(graphene.NonNull(model_object_type)), name=name, args=args, resolver=resolver, **extra_args)


class SearchField(graphene.Field):

    def __init__(self, model_as_paginated_object_type, plural_model_name, args=None, resolver=None, **extra_args):
        
        if model_as_paginated_object_type._meta.interfaces is None or PaginationInterface not in model_as_paginated_object_type._meta.interfaces:
            raise ValueError("The model_as_paginated_object_type must implement the PaginationInterface")
        

        super().__init__(model_as_paginated_object_type, name=f"search{plural_model_name}", args=args, resolver=resolver, **extra_args)
