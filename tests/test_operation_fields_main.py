import inspect

import pytest

import graphene
from graphene.test import Client
from graphene_cruddals.operation_fields.main import (
    IntOrAll,
    ModelActivateField,
    ModelCreateUpdateField,
    ModelDeactivateField,
    ModelDeleteField,
    ModelListField,
    ModelReadField,
    ModelSearchField,
    PaginationConfigInput,
    build_argument_from_modification,
    get_object_type_payload,
)
from graphene_cruddals.registry.registry_global import (
    get_global_registry,
)
from graphene_cruddals.types.error_types import ErrorCollectionType
from graphene_cruddals.types.main import (
    ModelInputObjectType,
    ModelObjectType,
    ModelOrderByInputObjectType,
    ModelPaginatedObjectType,
    ModelSearchInputObjectType,
)
from graphene_cruddals.utils.main import build_class
from graphene_cruddals.utils.typing.custom_typing import (
    TypeRegistryForModelEnum,
)

mock_database = [
    {"id": 1, "name": "test1", "active": True},
    {"id": 2, "name": "test2", "active": False},
    {"id": 3, "name": "test3", "active": True},
]


class MockModelOperationFields:
    id: int
    name: str
    active: bool
    mock_field: str


class NewMockModel:
    new_field: str


class MockModelOperationFieldsObjectType(ModelObjectType):
    class Meta:
        model = MockModelOperationFields


class MockModelOperationFieldsPaginatedObjectType(ModelPaginatedObjectType):
    class Meta:
        model_object_type = MockModelOperationFieldsObjectType


class MockModelOperationFieldsInputObjectType(ModelInputObjectType):
    class Meta:
        model = MockModelOperationFields


class MockModelOperationFieldsSearchInputObjectType(ModelSearchInputObjectType):
    class Meta:
        model = MockModelOperationFields


class MockModelOperationFieldsOrderByInputObjectType(ModelOrderByInputObjectType):
    class Meta:
        model = MockModelOperationFields


@pytest.fixture
def registry():
    registry = get_global_registry()
    registry.register_model(
        MockModelOperationFields,
        TypeRegistryForModelEnum.OBJECT_TYPE.value,
        MockModelOperationFieldsObjectType,
    )
    registry.register_model(
        MockModelOperationFields,
        TypeRegistryForModelEnum.PAGINATED_OBJECT_TYPE.value,
        MockModelOperationFieldsPaginatedObjectType,
    )
    registry.register_model(
        MockModelOperationFields,
        TypeRegistryForModelEnum.INPUT_OBJECT_TYPE.value,
        MockModelOperationFieldsInputObjectType,
    )
    registry.register_model(
        MockModelOperationFields,
        TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_CREATE.value,
        MockModelOperationFieldsInputObjectType,
    )
    registry.register_model(
        MockModelOperationFields,
        TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_UPDATE.value,
        MockModelOperationFieldsInputObjectType,
    )
    registry.register_model(
        MockModelOperationFields,
        TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_SEARCH.value,
        MockModelOperationFieldsSearchInputObjectType,
    )
    registry.register_model(
        MockModelOperationFields,
        TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_ORDER_BY.value,
        MockModelOperationFieldsOrderByInputObjectType,
    )
    return registry


@pytest.fixture
def client():
    query = build_class(
        "Query", bases=(graphene.ObjectType,), attrs={"sample": graphene.String()}
    )
    schema = graphene.Schema(
        query=query,
        types=[
            MockModelOperationFieldsObjectType,
            MockModelOperationFieldsPaginatedObjectType,
        ],
    )
    return Client(schema)


def test_get_object_type_payload_basic(registry):
    payload_type = get_object_type_payload(
        model=MockModelOperationFields,
        registry=registry,
        name_for_output_type="MockModelOperationFieldsObjectType",
        plural_model_name="Tests",
        include_success=False,
    )
    assert issubclass(payload_type, graphene.ObjectType)
    assert "objects" in payload_type._meta.fields
    assert "errors_report" in payload_type._meta.fields
    assert isinstance(payload_type._meta.fields["objects"], graphene.Field)
    assert isinstance(payload_type._meta.fields["objects"].type, graphene.List)
    assert (
        payload_type._meta.fields["objects"].type.of_type
        == MockModelOperationFieldsObjectType
    )

    assert isinstance(payload_type._meta.fields["errors_report"], graphene.Field)
    assert isinstance(payload_type._meta.fields["errors_report"].type, graphene.List)
    assert (
        payload_type._meta.fields["errors_report"].type.of_type == ErrorCollectionType
    )
    assert "success" not in payload_type._meta.fields


def test_get_object_type_payload_include_success(registry):
    payload_type = get_object_type_payload(
        model=MockModelOperationFields,
        registry=registry,
        name_for_output_type="MockModelOperationFieldsObjectType",
        plural_model_name="Tests",
        include_success=True,
    )
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


class TestModelCreateUpdateField:
    def test_create_update_field_initialization_create(self, registry):
        field = ModelCreateUpdateField(
            plural_model_name="Tests",
            type_operation="Create",
            model=MockModelOperationFields,
            registry=registry,
        )
        payload_type = field.type

        assert isinstance(field, graphene.Field)
        assert "input" in field.args
        assert field.resolver is None
        assert field.name == "createTests"

        assert issubclass(payload_type, graphene.ObjectType)  # type: ignore
        assert "objects" in payload_type._meta.fields
        assert "errors_report" in payload_type._meta.fields
        assert isinstance(payload_type._meta.fields["objects"], graphene.Field)
        assert isinstance(payload_type._meta.fields["objects"].type, graphene.List)
        assert (
            payload_type._meta.fields["objects"].type.of_type
            == MockModelOperationFieldsObjectType
        )

        assert isinstance(payload_type._meta.fields["errors_report"], graphene.Field)
        assert isinstance(
            payload_type._meta.fields["errors_report"].type, graphene.List
        )
        assert (
            payload_type._meta.fields["errors_report"].type.of_type
            == ErrorCollectionType
        )
        assert "success" not in payload_type._meta.fields

    def test_create_update_field_initialization_update(self, registry):
        field = ModelCreateUpdateField(
            plural_model_name="Tests",
            type_operation="Update",
            model=MockModelOperationFields,
            registry=registry,
        )
        payload_type = field.type

        assert isinstance(field, graphene.Field)
        assert "input" in field.args
        assert field.resolver is None
        assert field.name == "updateTests"

        assert issubclass(payload_type, graphene.ObjectType)  # type: ignore
        assert "objects" in payload_type._meta.fields
        assert "errors_report" in payload_type._meta.fields
        assert isinstance(payload_type._meta.fields["objects"], graphene.Field)
        assert isinstance(payload_type._meta.fields["objects"].type, graphene.List)
        assert (
            payload_type._meta.fields["objects"].type.of_type
            == MockModelOperationFieldsObjectType
        )

        assert isinstance(payload_type._meta.fields["errors_report"], graphene.Field)
        assert isinstance(
            payload_type._meta.fields["errors_report"].type, graphene.List
        )
        assert (
            payload_type._meta.fields["errors_report"].type.of_type
            == ErrorCollectionType
        )
        assert "success" not in payload_type._meta.fields

    def test_create_update_field_without_input_object_type(self, registry):
        with pytest.raises(ValueError) as exc_info:

            class NewModel:
                new_field = str

            ModelCreateUpdateField(
                plural_model_name="Tests",
                type_operation="Create",
                model=NewModel,
                registry=registry,
            )
        assert "The model does not have a ModelInputObjectType registered" in str(
            exc_info.value
        )

    def test_wrap_resolve_with_resolver(self, registry):
        # Setup: Create an instance of ModelCreateUpdateField with a mock resolver
        def mock_resolver(*args, **kwargs):
            return "mock result"

        field = ModelCreateUpdateField(
            plural_model_name="Tests",
            type_operation="Create",
            model=MockModelOperationFields,
            registry=registry,
            resolver=mock_resolver,
        )

        # Action: Wrap the resolver using wrap_resolve method
        wrapped_resolver = field.wrap_resolve(field.resolver)

        # Assert: Check if the returned resolver is not None and callable
        assert wrapped_resolver is not None
        assert callable(wrapped_resolver)

    def test_wrap_resolve_without_resolver(self, registry):
        # Setup: Create an instance of ModelCreateUpdateField without providing a resolver
        field = ModelCreateUpdateField(
            plural_model_name="Tests",
            type_operation="Create",
            model=MockModelOperationFields,
            registry=registry,
            resolver=None,  # Explicitly set resolver to None
        )

        # Action & Assert: Assert that calling wrap_resolve raises a ValueError
        with pytest.raises(ValueError) as exc_info:
            field.wrap_resolve(field.resolver)

        assert "resolver is None for ModelCreateUpdateField" in str(exc_info.value)


class TestModelReadField:
    def test_read_field_initialization(self, registry):
        singular_model_name = "TestModel"

        def resolver(root, info, **kwargs):
            return None

        extra_args = {"extra_arg": graphene.String()}

        read_field = ModelReadField(
            singular_model_name=singular_model_name,
            model=MockModelOperationFields,
            registry=registry,
            resolver=resolver,
            **extra_args,
        )

        assert isinstance(read_field, ModelReadField)
        assert read_field.type == MockModelOperationFieldsObjectType
        assert read_field.name == f"read{singular_model_name}"
        assert "where" in read_field.args
        assert "extra_arg" in read_field.args
        assert read_field.resolver == resolver

    def test_read_field_without_model_search_input_object_type(self, registry):
        singular_model_name = "TestModel"

        def resolver(root, info, **kwargs):
            return None

        extra_args = {"extra_arg": graphene.String()}

        with pytest.raises(ValueError) as exc_info:
            ModelReadField(
                singular_model_name=singular_model_name,
                model=NewMockModel,
                registry=registry,
                resolver=resolver,
                **extra_args,
            )
        assert (
            "The model does not have a ModelSearchInputObjectType registered and it is required for the read operation"
            in str(exc_info.value)
        )

    def test_wrap_resolve_with_resolver(self, registry):
        # Setup: Create an instance of ModelReadField with a mock resolver
        def mock_resolver(*args, **kwargs):
            return "mock result"

        field = ModelReadField(
            singular_model_name="TestModel",
            model=MockModelOperationFields,
            registry=registry,
            resolver=mock_resolver,
        )

        # Action: Wrap the resolver using wrap_resolve method
        wrapped_resolver = field.wrap_resolve(field.resolver)

        # Assert: Check if the returned resolver is not None and callable
        assert wrapped_resolver is not None
        assert callable(wrapped_resolver)

    def test_wrap_resolve_without_resolver(self, registry):
        # Setup: Create an instance of ModelReadField without providing a resolver
        field = ModelReadField(
            singular_model_name="TestModel",
            model=MockModelOperationFields,
            registry=registry,
            resolver=None,  # Explicitly set resolver to None
        )

        # Action & Assert: Assert that calling wrap_resolve raises a ValueError
        with pytest.raises(ValueError) as exc_info:
            field.wrap_resolve(field.resolver)

        assert "resolver is None for ModelReadField" in str(exc_info.value)


class TestModelDeleteField:
    def test_delete_field_initialization(self, registry):
        plural_model_name = "Tests"

        def resolver(root, info, **kwargs):
            return None

        extra_args = {"extra_arg": graphene.String()}

        delete_field = ModelDeleteField(
            plural_model_name=plural_model_name,
            model=MockModelOperationFields,
            registry=registry,
            resolver=resolver,
            **extra_args,
        )
        payload_type = delete_field.type

        assert isinstance(delete_field, graphene.Field)
        assert delete_field.name == f"delete{plural_model_name}"
        assert "where" in delete_field.args
        assert "extra_arg" in delete_field.args
        assert delete_field.resolver == resolver

        assert issubclass(payload_type, graphene.ObjectType)  # type: ignore
        assert "objects" in payload_type._meta.fields
        assert "errors_report" in payload_type._meta.fields
        assert isinstance(payload_type._meta.fields["objects"], graphene.Field)
        assert isinstance(payload_type._meta.fields["objects"].type, graphene.List)
        assert (
            payload_type._meta.fields["objects"].type.of_type
            == MockModelOperationFieldsObjectType
        )

        assert isinstance(payload_type._meta.fields["errors_report"], graphene.Field)
        assert isinstance(
            payload_type._meta.fields["errors_report"].type, graphene.List
        )
        assert (
            payload_type._meta.fields["errors_report"].type.of_type
            == ErrorCollectionType
        )
        assert "success" in payload_type._meta.fields
        assert payload_type._meta.fields["success"].type == graphene.Boolean

    def test_delete_field_without_model_search_input_object_type(self, registry):
        plural_model_name = "Tests"

        def resolver(root, info, **kwargs):
            return None

        extra_args = {"extra_arg": graphene.String()}

        with pytest.raises(ValueError) as exc_info:
            ModelDeleteField(
                plural_model_name=plural_model_name,
                model=NewMockModel,
                registry=registry,
                resolver=resolver,
                **extra_args,
            )
        assert (
            "The model does not have a ModelSearchInputObjectType registered and it is required for the delete operation"
            in str(exc_info.value)
        )

    def test_wrap_resolve_with_resolver(self, registry):
        # Setup: Create an instance of ModelDeleteField with a mock resolver
        def mock_resolver(*args, **kwargs):
            return "mock result"

        field = ModelDeleteField(
            plural_model_name="Tests",
            model=MockModelOperationFields,
            registry=registry,
            resolver=mock_resolver,
        )

        # Action: Wrap the resolver using wrap_resolve method
        wrapped_resolver = field.wrap_resolve(field.resolver)

        # Assert: Check if the returned resolver is not None and callable
        assert wrapped_resolver is not None
        assert callable(wrapped_resolver)

    def test_wrap_resolve_without_resolver(self, registry):
        # Setup: Create an instance of ModelDeleteField without providing a resolver
        field = ModelDeleteField(
            plural_model_name="Tests",
            model=MockModelOperationFields,
            registry=registry,
            resolver=None,  # Explicitly set resolver to None
        )

        # Action & Assert: Assert that calling wrap_resolve raises a ValueError
        with pytest.raises(ValueError) as exc_info:
            field.wrap_resolve(field.resolver)

        assert "resolver is None for ModelDeleteField" in str(exc_info.value)


class TestModelDeactivateField:
    def test_deactivate_field_initialization(self, registry):
        plural_model_name = "Tests"

        def resolver(root, info, **kwargs):
            return None

        extra_args = {"extra_arg": graphene.String()}

        deactivate_field = ModelDeactivateField(
            plural_model_name=plural_model_name,
            model=MockModelOperationFields,
            registry=registry,
            state_controller_field="is_active",
            resolver=resolver,
            **extra_args,
        )
        payload_type = deactivate_field.type

        assert isinstance(deactivate_field, graphene.Field)
        assert deactivate_field.name == f"deactivate{plural_model_name}"
        assert "where" in deactivate_field.args
        assert "extra_arg" in deactivate_field.args
        assert deactivate_field.resolver == resolver

        assert issubclass(payload_type, graphene.ObjectType)  # type: ignore
        assert "objects" in payload_type._meta.fields
        assert "errors_report" in payload_type._meta.fields
        assert isinstance(payload_type._meta.fields["objects"], graphene.Field)
        assert isinstance(payload_type._meta.fields["objects"].type, graphene.List)
        assert (
            payload_type._meta.fields["objects"].type.of_type
            == MockModelOperationFieldsObjectType
        )

        assert isinstance(payload_type._meta.fields["errors_report"], graphene.Field)
        assert isinstance(
            payload_type._meta.fields["errors_report"].type, graphene.List
        )
        assert (
            payload_type._meta.fields["errors_report"].type.of_type
            == ErrorCollectionType
        )
        assert "success" not in payload_type._meta.fields

    def test_deactivate_field_without_model_search_input_object_type(self, registry):
        plural_model_name = "Tests"

        def resolver(root, info, **kwargs):
            return None

        extra_args = {"extra_arg": graphene.String()}

        with pytest.raises(ValueError) as exc_info:
            ModelDeactivateField(
                plural_model_name=plural_model_name,
                model=NewMockModel,
                registry=registry,
                state_controller_field="is_active",
                resolver=resolver,
                **extra_args,
            )
        assert (
            "The model does not have a ModelSearchInputObjectType registered and it is required for the deactivate operation"
            in str(exc_info.value)
        )

    def test_wrap_resolve_with_resolver(self, registry):
        # Setup: Create an instance of ModelDeactivateField with a mock resolver
        def mock_resolver(*args, **kwargs):
            return "mock result"

        field = ModelDeactivateField(
            plural_model_name="Tests",
            model=MockModelOperationFields,
            registry=registry,
            state_controller_field="is_active",
            resolver=mock_resolver,
        )

        # Action: Wrap the resolver using wrap_resolve method
        wrapped_resolver = field.wrap_resolve(field.resolver)

        # Assert: Check if the returned resolver is not None and callable
        assert wrapped_resolver is not None
        assert callable(wrapped_resolver)

    def test_wrap_resolve_without_resolver(self, registry):
        # Setup: Create an instance of ModelDeactivateField without providing a resolver
        field = ModelDeactivateField(
            plural_model_name="Tests",
            model=MockModelOperationFields,
            registry=registry,
            state_controller_field="is_active",
            resolver=None,  # Explicitly set resolver to None
        )

        # Action & Assert: Assert that calling wrap_resolve raises a ValueError
        with pytest.raises(ValueError) as exc_info:
            field.wrap_resolve(field.resolver)

        assert "resolver is None for ModelDeactivateField" in str(exc_info.value)


class TestModelActivateField:
    def test_activate_field_initialization(self, registry):
        plural_model_name = "Tests"

        def resolver(root, info, **kwargs):
            return None

        extra_args = {"extra_arg": graphene.String()}

        activate_field = ModelActivateField(
            plural_model_name=plural_model_name,
            model=MockModelOperationFields,
            registry=registry,
            state_controller_field="is_active",
            resolver=resolver,
            **extra_args,
        )
        payload_type = activate_field.type

        assert isinstance(activate_field, graphene.Field)
        assert activate_field.name == f"activate{plural_model_name}"
        assert "where" in activate_field.args
        assert "extra_arg" in activate_field.args
        assert activate_field.resolver == resolver

        assert issubclass(payload_type, graphene.ObjectType)  # type: ignore
        assert "objects" in payload_type._meta.fields
        assert "errors_report" in payload_type._meta.fields
        assert isinstance(payload_type._meta.fields["objects"], graphene.Field)
        assert isinstance(payload_type._meta.fields["objects"].type, graphene.List)
        assert (
            payload_type._meta.fields["objects"].type.of_type
            == MockModelOperationFieldsObjectType
        )

        assert isinstance(payload_type._meta.fields["errors_report"], graphene.Field)
        assert isinstance(
            payload_type._meta.fields["errors_report"].type, graphene.List
        )
        assert (
            payload_type._meta.fields["errors_report"].type.of_type
            == ErrorCollectionType
        )
        assert "success" not in payload_type._meta.fields

    def test_activate_field_without_model_search_input_object_type(self, registry):
        plural_model_name = "Tests"

        def resolver(root, info, **kwargs):
            return None

        extra_args = {"extra_arg": graphene.String()}

        with pytest.raises(ValueError) as exc_info:
            ModelActivateField(
                plural_model_name=plural_model_name,
                model=NewMockModel,
                registry=registry,
                state_controller_field="is_active",
                resolver=resolver,
                **extra_args,
            )
        assert (
            "The model does not have a ModelSearchInputObjectType registered and it is required for the activate operation"
            in str(exc_info.value)
        )

    def test_wrap_resolve_with_resolver(self, registry):
        # Setup: Create an instance of ModelActivateField with a mock resolver
        def mock_resolver(*args, **kwargs):
            return "mock result"

        field = ModelActivateField(
            plural_model_name="Tests",
            model=MockModelOperationFields,
            registry=registry,
            state_controller_field="is_active",
            resolver=mock_resolver,
        )

        # Action: Wrap the resolver using wrap_resolve method
        wrapped_resolver = field.wrap_resolve(field.resolver)

        # Assert: Check if the returned resolver is not None and callable
        assert wrapped_resolver is not None
        assert callable(wrapped_resolver)

    def test_wrap_resolve_without_resolver(self, registry):
        # Setup: Create an instance of ModelActivateField without providing a resolver
        field = ModelActivateField(
            plural_model_name="Tests",
            model=MockModelOperationFields,
            registry=registry,
            state_controller_field="is_active",
            resolver=None,  # Explicitly set resolver to None
        )

        # Action & Assert: Assert that calling wrap_resolve raises a ValueError
        with pytest.raises(ValueError) as exc_info:
            field.wrap_resolve(field.resolver)

        assert "resolver is None for ModelActivateField" in str(exc_info.value)


class TestModelListField:
    def test_list_field_initialization(self, registry):
        plural_model_name = "Tests"

        def resolver(root, info, **kwargs):
            return None

        extra_args = {"extra_arg": graphene.String()}

        list_field = ModelListField(
            plural_model_name=plural_model_name,
            model=MockModelOperationFields,
            registry=registry,
            resolver=resolver,
            **extra_args,
        )
        payload_type = list_field.type

        assert isinstance(list_field, graphene.Field)
        assert list_field.name == f"list{plural_model_name}"
        assert "extra_arg" in list_field.args
        assert list_field.resolver == resolver

        assert isinstance(payload_type, graphene.List)  # type: ignore
        assert isinstance(payload_type.of_type, graphene.NonNull)
        assert payload_type.of_type.of_type == MockModelOperationFieldsObjectType

    def test_wrap_resolve_with_resolver(self, registry):
        # Setup: Create an instance of ModelListField with a mock resolver
        def mock_resolver(*args, **kwargs):
            return "mock result"

        field = ModelListField(
            plural_model_name="Tests",
            model=MockModelOperationFields,
            registry=registry,
            resolver=mock_resolver,
        )

        # Action: Wrap the resolver using wrap_resolve method
        wrapped_resolver = field.wrap_resolve(field.resolver)

        # Assert: Check if the returned resolver is not None and callable
        assert wrapped_resolver is not None
        assert callable(wrapped_resolver)

    def test_wrap_resolve_without_resolver(self, registry):
        # Setup: Create an instance of ModelListField without providing a resolver
        field = ModelListField(
            plural_model_name="Tests",
            model=MockModelOperationFields,
            registry=registry,
            resolver=None,  # Explicitly set resolver to None
        )

        # Action & Assert: Assert that calling wrap_resolve raises a ValueError
        with pytest.raises(ValueError) as exc_info:
            field.wrap_resolve(field.resolver)

        assert "resolver is None for ModelListField" in str(exc_info.value)


class TestModelSearchField:
    def test_search_field_initialization(self, registry):
        plural_model_name = "Tests"

        def resolver(root, info, **kwargs):
            return None

        extra_args = {"extra_arg": graphene.String()}

        search_field = ModelSearchField(
            plural_model_name=plural_model_name,
            model=MockModelOperationFields,
            registry=registry,
            resolver=resolver,
            **extra_args,
        )

        assert isinstance(search_field, graphene.Field)
        assert search_field.name == f"search{plural_model_name}"
        assert "where" in search_field.args
        assert "order_by" in search_field.args
        assert "pagination_config" in search_field.args
        assert "extra_arg" in search_field.args
        assert search_field.resolver == resolver

    def test_search_field_without_model_paginated_object_type(self, registry):
        plural_model_name = "Tests"

        def resolver(root, info, **kwargs):
            return None

        extra_args = {"extra_arg": graphene.String()}

        with pytest.raises(ValueError) as exc_info:
            ModelSearchField(
                plural_model_name=plural_model_name,
                model=NewMockModel,
                registry=registry,
                resolver=resolver,
                **extra_args,
            )
        assert (
            "The model does not have a ModelPaginatedObjectType registered and it is required for the search operation"
            in str(exc_info.value)
        )

    def test_wrap_resolve_with_resolver(self, registry):
        # Setup: Create an instance of ModelSearchField with a mock resolver
        def mock_resolver(*args, **kwargs):
            return "mock result"

        field = ModelSearchField(
            plural_model_name="Tests",
            model=MockModelOperationFields,
            registry=registry,
            resolver=mock_resolver,
        )

        # Action: Wrap the resolver using wrap_resolve method
        wrapped_resolver = field.wrap_resolve(field.resolver)

        # Assert: Check if the returned resolver is not None and callable
        assert wrapped_resolver is not None
        assert callable(wrapped_resolver)

    def test_wrap_resolve_without_resolver(self, registry):
        # Setup: Create an instance of ModelSearchField without providing a resolver
        field = ModelSearchField(
            plural_model_name="Tests",
            model=MockModelOperationFields,
            registry=registry,
            resolver=None,  # Explicitly set resolver to None
        )

        # Action & Assert: Assert that calling wrap_resolve raises a ValueError
        with pytest.raises(ValueError) as exc_info:
            field.wrap_resolve(field.resolver)

        assert "resolver is None for ModelSearchField" in str(exc_info.value)

    def test_search_field_without_model_search_input_object_type(self):
        class NewMockModel:
            new_field = str
            mock2 = int

        class NewMockModelOperationFieldsObjectType(ModelObjectType):
            class Meta:
                model = NewMockModel

        class NewMockModelOperationFieldsPaginatedObjectType(ModelPaginatedObjectType):
            class Meta:
                model_object_type = NewMockModelOperationFieldsObjectType

        registry = get_global_registry()
        registry.register_model(
            NewMockModel,
            TypeRegistryForModelEnum.OBJECT_TYPE.value,
            NewMockModelOperationFieldsObjectType,
        )
        registry.register_model(
            NewMockModel,
            TypeRegistryForModelEnum.PAGINATED_OBJECT_TYPE.value,
            NewMockModelOperationFieldsPaginatedObjectType,
        )

        plural_model_name = "Tests"

        def resolver(root, info, **kwargs):
            return None

        extra_args = {"extra_arg": graphene.String()}

        with pytest.raises(ValueError) as exc_info:
            ModelSearchField(
                plural_model_name=plural_model_name,
                model=NewMockModel,
                registry=registry,
                resolver=resolver,
                **extra_args,
            )
        assert (
            "The model does not have a ModelSearchInputObjectType registered and it is required for the search operation"
            in str(exc_info.value)
        )

    def test_search_field_without_model_order_by_input_object_type(self):
        class NewMockModel:
            new_field = str
            mock1 = int

        class MockModelOperationFieldsObjectType(ModelObjectType):
            class Meta:
                model = NewMockModel

        class MockModelOperationFieldsPaginatedObjectType(ModelPaginatedObjectType):
            class Meta:
                model_object_type = MockModelOperationFieldsObjectType

        class MockModelOperationFieldsSearchInputObjectType(ModelSearchInputObjectType):
            class Meta:
                model = NewMockModel

        registry = get_global_registry()
        registry.register_model(
            NewMockModel,
            TypeRegistryForModelEnum.OBJECT_TYPE.value,
            MockModelOperationFieldsObjectType,
        )
        registry.register_model(
            NewMockModel,
            TypeRegistryForModelEnum.PAGINATED_OBJECT_TYPE.value,
            MockModelOperationFieldsPaginatedObjectType,
        )
        registry.register_model(
            NewMockModel,
            TypeRegistryForModelEnum.INPUT_OBJECT_TYPE_FOR_SEARCH.value,
            MockModelOperationFieldsSearchInputObjectType,
        )

        plural_model_name = "Tests"

        def resolver(root, info, **kwargs):
            return None

        extra_args = {"extra_arg": graphene.String()}

        with pytest.raises(ValueError) as exc_info:
            ModelSearchField(
                plural_model_name=plural_model_name,
                model=NewMockModel,
                registry=registry,
                resolver=resolver,
                **extra_args,
            )
        assert (
            "The model does not have a ModelOrderByInputObjectType registered and it is required for the search operation"
            in str(exc_info.value)
        )


class TestBuildArgumentFromModification:
    def test_build_argument_without_config(self):
        """Test that build_argument_from_modification creates argument with defaults when config is None"""
        arg = build_argument_from_modification(
            modify_config=None,
            default_type=graphene.String,
            default_name="test_arg",
            default_required=True,
            default_description="Test description",
        )

        assert arg is not None
        assert arg.name == "test_arg"
        assert isinstance(arg.type, graphene.NonNull)
        assert arg.description == "Test description"

    def test_build_argument_with_hidden_true(self):
        """Test that build_argument_from_modification returns None when hidden=True"""
        arg = build_argument_from_modification(
            modify_config={"hidden": True},
            default_type=graphene.String,
            default_name="test_arg",
        )

        assert arg is None

    def test_build_argument_modify_required(self):
        """Test modifying the required property"""
        arg = build_argument_from_modification(
            modify_config={"required": False},
            default_type=graphene.String,
            default_name="test_arg",
            default_required=True,
        )

        assert arg is not None
        assert not isinstance(arg.type, graphene.NonNull)

    def test_build_argument_modify_name(self):
        """Test modifying the name property"""
        arg = build_argument_from_modification(
            modify_config={"name": "new_name"},
            default_type=graphene.String,
            default_name="test_arg",
        )

        assert arg is not None
        assert arg.name == "new_name"

    def test_build_argument_modify_description(self):
        """Test modifying the description property"""
        arg = build_argument_from_modification(
            modify_config={"description": "New description"},
            default_type=graphene.String,
            default_name="test_arg",
            default_description="Old description",
        )

        assert arg is not None
        assert arg.description == "New description"

    def test_build_argument_modify_all_properties(self):
        """Test modifying multiple properties at once"""
        arg = build_argument_from_modification(
            modify_config={
                "name": "custom_arg",
                "required": False,
                "description": "Custom description",
                "default_value": "default",
                "deprecation_reason": "Deprecated",
            },
            default_type=graphene.String,
            default_name="test_arg",
            default_required=True,
        )

        assert arg is not None
        assert arg.name == "custom_arg"
        assert not isinstance(arg.type, graphene.NonNull)
        assert arg.description == "Custom description"
        assert arg.default_value == "default"
        if (
            "deprecation_reason"
            in inspect.signature(graphene.Argument.__init__).parameters
        ):
            assert arg.deprecation_reason == "Deprecated"


class TestModelCreateUpdateFieldArgumentModification:
    def test_modify_input_argument_required_false(self, registry):
        """Test making the input argument optional"""
        field = ModelCreateUpdateField(
            plural_model_name="Tests",
            type_operation="Create",
            model=MockModelOperationFields,
            registry=registry,
            modify_input_argument={"required": False},
        )

        assert "input" in field.args
        # When required=False, the type should not be wrapped in NonNull
        # The input is a List, so we check if the List itself is not NonNull
        assert not isinstance(field.args["input"].type, graphene.NonNull)

    def test_modify_input_argument_name(self, registry):
        """Test changing the name of the input argument"""
        field = ModelCreateUpdateField(
            plural_model_name="Tests",
            type_operation="Create",
            model=MockModelOperationFields,
            registry=registry,
            modify_input_argument={"name": "data"},
        )

        assert "data" in field.args
        assert "input" not in field.args
        assert field.args["data"].name == "data"

    def test_modify_input_argument_description(self, registry):
        """Test adding description to input argument"""
        field = ModelCreateUpdateField(
            plural_model_name="Tests",
            type_operation="Create",
            model=MockModelOperationFields,
            registry=registry,
            modify_input_argument={"description": "Input data for creation"},
        )

        assert "input" in field.args
        assert field.args["input"].description == "Input data for creation"

    def test_modify_input_argument_hidden(self, registry):
        """Test hiding the input argument"""
        field = ModelCreateUpdateField(
            plural_model_name="Tests",
            type_operation="Create",
            model=MockModelOperationFields,
            registry=registry,
            modify_input_argument={"hidden": True},
        )

        assert "input" not in field.args
        assert len(field.args) == 0

    def test_modify_input_argument_with_extra_arguments(self, registry):
        """Test combining modify_input_argument with extra_arguments"""
        field = ModelCreateUpdateField(
            plural_model_name="Tests",
            type_operation="Create",
            model=MockModelOperationFields,
            registry=registry,
            modify_input_argument={"description": "Custom input"},
            **{"extra": graphene.Argument(graphene.String, name="extra")},
        )

        assert "input" in field.args
        assert "extra" in field.args
        assert field.args["input"].description == "Custom input"


class TestModelReadFieldArgumentModification:
    def test_modify_where_argument_required_false(self, registry):
        """Test making the where argument optional"""
        field = ModelReadField(
            singular_model_name="Test",
            model=MockModelOperationFields,
            registry=registry,
            modify_where_argument={"required": False},
        )

        assert "where" in field.args
        assert not isinstance(field.args["where"].type, graphene.NonNull)

    def test_modify_where_argument_name(self, registry):
        """Test changing the name of the where argument"""
        field = ModelReadField(
            singular_model_name="Test",
            model=MockModelOperationFields,
            registry=registry,
            modify_where_argument={"name": "filter"},
        )

        assert "filter" in field.args
        assert "where" not in field.args
        assert field.args["filter"].name == "filter"

    def test_modify_where_argument_hidden(self, registry):
        """Test hiding the where argument"""
        field = ModelReadField(
            singular_model_name="Test",
            model=MockModelOperationFields,
            registry=registry,
            modify_where_argument={"hidden": True},
        )

        assert "where" not in field.args
        assert len(field.args) == 0


class TestModelDeleteFieldArgumentModification:
    def test_modify_where_argument_required_false(self, registry):
        """Test making the where argument optional in delete field"""
        field = ModelDeleteField(
            plural_model_name="Tests",
            model=MockModelOperationFields,
            registry=registry,
            modify_where_argument={"required": False},
        )

        assert "where" in field.args
        assert not isinstance(field.args["where"].type, graphene.NonNull)

    def test_modify_where_argument_name(self, registry):
        """Test changing the name of the where argument in delete field"""
        field = ModelDeleteField(
            plural_model_name="Tests",
            model=MockModelOperationFields,
            registry=registry,
            modify_where_argument={"name": "filter"},
        )

        assert "filter" in field.args
        assert "where" not in field.args


class TestModelDeactivateFieldArgumentModification:
    def test_modify_where_argument_required_false(self, registry):
        """Test making the where argument optional in deactivate field"""
        field = ModelDeactivateField(
            plural_model_name="Tests",
            model=MockModelOperationFields,
            registry=registry,
            modify_where_argument={"required": False},
        )

        assert "where" in field.args
        assert not isinstance(field.args["where"].type, graphene.NonNull)


class TestModelActivateFieldArgumentModification:
    def test_modify_where_argument_required_false(self, registry):
        """Test making the where argument optional in activate field"""
        field = ModelActivateField(
            plural_model_name="Tests",
            model=MockModelOperationFields,
            registry=registry,
            modify_where_argument={"required": False},
        )

        assert "where" in field.args
        assert not isinstance(field.args["where"].type, graphene.NonNull)


class TestModelSearchFieldArgumentModification:
    def test_modify_where_argument(self, registry):
        """Test modifying the where argument in search field"""
        field = ModelSearchField(
            plural_model_name="Tests",
            model=MockModelOperationFields,
            registry=registry,
            modify_where_argument={
                "required": True,
                "description": "Filter conditions",
            },
        )

        assert "where" in field.args
        assert isinstance(field.args["where"].type, graphene.NonNull)
        assert field.args["where"].description == "Filter conditions"

    def test_modify_order_by_argument(self, registry):
        """Test modifying the order_by argument in search field"""
        field = ModelSearchField(
            plural_model_name="Tests",
            model=MockModelOperationFields,
            registry=registry,
            modify_order_by_argument={
                "name": "sortBy",
                "description": "Sorting options",
            },
        )

        assert "sortBy" in field.args
        assert "order_by" not in field.args
        assert field.args["sortBy"].description == "Sorting options"

    def test_modify_pagination_config_argument(self, registry):
        """Test modifying the pagination_config argument in search field"""
        field = ModelSearchField(
            plural_model_name="Tests",
            model=MockModelOperationFields,
            registry=registry,
            modify_pagination_config_argument={"name": "pagination", "required": True},
        )

        assert "pagination" in field.args
        assert "pagination_config" not in field.args
        assert isinstance(field.args["pagination"].type, graphene.NonNull)

    def test_modify_all_search_arguments(self, registry):
        """Test modifying all arguments in search field"""
        field = ModelSearchField(
            plural_model_name="Tests",
            model=MockModelOperationFields,
            registry=registry,
            modify_where_argument={"description": "Where clause"},
            modify_order_by_argument={"description": "Order by clause"},
            modify_pagination_config_argument={"description": "Pagination config"},
        )

        assert "where" in field.args
        assert "order_by" in field.args
        assert "pagination_config" in field.args
        assert field.args["where"].description == "Where clause"
        assert field.args["order_by"].description == "Order by clause"
        assert field.args["pagination_config"].description == "Pagination config"

    def test_hide_search_arguments(self, registry):
        """Test hiding arguments in search field"""
        field = ModelSearchField(
            plural_model_name="Tests",
            model=MockModelOperationFields,
            registry=registry,
            modify_where_argument={"hidden": True},
            modify_order_by_argument={"hidden": True},
            modify_pagination_config_argument={"hidden": True},
        )

        assert "where" not in field.args
        assert "order_by" not in field.args
        assert "pagination_config" not in field.args
        assert len(field.args) == 0

    def test_modify_search_arguments_with_extra_arguments(self, registry):
        """Test combining modify arguments with extra_arguments in search field"""
        field = ModelSearchField(
            plural_model_name="Tests",
            model=MockModelOperationFields,
            registry=registry,
            modify_where_argument={"description": "Custom where"},
            **{"extra": graphene.Argument(graphene.String, name="extra")},
        )

        assert "where" in field.args
        assert "order_by" in field.args
        assert "pagination_config" in field.args
        assert "extra" in field.args
        assert field.args["where"].description == "Custom where"
