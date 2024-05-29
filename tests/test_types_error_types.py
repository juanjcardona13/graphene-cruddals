import pytest

from graphene import ObjectType
from graphene_cruddals.types.error_types import (
    ErrorCollectionType,
    ErrorType,
)


@pytest.fixture
def sample_error_dict():
    return {
        "char_field_required": [
            "Ensure this value has at most 100 characters (it has 110)."
        ],
        "char_field_with_description": [
            "Ensure this value has at most 100 characters (it has 110)."
        ],
        "duration_field_with_default": ["This field is required."],
        "url_field_with_default": ["Enter a valid URL."],
        "uuid_field_with_default": ["This field is required."],
        "foreign_key_field_required": [
            "Select a valid choice. That choice is not one of the available choices."
        ],
        "foreign_key_field_with_description": [
            "Select a valid choice. That choice is not one of the available choices."
        ],
        "foreign_key_field_without_related_name": [
            "Select a valid choice. That choice is not one of the available choices."
        ],
        "one_to_one_field_required": [
            "Select a valid choice. That choice is not one of the available choices."
        ],
        "one_to_one_field_with_description": [
            "Select a valid choice. That choice is not one of the available choices."
        ],
        "one_to_one_field_without_related_name": [
            "Select a valid choice. That choice is not one of the available choices."
        ],
        "many_to_many_field_required": [
            "Select a valid choice. 1 is not one of the available choices."
        ],
        "many_to_many_field_with_description": [
            "Select a valid choice. 1 is not one of the available choices."
        ],
        "many_to_many_field_without_related_name": [
            "Select a valid choice. 1 is not one of the available choices."
        ],
    }


@pytest.fixture
def error_types_list(sample_error_dict):
    return ErrorType.from_errors(sample_error_dict)


def test_from_errors_creates_list_of_error_types(sample_error_dict):
    error_types = ErrorType.from_errors(sample_error_dict)
    assert isinstance(error_types, list)
    assert all(isinstance(error, ObjectType) for error in error_types)
    for error in error_types:
        assert hasattr(error, "field")
        assert hasattr(error, "messages")
        assert isinstance(error.messages, list)


def test_error_collection_type_from_errors():
    obj_position = "position1"
    sample_errors = ErrorType.from_errors(
        {"first_name": ["Must not be empty", "Must contain only letters"]}
    )
    error_collection = ErrorCollectionType.from_errors(obj_position, sample_errors)

    assert isinstance(error_collection, ObjectType)
    assert error_collection.object_position == obj_position


def test_from_errors_with_empty_dict():
    error_types = ErrorType.from_errors({})
    assert error_types == []


def test_error_collection_type_with_empty_errors():
    error_collection = ErrorCollectionType.from_errors("position1", [])
    assert error_collection.object_position == "position1"
    assert error_collection.errors == []
