import graphene
from graphene_cruddals.utils.main import camelize

class ErrorType(graphene.ObjectType):
    field = graphene.String(required=True)
    messages = graphene.List(graphene.NonNull(graphene.String), required=True)

    @classmethod
    def from_errors(cls, errors):
        data = camelize(errors)
        return [cls(field=key, messages=value) for key, value in data.items()]


class ErrorCollectionType(graphene.ObjectType):
    object_position = graphene.String()
    errors = graphene.List(ErrorType)

    @classmethod
    def from_errors(cls, object_position, errors):
        return cls(object_position=object_position, errors=errors)
