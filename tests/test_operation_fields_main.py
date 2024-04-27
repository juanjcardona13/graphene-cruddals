import pytest
import graphene
from graphene_cruddals.operation_fields.main import get_object_type_payload, CreateUpdateField, ListField, ReadField, DeleteField, DeactivateField, ActivateField, SearchField, PaginationInterface, PaginationConfigInput, IntOrAll
from graphene_cruddals.utils.error_handling.error_types import ErrorCollectionType

from graphene.test import Client

from graphene_cruddals.utils.main import build_class


class MockModelObjectType(graphene.ObjectType):
    pass


class DummyModelType(graphene.ObjectType):
    field = graphene.String()


class DummyPaginatedModelType(graphene.ObjectType):
    class Meta:
        interfaces = (PaginationInterface,)
    objects = graphene.List(DummyModelType)


def test_get_object_type_payload_basic():
    payload_type = get_object_type_payload(MockModelObjectType, "TestOutput", "Tests", False)
    assert issubclass(payload_type, graphene.ObjectType)
    assert "objects" in payload_type._meta.fields
    assert "errors_report" in payload_type._meta.fields
    assert isinstance(payload_type._meta.fields["objects"], ListField)
    assert isinstance(payload_type._meta.fields["objects"].type, graphene.List)
    assert isinstance(payload_type._meta.fields["objects"].type.of_type, graphene.NonNull)
    assert payload_type._meta.fields["objects"].type.of_type.of_type == MockModelObjectType

    assert isinstance(payload_type._meta.fields["errors_report"], graphene.Field)
    assert isinstance(payload_type._meta.fields["errors_report"].type, graphene.List)
    assert payload_type._meta.fields["errors_report"].type.of_type == ErrorCollectionType
    assert "success" not in payload_type._meta.fields


def test_get_object_type_payload_include_success():
    payload_type = get_object_type_payload(MockModelObjectType, "TestOutput", "Tests", True)
    assert "success" in payload_type._meta.fields
    assert isinstance(payload_type._meta.fields["success"], graphene.Field)
    assert payload_type._meta.fields["success"].type == graphene.Boolean


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


@pytest.fixture
def client():
    query = build_class("Query", bases=(graphene.ObjectType,), attrs={"dummy": graphene.String()})
    schema = graphene.Schema(query=query, types=[DummyModelType, DummyPaginatedModelType])
    return Client(schema)


def test_pagination_interface_fields(client):
    result = client.execute('''
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
    ''')

    expected_fields = [
        {'name': 'total', 'type': {'name': 'Int', 'kind': 'SCALAR'}},
        {'name': 'page', 'type': {'name': 'Int', 'kind': 'SCALAR'}},
        {'name': 'pages', 'type': {'name': 'Int', 'kind': 'SCALAR'}},
        {'name': 'hasNext', 'type': {'name': 'Boolean', 'kind': 'SCALAR'}},
        {'name': 'hasPrev', 'type': {'name': 'Boolean', 'kind': 'SCALAR'}},
        {'name': 'indexStartObj', 'type': {'name': 'Int', 'kind': 'SCALAR'}},
        {'name': 'indexEndObj', 'type': {'name': 'Int', 'kind': 'SCALAR'}}
    ]

    assert result['data']['__type']['fields'] == expected_fields


class TestCreateUpdateField:

    def test_create_update_field_initialization_create(self):
        field = CreateUpdateField(MockModelObjectType, "Tests", "Create")
        payload_type = field.type
        
        assert isinstance(field, graphene.Field)
        assert field.args == {}
        assert field.resolver == None
        assert field.name == "createTests"

        assert issubclass(payload_type, graphene.ObjectType) # type: ignore
        assert "objects" in payload_type._meta.fields
        assert "errors_report" in payload_type._meta.fields
        assert isinstance(payload_type._meta.fields["objects"], ListField)
        assert isinstance(payload_type._meta.fields["objects"].type, graphene.List)
        assert isinstance(payload_type._meta.fields["objects"].type.of_type, graphene.NonNull)
        assert payload_type._meta.fields["objects"].type.of_type.of_type == MockModelObjectType

        assert isinstance(payload_type._meta.fields["errors_report"], graphene.Field)
        assert isinstance(payload_type._meta.fields["errors_report"].type, graphene.List)
        assert payload_type._meta.fields["errors_report"].type.of_type == ErrorCollectionType
        assert "success" not in payload_type._meta.fields

    def test_create_update_field_initialization_update(self):
        field = CreateUpdateField(MockModelObjectType, "Tests", "Update")
        payload_type = field.type

        assert isinstance(field, graphene.Field)
        assert field.args == {}
        assert field.resolver == None
        assert field.name == "updateTests"

        assert issubclass(payload_type, graphene.ObjectType) # type: ignore
        assert "objects" in payload_type._meta.fields
        assert "errors_report" in payload_type._meta.fields
        assert isinstance(payload_type._meta.fields["objects"], ListField)
        assert isinstance(payload_type._meta.fields["objects"].type, graphene.List)
        assert isinstance(payload_type._meta.fields["objects"].type.of_type, graphene.NonNull)
        assert payload_type._meta.fields["objects"].type.of_type.of_type == MockModelObjectType

        assert isinstance(payload_type._meta.fields["errors_report"], graphene.Field)
        assert isinstance(payload_type._meta.fields["errors_report"].type, graphene.List)
        assert payload_type._meta.fields["errors_report"].type.of_type == ErrorCollectionType
        assert "success" not in payload_type._meta.fields

    def test_create_update_field_with_args(self):
        field = CreateUpdateField(MockModelObjectType, "Tests", "Create", {"test": graphene.String()})
        assert field.args == {"test": graphene.Argument(graphene.String)}


class TestReadField:
    def test_read_field_initialization(self):
        singular_model_name = "TestModel"
        args = {"id": graphene.ID(required=True)}
        resolver = lambda root, info, **kwargs: None
        extra_args = {"extra_arg": graphene.String()}

        read_field = ReadField(MockModelObjectType, singular_model_name, args, resolver, **extra_args)

        assert isinstance(read_field, graphene.Field)
        assert read_field.type == MockModelObjectType
        assert read_field.name == f"read{singular_model_name}"
        assert read_field.args == {"id": graphene.Argument(graphene.ID, required=True), "extra_arg": graphene.Argument(graphene.String)}
        assert read_field.resolver == resolver


class TestDeleteField:
    def test_delete_field_initialization(self):
        plural_model_name = "Tests"
        args = {"id": graphene.ID(required=True)}
        resolver = lambda root, info, **kwargs: None
        extra_args = {"extra_arg": graphene.String()}

        delete_field = DeleteField(MockModelObjectType, plural_model_name, args, resolver, **extra_args)
        payload_type = delete_field.type

        assert isinstance(delete_field, graphene.Field)
        assert delete_field.name == f"delete{plural_model_name}"
        assert delete_field.args == {"id": graphene.Argument(graphene.ID, required=True), "extra_arg": graphene.Argument(graphene.String)}
        assert delete_field.resolver == resolver

        assert issubclass(payload_type, graphene.ObjectType) # type: ignore
        assert "objects" in payload_type._meta.fields
        assert "errors_report" in payload_type._meta.fields
        assert isinstance(payload_type._meta.fields["objects"], ListField)
        assert isinstance(payload_type._meta.fields["objects"].type, graphene.List)
        assert isinstance(payload_type._meta.fields["objects"].type.of_type, graphene.NonNull)
        assert payload_type._meta.fields["objects"].type.of_type.of_type == MockModelObjectType

        assert isinstance(payload_type._meta.fields["errors_report"], graphene.Field)
        assert isinstance(payload_type._meta.fields["errors_report"].type, graphene.List)
        assert payload_type._meta.fields["errors_report"].type.of_type == ErrorCollectionType
        assert "success" in payload_type._meta.fields
        assert payload_type._meta.fields["success"].type == graphene.Boolean


class TestDeactivateField:
    def test_deactivate_field_initialization(self):
        plural_model_name = "Tests"
        args = {"id": graphene.ID(required=True)}
        resolver = lambda root, info, **kwargs: None
        extra_args = {"extra_arg": graphene.String()}

        deactivate_field = DeactivateField(MockModelObjectType, plural_model_name, args, resolver, **extra_args)
        payload_type = deactivate_field.type

        assert isinstance(deactivate_field, graphene.Field)
        assert deactivate_field.name == f"deactivate{plural_model_name}"
        assert deactivate_field.args == {"id": graphene.Argument(graphene.ID, required=True), "extra_arg": graphene.Argument(graphene.String)}
        assert deactivate_field.resolver == resolver

        assert issubclass(payload_type, graphene.ObjectType) # type: ignore
        assert "objects" in payload_type._meta.fields
        assert "errors_report" in payload_type._meta.fields
        assert isinstance(payload_type._meta.fields["objects"], ListField)
        assert isinstance(payload_type._meta.fields["objects"].type, graphene.List)
        assert isinstance(payload_type._meta.fields["objects"].type.of_type, graphene.NonNull)
        assert payload_type._meta.fields["objects"].type.of_type.of_type == MockModelObjectType

        assert isinstance(payload_type._meta.fields["errors_report"], graphene.Field)
        assert isinstance(payload_type._meta.fields["errors_report"].type, graphene.List)
        assert payload_type._meta.fields["errors_report"].type.of_type == ErrorCollectionType
        assert "success" not in payload_type._meta.fields


class TestActivateField:
    def test_activate_field_initialization(self):
        plural_model_name = "Tests"
        args = {"id": graphene.ID(required=True)}
        resolver = lambda root, info, **kwargs: None
        extra_args = {"extra_arg": graphene.String()}

        activate_field = ActivateField(MockModelObjectType, plural_model_name, args, resolver, **extra_args)
        payload_type = activate_field.type

        assert isinstance(activate_field, graphene.Field)
        assert activate_field.name == f"activate{plural_model_name}"
        assert activate_field.args == {"id": graphene.Argument(graphene.ID, required=True), "extra_arg": graphene.Argument(graphene.String)}
        assert activate_field.resolver == resolver

        assert issubclass(payload_type, graphene.ObjectType) # type: ignore
        assert "objects" in payload_type._meta.fields
        assert "errors_report" in payload_type._meta.fields
        assert isinstance(payload_type._meta.fields["objects"], ListField)
        assert isinstance(payload_type._meta.fields["objects"].type, graphene.List)
        assert isinstance(payload_type._meta.fields["objects"].type.of_type, graphene.NonNull)
        assert payload_type._meta.fields["objects"].type.of_type.of_type == MockModelObjectType

        assert isinstance(payload_type._meta.fields["errors_report"], graphene.Field)
        assert isinstance(payload_type._meta.fields["errors_report"].type, graphene.List)
        assert payload_type._meta.fields["errors_report"].type.of_type == ErrorCollectionType
        assert "success" not in payload_type._meta.fields


class TestListField:
    def test_list_field_initialization(self):
        plural_model_name = "Tests"
        args = {"id": graphene.ID(required=True)}
        resolver = lambda root, info, **kwargs: None
        extra_args = {"extra_arg": graphene.String()}

        list_field = ListField(MockModelObjectType, plural_model_name, args, resolver, **extra_args)
        payload_type = list_field.type

        assert isinstance(list_field, graphene.Field)
        assert list_field.name == f"list{plural_model_name}"
        assert list_field.args == {"id": graphene.Argument(graphene.ID, required=True), "extra_arg": graphene.Argument(graphene.String)}
        assert list_field.resolver == resolver

        assert isinstance(payload_type, graphene.List) # type: ignore
        assert isinstance(payload_type.of_type, graphene.NonNull)
        assert payload_type.of_type.of_type == MockModelObjectType
        

    def test_list_field_initialization_no_args(self):
        plural_model_name = "Tests"
        resolver = lambda root, info, **kwargs: None
        extra_args = {"extra_arg": graphene.String()}

        list_field = ListField(MockModelObjectType, plural_model_name, None, resolver, **extra_args)
        payload_type = list_field.type

        assert isinstance(list_field, graphene.Field)
        assert list_field.name == f"list{plural_model_name}"
        assert list_field.args == {"extra_arg": graphene.Argument(graphene.String)}
        assert list_field.resolver == resolver

        assert isinstance(payload_type, graphene.List) # type: ignore
        assert isinstance(payload_type.of_type, graphene.NonNull)
        assert payload_type.of_type.of_type == MockModelObjectType


class TestSearchField:
    def test_search_field_initialization(self):
        field = SearchField(DummyPaginatedModelType, "DummyModel")
        assert isinstance(field, graphene.Field)
        assert field.type == DummyPaginatedModelType
        assert field.name == "searchDummyModel"
        assert field.args == {}
        assert field.resolver is None

    def test_search_field_initialization_with_args_and_resolver(self):
        args = {"query": graphene.String()}
        resolver = lambda root, info, **kwargs: None
        field = SearchField(DummyPaginatedModelType, "DummyModel", args=args, resolver=resolver)
        assert isinstance(field, graphene.Field)
        assert field.type == DummyPaginatedModelType
        assert field.name == "searchDummyModel"
        assert field.args == {"query": graphene.Argument(graphene.String)}
        assert field.resolver == resolver

    def test_search_field_initialization_without_pagination_interface(self):
        with pytest.raises(ValueError) as error:
            SearchField(DummyModelType, "DummyModel")
        assert str(error.value) == "The model_as_paginated_object_type must implement the PaginationInterface"