from unittest.mock import Mock

import pytest

import graphene
from graphene import ObjectType
from graphene_cruddals.types.utils import (
    convert_model_to_model_filter_input_object_type,
    convert_model_to_model_object_type,
    convert_model_to_model_order_by_input_object_type,
    convert_model_to_model_paginated_object_type,
)

mock_field_converter_function = Mock(return_value="GRAPHENE_FIELD")
mock_registry = Mock()


model = {"field1": int, "field2": str, "field3": float}
meta_attrs = {"exclude": ["field3"], "only": ["field1"]}


def get_fields(model):
    return model


@pytest.fixture
def setup_registry():
    mock_registry.get_global_registry = Mock(return_value=mock_registry)
    mock_registry.get_registry_for_model = Mock(return_value={})
    return mock_registry


def test_convert_model_to_model_object_type(setup_registry):
    result = convert_model_to_model_object_type(
        model, "Test", setup_registry, get_fields, mock_field_converter_function
    )
    assert isinstance(result, type)
    assert issubclass(result, ObjectType)


def test_convert_model_to_model_paginated_object_type(setup_registry):
    model = {
        "field1": int,
        "field2": str,
        "field3": bool,
    }
    pascal_case_name = "TestModel"
    registry = mock_registry
    model_object_type = convert_model_to_model_object_type(
        model, "TestModel", registry, get_fields, mock_field_converter_function
    )
    extra_fields = {
        "extra_field1": int,
        "extra_field2": str,
    }

    pagination_object_type = convert_model_to_model_paginated_object_type(
        model, pascal_case_name, registry, model_object_type, extra_fields
    )

    assert issubclass(pagination_object_type, ObjectType)
    assert pagination_object_type._meta.name == "TestModelPaginatedType"


def test_convert_model_to_model_filter_input_object_type(setup_registry):
    model = {
        "id": int,
        "name": str,
        "age": int,
    }

    pascal_case_name = "Person"
    registry = mock_registry

    def field_converter_function(field_type, registry):
        if field_type == str:
            return graphene.String()
        else:
            return graphene.Int()

    def get_fields(model):
        return model

    meta_attrs = None
    extra_fields = None

    filter_input_object_type = convert_model_to_model_filter_input_object_type(
        model,
        pascal_case_name,
        registry,
        get_fields,
        field_converter_function,
        meta_attrs,
        extra_fields,
    )

    assert issubclass(filter_input_object_type, graphene.InputObjectType)
    assert filter_input_object_type._meta.name == "FilterPersonInput"

    assert isinstance(filter_input_object_type._meta.fields["id"], graphene.InputField)
    assert isinstance(
        filter_input_object_type._meta.fields["name"], graphene.InputField
    )
    assert isinstance(filter_input_object_type._meta.fields["age"], graphene.InputField)

    assert "AND" in filter_input_object_type._meta.fields
    assert isinstance(filter_input_object_type._meta.fields["AND"], graphene.Dynamic)
    assert "OR" in filter_input_object_type._meta.fields
    assert isinstance(filter_input_object_type._meta.fields["OR"], graphene.Dynamic)
    assert "NOT" in filter_input_object_type._meta.fields
    assert isinstance(filter_input_object_type._meta.fields["NOT"], graphene.Dynamic)


def test_convert_model_to_model_order_by_input_object_type(setup_registry):
    # Define a sample model
    model = {
        "id": int,
        "name": str,
        "age": int,
    }

    # Define other required parameters
    pascal_case_name = "Person"
    registry = mock_registry

    def field_converter_function(field_type, registry):
        if field_type == str:
            return graphene.String()
        else:
            return graphene.Int()

    def get_fields(model):
        return model

    meta_attrs = None
    extra_fields = None

    # Convert the model to an order_by InputObjectType
    order_by_input_object_type = convert_model_to_model_order_by_input_object_type(
        model,
        pascal_case_name,
        registry,
        get_fields,
        field_converter_function,
        meta_attrs,
        extra_fields,
    )

    # Assert that the order_by InputObjectType is correctly constructed
    assert issubclass(order_by_input_object_type, graphene.InputObjectType)
    assert order_by_input_object_type._meta.name == "OrderByPersonInput"

    assert isinstance(
        order_by_input_object_type._meta.fields["id"], graphene.InputField
    )
    assert isinstance(
        order_by_input_object_type._meta.fields["name"], graphene.InputField
    )
    assert isinstance(
        order_by_input_object_type._meta.fields["age"], graphene.InputField
    )


# def test_get_final_exclude_fields_with_exclude():
#     meta_attrs = {"exclude": ["field1", "field2"]}
#     result = get_final_exclude_fields(meta_attrs)
#     assert result == ["field1", "field2"]

# def test_get_final_exclude_fields_with_exclude_fields():
#     meta_attrs = {"exclude_fields": ["field1", "field2"]}
#     result = get_final_exclude_fields(meta_attrs)
#     assert result == ["field1", "field2"]

# def test_get_final_exclude_fields_with_both_exclude_and_exclude_fields():
#     meta_attrs = {"exclude": ["field1", "field2"], "exclude_fields": ["field3", "field4"]}
#     result = get_final_exclude_fields(meta_attrs)
#     assert result == ["field1", "field2"]

# def test_get_final_exclude_fields_with_empty_meta_attrs():
#     result = get_final_exclude_fields()
#     assert result is None

# def test_get_final_exclude_fields_with_empty_exclude():
#     meta_attrs = {"exclude": []}
#     result = get_final_exclude_fields(meta_attrs)
#     assert result == None

# def test_get_final_exclude_fields_with_empty_exclude_fields():
#     meta_attrs = {"exclude_fields": []}
#     result = get_final_exclude_fields(meta_attrs)
#     assert result == None

# def test_get_final_exclude_fields_with_no_exclusions():
#     meta_attrs = {"other_attr": ["value"]}
#     result = get_final_exclude_fields(meta_attrs)
#     assert result is None


# @pytest.mark.parametrize("meta_attrs, expected", [
#     ({'exclude': ['field1', 'field3']}, ['field1', 'field3']),
#     ({'exclude_fields': ['field2']}, ['field2']),
#     (None, None),
#     ({}, None)
# ])
# def test_get_final_exclude_fields(meta_attrs, expected):
#     assert get_final_exclude_fields(meta_attrs) == expected


# @pytest.mark.parametrize("meta_attrs, expected", [
#     ({'only': ['field1']}, ['field1']),
#     ({'fields': ['field1', 'field2']}, ['field1', 'field2']),
#     (None, list(model.keys())),
#     ({'exclude': ['field2']}, ['field1', 'field3'])
# ])
# def test_get_final_fields(meta_attrs, expected):
#     result = get_final_fields(model, meta_attrs)
#     assert result == expected


# def test_get_converted_fields():
#     expected = {'field1': 'GRAPHENE_FIELD', 'field2': 'GRAPHENE_FIELD', 'field3': 'GRAPHENE_FIELD'}
#     assert get_converted_fields(model, mock_field_converter_function) == expected
