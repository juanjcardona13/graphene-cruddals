import graphene
from typing import Literal, Type
from collections import OrderedDict
from graphene_cruddals.utils.error_handling.error_types import ErrorCollectionType
from graphene_cruddals.utils.main import build_class


def get_object_type_payload( model_object_type: Type[graphene.ObjectType], name_for_output_type:str, plural_model_name:str, include_success=False ):

    output_fields = OrderedDict(
        {
            "objects": ListField(model_object_type, "objects"), # TODa: If I want that the name of the field is the plural_model_name, I need to change the name of the field to plural_model_name, Missing check impact
            "errors_report": graphene.List(ErrorCollectionType),
        }
    )
    if include_success:
        output_fields["success"] = graphene.Boolean()

    return build_class(
        name=name_for_output_type, bases=(graphene.ObjectType,), attrs=output_fields
    )


class CreateUpdateField(graphene.Field):
    def __init__(self, model_object_type: Type[graphene.ObjectType], plural_model_name:str, type_operation:Literal["Create", "Update"], args=None, resolver=None, **extra_args):
        
        if isinstance(model_object_type, graphene.NonNull):
            model_object_type = model_object_type.of_type

        payload_type = get_object_type_payload( model_object_type=model_object_type, name_for_output_type=f"{type_operation}{plural_model_name}Payload", plural_model_name=plural_model_name )

        super().__init__(payload_type, name=f"{type_operation.lower()}{plural_model_name}", args=args, resolver=resolver, **extra_args)


class ReadField(graphene.Field):
    def __init__(self, model_object_type:Type[graphene.ObjectType], singular_model_name:str, args=None, resolver=None, **extra_args):
        if isinstance(model_object_type, graphene.NonNull):
            model_object_type = model_object_type.of_type
        super().__init__(model_object_type, name=f"read{singular_model_name}", args=args, resolver=resolver, **extra_args)


class DeleteField(graphene.Field):
    def __init__(self, model_object_type:Type[graphene.ObjectType], plural_model_name:str, args=None, resolver=None, **extra_args):
        if isinstance(model_object_type, graphene.NonNull):
            model_object_type = model_object_type.of_type

        payload_type = get_object_type_payload(
            model_object_type=model_object_type,
            plural_model_name=plural_model_name,
            name_for_output_type=f"Delete{plural_model_name}Payload",
            include_success=True,
        )

        super().__init__(payload_type, name=f"delete{plural_model_name}", args=args, resolver=resolver, **extra_args)


class DeactivateField(graphene.Field):
    def __init__(self, model_object_type:Type[graphene.ObjectType], plural_model_name:str, args=None, resolver=None, **extra_args):
        if isinstance(model_object_type, graphene.NonNull):
            model_object_type = model_object_type.of_type

        payload_type = get_object_type_payload(
            model_object_type=model_object_type, 
            plural_model_name=plural_model_name,
            name_for_output_type=f"Deactivate{plural_model_name}Payload"
        )

        super().__init__(payload_type, name=f"deactivate{plural_model_name}", args=args, resolver=resolver, **extra_args)


class ActivateField(graphene.Field):
    def __init__(self, model_object_type:Type[graphene.ObjectType], plural_model_name:str, args=None, resolver=None, **extra_args):
        if isinstance(model_object_type, graphene.NonNull):
            model_object_type = model_object_type.of_type

        payload_type = get_object_type_payload(
            model_object_type=model_object_type, 
            plural_model_name=plural_model_name,
            name_for_output_type=f"Activate{plural_model_name}Payload"
        )

        super().__init__(payload_type, name=f"activate{plural_model_name}", args=args, resolver=resolver, **extra_args)


class ListField(graphene.Field):
    def __init__(self, model_object_type:Type[graphene.ObjectType], plural_model_name:str, args=None, resolver=None, **extra_args):
        if isinstance(model_object_type, graphene.NonNull):
            model_object_type = model_object_type.of_type

        name = f"list{plural_model_name}" if plural_model_name != "objects" else "objects"

        super().__init__(graphene.List(graphene.NonNull(model_object_type)), name=name, args=args, resolver=resolver, **extra_args)


class SearchField(graphene.Field):
    def __init__(self, model_as_paginated_object_type, plural_model_name, args=None, resolver=None, **extra_args):
        if isinstance(model_as_paginated_object_type, graphene.NonNull):
            model_as_paginated_object_type = model_as_paginated_object_type.of_type

        super().__init__(model_as_paginated_object_type, name=f"search{plural_model_name}", args=args, resolver=resolver, **extra_args)
