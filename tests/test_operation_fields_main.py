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
