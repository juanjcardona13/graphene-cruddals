from typing import Dict, List
import graphene
from graphene_cruddals.utils.main import camelize

class ErrorType(graphene.ObjectType):
    """
    Represents an error type with a field and a list of error messages.
    """

    field = graphene.String(required=True)
    messages = graphene.List(graphene.NonNull(graphene.String), required=True)

    @classmethod
    def from_errors(cls, errors: Dict[str, List[str]]) -> List["ErrorType"]:
        """
        Converts a dictionary of errors into a list of ErrorType instances.

        Args:
            errors (dict): A dictionary containing field-error message pairs.

        Returns:
            list: A list of ErrorType instances representing the errors.
        """
        data: Dict[str, List[str]] = camelize(errors) # type: ignore
        return [cls(field=key, messages=value) for key, value in data.items()]


class ErrorCollectionType(graphene.ObjectType):
    """
    Represents a collection of errors associated with an object.

    Attributes:
        object_position (str): The position of the object.
        errors (List[ErrorType]): A list of ErrorType objects representing the errors.

    Methods:
        from_errors(cls, object_position, errors): Creates an instance of ErrorCollectionType from the given object position and errors.
    """
    object_position = graphene.String()
    errors = graphene.List(ErrorType)

    @classmethod
    def from_errors(cls, object_position:str, errors:List[ErrorType]) -> "ErrorCollectionType":
        """
        Creates an instance of ErrorCollectionType from the given object position and errors.

        Args:
            object_position (str): The position of the object.
            errors (List[ErrorType]): A list of ErrorType objects representing the errors.

        Returns:
            ErrorCollectionType: An instance of ErrorCollectionType.
        """
        return cls(object_position=object_position, errors=errors)
