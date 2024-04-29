import pytest

import graphene
from graphene.test import Client
from graphene_cruddals.operation_fields.main import (
    IntOrAll,
    PaginationConfigInput,
)
from graphene_cruddals.registry.registry_global import (
    get_global_registry,
)
from graphene_cruddals.types.main import (
    ModelObjectType,
    ModelPaginatedObjectType,
)
from graphene_cruddals.utils.main import build_class


@pytest.fixture
def registry():
    return get_global_registry()


sample_model = {"id": int, "name": str, "active": bool}


class MockModelObjectType(ModelObjectType):
    class Meta:
        model = sample_model


class MockModelPaginatedObjectType(ModelPaginatedObjectType):
    class Meta:
        model_object_type = MockModelObjectType


@pytest.fixture
def client():
    query = build_class(
        "Query", bases=(graphene.ObjectType,), attrs={"sample": graphene.String()}
    )
    schema = graphene.Schema(
        query=query, types=[MockModelObjectType, MockModelPaginatedObjectType]
    )
    return Client(schema)


# def test_get_object_type_payload_basic(registry):
#     payload_type = get_object_type_payload(
#         model=sample_model,
#         registry=registry,
#         name_for_output_type="MockModelObjectType",
#         plural_model_name="Tests",
#         include_success=False,
#     )
#     assert issubclass(payload_type, graphene.ObjectType)
#     assert "objects" in payload_type._meta.fields
#     assert "errors_report" in payload_type._meta.fields
#     assert isinstance(payload_type._meta.fields["objects"], ModelListField)
#     assert isinstance(payload_type._meta.fields["objects"].type, graphene.List)
#     assert isinstance(
#         payload_type._meta.fields["objects"].type.of_type, graphene.NonNull
#     )
#     # assert payload_type._meta.fields["objects"].type.of_type.of_type == MockModelObjectType

#     assert isinstance(payload_type._meta.fields["errors_report"], graphene.Field)
#     assert isinstance(payload_type._meta.fields["errors_report"].type, graphene.List)
#     assert (
#         payload_type._meta.fields["errors_report"].type.of_type == ErrorCollectionType
#     )
#     assert "success" not in payload_type._meta.fields


# def test_get_object_type_payload_include_success(registry):
#     payload_type = get_object_type_payload(
#         model=sample_model,
#         registry=registry,
#         name_for_output_type="MockModelObjectType",
#         plural_model_name="Tests",
#         include_success=True,
#     )
#     assert "success" in payload_type._meta.fields
#     assert isinstance(payload_type._meta.fields["success"], graphene.Field)
#     assert payload_type._meta.fields["success"].type == graphene.Boolean


def test_pagination_config_input():
    # Create an instance of the PaginationConfigInput class
    pagination_config = PaginationConfigInput(page=2, items_per_page=10)

    # Assert that the page and items_per_page fields are set correctly
    assert pagination_config.kwargs == {"page": 2, "items_per_page": 10}
    assert isinstance(pagination_config.page, graphene.InputField)
    assert pagination_config.page.type == graphene.Int
    assert pagination_config.page.default_value == 1
    assert isinstance(pagination_config.items_per_page, graphene.InputField)
    assert pagination_config.items_per_page.type == IntOrAll
    assert pagination_config.items_per_page.default_value == "All"


def test_pagination_interface_fields(client):
    result = client.execute(
        """
        query {
            __type(name: "PaginationInterface") {
                fields {
                    name
                    type {
                        name
                        kind
                    }
                }
            }
        }
    """
    )

    expected_fields = [
        {"name": "total", "type": {"name": "Int", "kind": "SCALAR"}},
        {"name": "page", "type": {"name": "Int", "kind": "SCALAR"}},
        {"name": "pages", "type": {"name": "Int", "kind": "SCALAR"}},
        {"name": "hasNext", "type": {"name": "Boolean", "kind": "SCALAR"}},
        {"name": "hasPrev", "type": {"name": "Boolean", "kind": "SCALAR"}},
        {"name": "indexStart", "type": {"name": "Int", "kind": "SCALAR"}},
        {"name": "indexEnd", "type": {"name": "Int", "kind": "SCALAR"}},
    ]

    assert result["data"]["__type"]["fields"] == expected_fields


# class TestModelCreateUpdateField:

#     def test_create_update_field_initialization_create(self, registry):
#         field = ModelCreateUpdateField(
#             plural_model_name="Tests",
#             type_operation="Create",
#             model=sample_model,
#             registry=registry,
#         )
#         payload_type = field.type

#         assert isinstance(field, graphene.Field)
#         assert field.args == {}
#         assert field.resolver == None
#         assert field.name == "createTests"

#         assert issubclass(payload_type, graphene.ObjectType) # type: ignore
#         assert "objects" in payload_type._meta.fields
#         assert "errors_report" in payload_type._meta.fields
#         assert isinstance(payload_type._meta.fields["objects"], ModelListField)
#         assert isinstance(payload_type._meta.fields["objects"].type, graphene.List)
#         assert isinstance(payload_type._meta.fields["objects"].type.of_type, graphene.NonNull)
#         assert payload_type._meta.fields["objects"].type.of_type.of_type == MockModelObjectType

#         assert isinstance(payload_type._meta.fields["errors_report"], graphene.Field)
#         assert isinstance(payload_type._meta.fields["errors_report"].type, graphene.List)
#         assert payload_type._meta.fields["errors_report"].type.of_type == ErrorCollectionType
#         assert "success" not in payload_type._meta.fields

#     def test_create_update_field_initialization_update(self, registry):
#         field = ModelCreateUpdateField(
#             plural_model_name="Tests",
#             type_operation="Update",
#             model=sample_model,
#             registry=registry,
#         )
#         payload_type = field.type

#         assert isinstance(field, graphene.Field)
#         assert field.args == {}
#         assert field.resolver == None
#         assert field.name == "updateTests"

#         assert issubclass(payload_type, graphene.ObjectType) # type: ignore
#         assert "objects" in payload_type._meta.fields
#         assert "errors_report" in payload_type._meta.fields
#         assert isinstance(payload_type._meta.fields["objects"], ModelListField)
#         assert isinstance(payload_type._meta.fields["objects"].type, graphene.List)
#         assert isinstance(payload_type._meta.fields["objects"].type.of_type, graphene.NonNull)
#         assert payload_type._meta.fields["objects"].type.of_type.of_type == MockModelObjectType

#         assert isinstance(payload_type._meta.fields["errors_report"], graphene.Field)
#         assert isinstance(payload_type._meta.fields["errors_report"].type, graphene.List)
#         assert payload_type._meta.fields["errors_report"].type.of_type == ErrorCollectionType
#         assert "success" not in payload_type._meta.fields

#     def test_create_update_field_with_args(self, registry):
#         field = ModelCreateUpdateField(
#             plural_model_name="Tests",
#             type_operation="Create",
#             model=sample_model,
#             registry=registry,
#             resolver=lambda root, info, **kwargs: None,
#             **{"test": graphene.String()}
#         )
#         assert field.args == {"test": graphene.Argument(graphene.String)}


# class TestModelReadField:
#     def test_read_field_initialization(self, registry):
#         singular_model_name = "TestModel"
#         resolver = lambda root, info, **kwargs: None
#         extra_args = {"extra_arg": graphene.String()}

#         read_field = ModelReadField(
#             singular_model_name=singular_model_name,
#             model=sample_model,
#             registry=registry,
#             resolver=resolver,
#             **extra_args
#         )

#         assert isinstance(read_field, graphene.Field)
#         assert read_field.type == MockModelObjectType
#         assert read_field.name == f"read{singular_model_name}"
#         assert read_field.args == {"where": graphene.Argument(graphene.ID, required=True), "extra_arg": graphene.Argument(graphene.String)}
#         assert read_field.resolver == resolver


# class TestModelDeleteField:
#     def test_delete_field_initialization(self, registry):
#         plural_model_name = "Tests"
#         resolver = lambda root, info, **kwargs: None
#         extra_args = {"extra_arg": graphene.String()}

#         delete_field = ModelDeleteField(
#             plural_model_name=plural_model_name,
#             model=sample_model,
#             registry=registry,
#             resolver=resolver,
#             **extra_args
#         )
#         payload_type = delete_field.type

#         assert isinstance(delete_field, graphene.Field)
#         assert delete_field.name == f"delete{plural_model_name}"
#         assert delete_field.args == {"where": graphene.Argument(graphene.ID, required=True), "extra_arg": graphene.Argument(graphene.String)}
#         assert delete_field.resolver == resolver

#         assert issubclass(payload_type, graphene.ObjectType) # type: ignore
#         assert "objects" in payload_type._meta.fields
#         assert "errors_report" in payload_type._meta.fields
#         assert isinstance(payload_type._meta.fields["objects"], ModelListField)
#         assert isinstance(payload_type._meta.fields["objects"].type, graphene.List)
#         assert isinstance(payload_type._meta.fields["objects"].type.of_type, graphene.NonNull)
#         assert payload_type._meta.fields["objects"].type.of_type.of_type == MockModelObjectType

#         assert isinstance(payload_type._meta.fields["errors_report"], graphene.Field)
#         assert isinstance(payload_type._meta.fields["errors_report"].type, graphene.List)
#         assert payload_type._meta.fields["errors_report"].type.of_type == ErrorCollectionType
#         assert "success" in payload_type._meta.fields
#         assert payload_type._meta.fields["success"].type == graphene.Boolean


# class TestModelDeactivateField:
#     def test_deactivate_field_initialization(self, registry):
#         plural_model_name = "Tests"
#         resolver = lambda root, info, **kwargs: None
#         extra_args = {"extra_arg": graphene.String()}

#         deactivate_field = ModelDeactivateField(
#             plural_model_name=plural_model_name,
#             model=sample_model,
#             registry=registry,
#             state_controller_field="is_active",
#             resolver=resolver,
#             **extra_args
#         )
#         payload_type = deactivate_field.type

#         assert isinstance(deactivate_field, graphene.Field)
#         assert deactivate_field.name == f"deactivate{plural_model_name}"
#         assert deactivate_field.args == {"where": graphene.Argument(graphene.ID, required=True), "extra_arg": graphene.Argument(graphene.String)}
#         assert deactivate_field.resolver == resolver

#         assert issubclass(payload_type, graphene.ObjectType) # type: ignore
#         assert "objects" in payload_type._meta.fields
#         assert "errors_report" in payload_type._meta.fields
#         assert isinstance(payload_type._meta.fields["objects"], ModelListField)
#         assert isinstance(payload_type._meta.fields["objects"].type, graphene.List)
#         assert isinstance(payload_type._meta.fields["objects"].type.of_type, graphene.NonNull)
#         assert payload_type._meta.fields["objects"].type.of_type.of_type == MockModelObjectType

#         assert isinstance(payload_type._meta.fields["errors_report"], graphene.Field)
#         assert isinstance(payload_type._meta.fields["errors_report"].type, graphene.List)
#         assert payload_type._meta.fields["errors_report"].type.of_type == ErrorCollectionType
#         assert "success" not in payload_type._meta.fields


# class TestModelActivateField:
#     def test_activate_field_initialization(self, registry):
#         plural_model_name = "Tests"
#         resolver = lambda root, info, **kwargs: None
#         extra_args = {"extra_arg": graphene.String()}

#         activate_field = ModelActivateField(
#             plural_model_name=plural_model_name,
#             model=sample_model,
#             registry=registry,
#             state_controller_field="is_active",
#             resolver=resolver,
#             **extra_args
#         )
#         payload_type = activate_field.type

#         assert isinstance(activate_field, graphene.Field)
#         assert activate_field.name == f"activate{plural_model_name}"
#         assert activate_field.args == {"where": graphene.Argument(graphene.ID, required=True), "extra_arg": graphene.Argument(graphene.String)}
#         assert activate_field.resolver == resolver

#         assert issubclass(payload_type, graphene.ObjectType) # type: ignore
#         assert "objects" in payload_type._meta.fields
#         assert "errors_report" in payload_type._meta.fields
#         assert isinstance(payload_type._meta.fields["objects"], ModelListField)
#         assert isinstance(payload_type._meta.fields["objects"].type, graphene.List)
#         assert isinstance(payload_type._meta.fields["objects"].type.of_type, graphene.NonNull)
#         assert payload_type._meta.fields["objects"].type.of_type.of_type == MockModelObjectType

#         assert isinstance(payload_type._meta.fields["errors_report"], graphene.Field)
#         assert isinstance(payload_type._meta.fields["errors_report"].type, graphene.List)
#         assert payload_type._meta.fields["errors_report"].type.of_type == ErrorCollectionType
#         assert "success" not in payload_type._meta.fields


# class TestModelListField:
#     def test_list_field_initialization(self, registry):
#         plural_model_name = "Tests"
#         resolver = lambda root, info, **kwargs: None
#         extra_args = {"extra_arg": graphene.String()}

#         list_field = ModelListField(
#             plural_model_name=plural_model_name,
#             model=sample_model,
#             registry=registry,
#             resolver=resolver,
#             **extra_args
#         )
#         payload_type = list_field.type

#         assert isinstance(list_field, graphene.Field)
#         assert list_field.name == f"list{plural_model_name}"
#         assert list_field.args == {"extra_arg": graphene.Argument(graphene.String)}
#         assert list_field.resolver == resolver

#         assert isinstance(payload_type, graphene.List) # type: ignore
#         assert isinstance(payload_type.of_type, graphene.NonNull)
#         assert payload_type.of_type.of_type == MockModelObjectType


# class TestModelSearchField:
#     def test_search_field_initialization(self, registry):
#         plural_model_name = "Tests"
#         resolver = lambda root, info, **kwargs: None
#         extra_args = {"extra_arg": graphene.String()}

#         search_field = ModelSearchField(
#             plural_model_name=plural_model_name,
#             model=sample_model,
#             registry=registry,
#             resolver=resolver,
#             **extra_args
#         )
#         payload_type = search_field.type

#         assert isinstance(search_field, graphene.Field)
#         assert search_field.name == f"search{plural_model_name}"
#         assert search_field.args == {"where": graphene.Argument(ModelSearchInputObjectType), "order_by": graphene.Argument(ModelOrderByInputObjectType), "pagination": graphene.Argument(PaginationConfigInput), "extra_arg": graphene.Argument(graphene.String)}
#         assert search_field.resolver == resolver

#         assert isinstance(payload_type, graphene.ObjectType)
