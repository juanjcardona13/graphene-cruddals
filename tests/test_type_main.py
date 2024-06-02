import pytest

import graphene
from graphene_cruddals.registry.registry_global import (
    RegistryGlobal,
    get_global_registry,
)
from graphene_cruddals.types.main import (
    ModelInputObjectType,
    ModelObjectType,
    ModelOrderByInputObjectType,
    ModelPaginatedObjectType,
    ModelSearchInputObjectType,
    construct_fields,
)


def mock_field_converter(name, field, model, registry):
    return graphene.String(description="Converted")


def mock_field_converter_to_field(name, field, model, registry):
    return graphene.Field(graphene.String, description="Converted")


def mock_field_converter_to_input_field(name, field, model, registry):
    return graphene.InputField(graphene.String, description="Converted")


def mock_get_fields(cls):
    try:
        return cls.__annotations__
    except AttributeError:
        return {
            name: field
            for name, field in cls.__dict__.items()
            if not name.startswith("__") and not callable(field)
        }


class SampleModel:
    id: int
    name: str
    active: bool
    sample: str


@pytest.fixture
def registry():
    return get_global_registry()


@pytest.mark.usefixtures("registry")
class TestConstructFields:
    def test_empty_model(self):
        class ModelEmpty:
            pass

        fields = construct_fields(
            ModelEmpty, mock_get_fields, mock_field_converter, get_global_registry()
        )
        assert fields == {}

    def test_full_inclusion_with_all(self):
        fields = construct_fields(
            SampleModel,
            mock_get_fields,
            mock_field_converter,
            get_global_registry(),
            only_fields="__all__",
        )
        assert list(fields.keys()) == ["id", "name", "active", "sample"]

    def test_full_inclusion_without_all(self):
        fields = construct_fields(
            SampleModel, mock_get_fields, mock_field_converter, get_global_registry()
        )
        assert list(fields.keys()) == ["id", "name", "active", "sample"]

    def test_partial_exclusion(self):
        fields = construct_fields(
            SampleModel,
            mock_get_fields,
            mock_field_converter,
            get_global_registry(),
            exclude_fields=["id"],
        )
        assert "id" not in fields
        assert list(fields.keys()) == ["name", "active", "sample"]

    def test_non_included_field(self):
        fields = construct_fields(
            SampleModel,
            mock_get_fields,
            mock_field_converter,
            get_global_registry(),
            only_fields=["name"],
        )
        assert list(fields.keys()) == ["name"]


class TestModelObjectType:
    def test_model_object_type_init(self, registry: RegistryGlobal):
        class TestModel(ModelObjectType):
            class Meta:
                model = SampleModel
                field_converter_function = mock_field_converter

        assert hasattr(TestModel, "_meta")
        assert TestModel._meta.model == SampleModel
        assert TestModel._meta.fields.keys() == {"id", "name", "active", "sample"}
        assert isinstance(TestModel._meta.fields["id"], graphene.Field)
        assert isinstance(TestModel._meta.fields["name"], graphene.Field)
        assert isinstance(TestModel._meta.fields["active"], graphene.Field)
        assert isinstance(TestModel._meta.fields["sample"], graphene.Field)
        registries_for_model = registry.get_registry_for_model(SampleModel)
        assert "object_type" in registries_for_model
        assert registries_for_model["object_type"] == TestModel

    def test_model_object_type_init_with_fields(self, registry: RegistryGlobal):
        class TestModel(ModelObjectType):
            class Meta:
                model = SampleModel
                field_converter_function = mock_field_converter
                only_fields = ["id", "name"]

        assert hasattr(TestModel, "_meta")
        assert TestModel._meta.model == SampleModel
        assert TestModel._meta.fields.keys() == {"id", "name"}
        registries_for_model = registry.get_registry_for_model(SampleModel)
        assert "object_type" in registries_for_model
        assert registries_for_model["object_type"] == TestModel

    def test_model_object_type_init_with_exclude_fields(self, registry: RegistryGlobal):
        class TestModel(ModelObjectType):
            class Meta:
                model = SampleModel
                field_converter_function = mock_field_converter
                exclude_fields = ["id"]

        assert hasattr(TestModel, "_meta")
        assert TestModel._meta.model == SampleModel
        assert TestModel._meta.fields.keys() == {"name", "active", "sample"}
        registries_for_model = registry.get_registry_for_model(SampleModel)
        assert "object_type" in registries_for_model
        assert registries_for_model["object_type"] == TestModel

    def test_model_object_type_init_with_field_converter(
        self, registry: RegistryGlobal
    ):
        class TestModel(ModelObjectType):
            class Meta:
                model = SampleModel
                field_converter_function = mock_field_converter_to_field

        assert hasattr(TestModel, "_meta")
        assert TestModel._meta.model == SampleModel
        assert TestModel._meta.fields.keys() == {"id", "name", "active", "sample"}
        assert isinstance(TestModel._meta.fields["id"], graphene.Field)
        registries_for_model = registry.get_registry_for_model(SampleModel)
        assert "object_type" in registries_for_model
        assert registries_for_model["object_type"] == TestModel

    def test_model_object_type_init_with_fields_empty(self, registry: RegistryGlobal):
        class TestModel(ModelObjectType):
            class Meta:
                model = SampleModel
                field_converter_function = mock_field_converter
                only_fields = []

        assert hasattr(TestModel, "_meta")
        assert TestModel._meta.model == SampleModel
        assert list(TestModel._meta.fields.keys()) == []
        registries_for_model = registry.get_registry_for_model(SampleModel)
        assert "object_type" in registries_for_model
        assert registries_for_model["object_type"] == TestModel

    # def test_model_object_type_init_with_fields_and_exclude_fields(self, registry:RegistryGlobal):
    # def test_model_object_type_exclude_fields_type_checking
    # def test_model_object_type_only_fields_type_checking
    # def test_model_object_type_field_converter_type_checking
    # def test_model_object_type_field_converter_return_type_checking

    def test_schema(self):
        class SampleModelType(ModelObjectType):
            class Meta:
                model = SampleModel
                field_converter_function = mock_field_converter

        schema = graphene.Schema(query=SampleModelType)
        expected = 'schema {\n  query: SampleModelType\n}\n\ntype SampleModelType {\n  """Converted"""\n  id: String\n\n  """Converted"""\n  name: String\n\n  """Converted"""\n  active: String\n\n  """Converted"""\n  sample: String\n}'
        assert str(schema).strip() == expected.strip()


class TestModelPaginatedObjectType:
    def test_model_paginated_object_type_init(self, registry: RegistryGlobal):
        class SampleModelType(ModelObjectType):
            class Meta:
                model = SampleModel

        class TestModelPaginated(ModelPaginatedObjectType):
            class Meta:
                model_object_type = SampleModelType

        assert hasattr(TestModelPaginated, "_meta")
        assert TestModelPaginated._meta.fields.keys() == {
            "objects",
            "total",
            "page",
            "pages",
            "has_next",
            "has_prev",
            "index_start",
            "index_end",
        }
        assert isinstance(
            TestModelPaginated._meta.fields["objects"].type, graphene.List
        )
        assert (
            TestModelPaginated._meta.fields["objects"].type.of_type == SampleModelType
        )
        assert TestModelPaginated._meta.fields["total"].type == graphene.Int
        assert TestModelPaginated._meta.fields["page"].type == graphene.Int
        assert TestModelPaginated._meta.fields["pages"].type == graphene.Int
        assert TestModelPaginated._meta.fields["has_next"].type == graphene.Boolean
        assert TestModelPaginated._meta.fields["has_prev"].type == graphene.Boolean
        assert TestModelPaginated._meta.fields["index_start"].type == graphene.Int
        assert TestModelPaginated._meta.fields["index_end"].type == graphene.Int

        registries_for_model = registry.get_registry_for_model(SampleModel)
        assert "paginated_object_type" in registries_for_model
        assert registries_for_model["paginated_object_type"] == TestModelPaginated

    def test_schema(self):
        class SampleModelType(ModelObjectType):
            class Meta:
                model = SampleModel

        class TestModelPaginated(ModelPaginatedObjectType):
            class Meta:
                model_object_type = SampleModelType

        schema = graphene.Schema(query=TestModelPaginated)
        expected = 'schema {\n  query: TestModelPaginated\n}\n\ntype TestModelPaginated implements PaginationInterface {\n  objects: [SampleModelType]\n  total: Int\n  page: Int\n  pages: Int\n  hasNext: Boolean\n  hasPrev: Boolean\n  indexStart: Int\n  indexEnd: Int\n}\n\n"""Defines a GraphQL Interface for pagination-related attributes."""\ninterface PaginationInterface {\n  total: Int\n  page: Int\n  pages: Int\n  hasNext: Boolean\n  hasPrev: Boolean\n  indexStart: Int\n  indexEnd: Int\n}\n\ntype SampleModelType {\n  id: String\n  name: String\n  active: String\n  sample: String\n}'
        assert str(schema).strip() == expected.strip()


class TestModelInputObjectType:
    def test_model_input_object_type_init_without_type_mutation(
        self, registry: RegistryGlobal
    ):
        class TestModelInput(ModelInputObjectType):
            class Meta:
                model = SampleModel
                field_converter_function = mock_field_converter

        assert hasattr(TestModelInput, "_meta")
        assert list(TestModelInput._meta.fields.keys()) == [
            "id",
            "name",
            "active",
            "sample",
        ]
        assert isinstance(TestModelInput._meta.fields["id"], graphene.InputField)
        assert isinstance(TestModelInput._meta.fields["name"], graphene.InputField)
        assert isinstance(TestModelInput._meta.fields["active"], graphene.InputField)
        assert isinstance(TestModelInput._meta.fields["sample"], graphene.InputField)
        registries_for_model = registry.get_registry_for_model(SampleModel)
        assert "input_object_type" in registries_for_model
        assert registries_for_model["input_object_type"] == TestModelInput

    def test_model_input_object_type_init_with_type_mutation_create(
        self, registry: RegistryGlobal
    ):
        class TestModelInput(ModelInputObjectType):
            class Meta:
                model = SampleModel
                type_mutation = "create"
                field_converter_function = mock_field_converter

        assert hasattr(TestModelInput, "_meta")
        assert list(TestModelInput._meta.fields.keys()) == [
            "id",
            "name",
            "active",
            "sample",
        ]
        assert isinstance(TestModelInput._meta.fields["id"], graphene.InputField)
        assert isinstance(TestModelInput._meta.fields["name"], graphene.InputField)
        assert isinstance(TestModelInput._meta.fields["active"], graphene.InputField)
        assert isinstance(TestModelInput._meta.fields["sample"], graphene.InputField)
        assert TestModelInput._meta.name == "CreateTestModelInput"
        registries_for_model = registry.get_registry_for_model(SampleModel)
        assert "input_object_type_for_create" in registries_for_model
        assert registries_for_model["input_object_type_for_create"] == TestModelInput

    def test_model_input_object_type_init_with_type_mutation_update(
        self, registry: RegistryGlobal
    ):
        class TestModelInput(ModelInputObjectType):
            class Meta:
                model = SampleModel
                type_mutation = "update"
                field_converter_function = mock_field_converter

        assert hasattr(TestModelInput, "_meta")
        assert list(TestModelInput._meta.fields.keys()) == [
            "id",
            "name",
            "active",
            "sample",
        ]
        assert isinstance(TestModelInput._meta.fields["id"], graphene.InputField)
        assert isinstance(TestModelInput._meta.fields["name"], graphene.InputField)
        assert isinstance(TestModelInput._meta.fields["active"], graphene.InputField)
        assert isinstance(TestModelInput._meta.fields["sample"], graphene.InputField)
        assert TestModelInput._meta.name == "UpdateTestModelInput"
        registries_for_model = registry.get_registry_for_model(SampleModel)
        assert "input_object_type_for_update" in registries_for_model
        assert registries_for_model["input_object_type_for_update"] == TestModelInput

    def test_model_input_object_type_init_with_fields(self, registry: RegistryGlobal):
        class TestModelInput(ModelInputObjectType):
            class Meta:
                model = SampleModel
                field_converter_function = mock_field_converter
                only_fields = ["id", "name"]

        assert hasattr(TestModelInput, "_meta")
        assert list(TestModelInput._meta.fields.keys()) == ["id", "name"]
        registries_for_model = registry.get_registry_for_model(SampleModel)
        assert "input_object_type" in registries_for_model
        assert registries_for_model["input_object_type"] == TestModelInput

    def test_model_input_object_type_init_with_exclude_fields(
        self, registry: RegistryGlobal
    ):
        class TestModelInput(ModelInputObjectType):
            class Meta:
                model = SampleModel
                field_converter_function = mock_field_converter
                exclude_fields = ["id"]

        assert hasattr(TestModelInput, "_meta")
        assert list(TestModelInput._meta.fields.keys()) == ["name", "active", "sample"]
        registries_for_model = registry.get_registry_for_model(SampleModel)
        assert "input_object_type" in registries_for_model
        assert registries_for_model["input_object_type"] == TestModelInput

    def test_model_input_object_type_init_with_field_converter(
        self, registry: RegistryGlobal
    ):
        class TestModelInput(ModelInputObjectType):
            class Meta:
                model = SampleModel
                field_converter_function = mock_field_converter_to_input_field

        assert hasattr(TestModelInput, "_meta")
        assert list(TestModelInput._meta.fields.keys()) == [
            "id",
            "name",
            "active",
            "sample",
        ]
        assert isinstance(TestModelInput._meta.fields["id"], graphene.InputField)
        registries_for_model = registry.get_registry_for_model(SampleModel)
        assert "input_object_type" in registries_for_model
        assert registries_for_model["input_object_type"] == TestModelInput

    def test_model_input_object_type_init_with_fields_empty(
        self, registry: RegistryGlobal
    ):
        class TestModelInput(ModelInputObjectType):
            class Meta:
                model = SampleModel
                field_converter_function = mock_field_converter
                only_fields = []

        assert hasattr(TestModelInput, "_meta")
        assert list(TestModelInput._meta.fields.keys()) == []
        registries_for_model = registry.get_registry_for_model(SampleModel)
        assert "input_object_type" in registries_for_model
        assert registries_for_model["input_object_type"] == TestModelInput

    # def test_model_input_object_type_init_with_fields_and_exclude_fields(self, registry:RegistryGlobal):
    # def test_model_input_object_type_exclude_fields_type_checking
    # def test_model_input_object_type_only_fields_type_checking
    # def test_model_input_object_type_field_converter_type_checking
    # def test_model_input_object_type_field_converter_return_type_checking


class TestModelSearchInputObjectType:
    def test_model_search_input_object_type_init(self, registry: RegistryGlobal):
        class TestModelSearchInput(ModelSearchInputObjectType):
            class Meta:
                model = SampleModel
                field_converter_function = mock_field_converter

        assert hasattr(TestModelSearchInput, "_meta")
        assert list(TestModelSearchInput._meta.fields.keys()) == [
            "id",
            "name",
            "active",
            "sample",
            "AND",
            "OR",
            "NOT",
        ]
        assert isinstance(TestModelSearchInput._meta.fields["id"], graphene.InputField)
        assert isinstance(
            TestModelSearchInput._meta.fields["name"], graphene.InputField
        )
        assert isinstance(
            TestModelSearchInput._meta.fields["active"], graphene.InputField
        )
        assert isinstance(
            TestModelSearchInput._meta.fields["sample"], graphene.InputField
        )
        assert isinstance(TestModelSearchInput._meta.fields["AND"], graphene.Dynamic)
        assert isinstance(TestModelSearchInput._meta.fields["OR"], graphene.Dynamic)
        assert isinstance(TestModelSearchInput._meta.fields["NOT"], graphene.Dynamic)
        registries_for_model = registry.get_registry_for_model(SampleModel)
        assert "input_object_type_for_search" in registries_for_model
        assert (
            registries_for_model["input_object_type_for_search"] == TestModelSearchInput
        )

    def test_model_search_input_object_type_init_with_fields(
        self, registry: RegistryGlobal
    ):
        class TestModelSearchInput(ModelSearchInputObjectType):
            class Meta:
                model = SampleModel
                field_converter_function = mock_field_converter
                only_fields = ["id", "name"]

        assert hasattr(TestModelSearchInput, "_meta")
        assert list(TestModelSearchInput._meta.fields.keys()) == [
            "id",
            "name",
            "AND",
            "OR",
            "NOT",
        ]
        registries_for_model = registry.get_registry_for_model(SampleModel)
        assert "input_object_type_for_search" in registries_for_model
        assert (
            registries_for_model["input_object_type_for_search"] == TestModelSearchInput
        )

    def test_model_search_input_object_type_init_with_exclude_fields(
        self, registry: RegistryGlobal
    ):
        class TestModelSearchInput(ModelSearchInputObjectType):
            class Meta:
                model = SampleModel
                field_converter_function = mock_field_converter
                exclude_fields = ["id"]

        assert hasattr(TestModelSearchInput, "_meta")
        assert list(TestModelSearchInput._meta.fields.keys()) == [
            "name",
            "active",
            "sample",
            "AND",
            "OR",
            "NOT",
        ]
        registries_for_model = registry.get_registry_for_model(SampleModel)
        assert "input_object_type_for_search" in registries_for_model
        assert (
            registries_for_model["input_object_type_for_search"] == TestModelSearchInput
        )

    # def test_model_search_input_object_type_init_with_fields_and_exclude_fields(self, registry:RegistryGlobal):
    # def test_model_search_input_object_type_exclude_fields_type_checking
    # def test_model_search_input_object_type_only_fields_type_checking
    # def test_model_search_input_object_type_field_converter_type_checking
    # def test_model_search_input_object_type_field_converter_return_type_checking


class TestModelOrderByInputObjectType:
    def test_model_order_by_input_object_type_init(self, registry: RegistryGlobal):
        class TestModelOrderByInput(ModelOrderByInputObjectType):
            class Meta:
                model = SampleModel
                field_converter_function = mock_field_converter

        assert hasattr(TestModelOrderByInput, "_meta")
        assert list(TestModelOrderByInput._meta.fields.keys()) == [
            "id",
            "name",
            "active",
            "sample",
        ]
        assert isinstance(TestModelOrderByInput._meta.fields["id"], graphene.InputField)
        assert isinstance(
            TestModelOrderByInput._meta.fields["name"], graphene.InputField
        )
        assert isinstance(
            TestModelOrderByInput._meta.fields["active"], graphene.InputField
        )
        assert isinstance(
            TestModelOrderByInput._meta.fields["sample"], graphene.InputField
        )
        registries_for_model = registry.get_registry_for_model(SampleModel)
        assert "input_object_type_for_order_by" in registries_for_model
        assert (
            registries_for_model["input_object_type_for_order_by"]
            == TestModelOrderByInput
        )

    def test_model_order_by_input_object_type_init_with_fields(
        self, registry: RegistryGlobal
    ):
        class TestModelOrderByInput(ModelOrderByInputObjectType):
            class Meta:
                model = SampleModel
                field_converter_function = mock_field_converter
                only_fields = ["id", "name"]

        assert hasattr(TestModelOrderByInput, "_meta")
        assert list(TestModelOrderByInput._meta.fields.keys()) == ["id", "name"]
        registries_for_model = registry.get_registry_for_model(SampleModel)
        assert "input_object_type_for_order_by" in registries_for_model
        assert (
            registries_for_model["input_object_type_for_order_by"]
            == TestModelOrderByInput
        )

    def test_model_order_by_input_object_type_init_with_exclude_fields(
        self, registry: RegistryGlobal
    ):
        class TestModelOrderByInput(ModelOrderByInputObjectType):
            class Meta:
                model = SampleModel
                field_converter_function = mock_field_converter
                exclude_fields = ["id"]

        assert hasattr(TestModelOrderByInput, "_meta")
        assert list(TestModelOrderByInput._meta.fields.keys()) == [
            "name",
            "active",
            "sample",
        ]
        registries_for_model = registry.get_registry_for_model(SampleModel)
        assert "input_object_type_for_order_by" in registries_for_model
        assert (
            registries_for_model["input_object_type_for_order_by"]
            == TestModelOrderByInput
        )

    # def test_model_order_by_input_object_type_init_with_fields_and_exclude_fields(self, registry:RegistryGlobal):
    # def test_model_order_by_input_object_type_exclude_fields_type_checking
    # def test_model_order_by_input_object_type_only_fields_type_checking
    # def test_model_order_by_input_object_type_field_converter_type_checking
    # def test_model_order_by_input_object_type_field_converter_return_type_checking
