import pytest
import graphene
from graphene.test import Client

from graphene_cruddals.types.main import (
    construct_fields,
    ModelObjectType,
    ModelPaginatedObjectType, 
    ModelInputObjectType,
    ModelCreateInputObjectType, 
    ModelUpdateInputObjectType,
    ModelSearchInputObjectType,
    ModelOrderByInputObjectType
)
from graphene_cruddals.registry.registry_global import RegistryGlobal, get_global_registry


def mock_field_converter(field, registry):
    return graphene.String(description="Converted")

def mock_field_converter_to_field(field, registry):
    return graphene.Field(graphene.String, description="Converted")

def mock_field_converter_to_input_field(field, registry):
    return graphene.InputField(graphene.String, description="Converted")

# Sample model dictionary simulating fields of a Django model or similar
sample_model = {
    "id": int,
    "name": str,
    "active": bool
}



@pytest.fixture
def registry():
    return get_global_registry()


@pytest.mark.usefixtures("registry")
class TestConstructFields:
    def test_empty_model(self):
        fields = construct_fields({}, mock_field_converter, get_global_registry())
        assert fields == {}

    def test_full_inclusion_with_all(self):
        fields = construct_fields(sample_model, mock_field_converter, get_global_registry(), only_fields="__all__")
        assert list(fields.keys()) == ["id", "name", "active"]
    
    def test_full_inclusion_without_all(self):
        fields = construct_fields(sample_model, mock_field_converter, get_global_registry())
        assert list(fields.keys()) == ["id", "name", "active"]

    def test_partial_exclusion(self):
        fields = construct_fields(sample_model, mock_field_converter, get_global_registry(), exclude_fields=["id"])
        assert "id" not in fields
        assert list(fields.keys()) == ["name", "active"]

    def test_non_included_field(self):
        fields = construct_fields(sample_model, mock_field_converter, get_global_registry(), only_fields=["name"])
        assert list(fields.keys()) == ["name"]

class TestModelObjectType:
    
    def test_model_object_type_init(self, registry:RegistryGlobal):
        
        class TestModel(ModelObjectType):
            class Meta:
                model = sample_model
                field_converter_function = mock_field_converter    

        assert hasattr(TestModel, "_meta")
        assert TestModel._meta.model == sample_model
        assert TestModel._meta.fields.keys() == {"id", "name", "active"}
        registries_for_model = registry.get_registry_for_model(sample_model)
        assert 'object_type' in registries_for_model
        assert registries_for_model['object_type'] == TestModel
        
    def test_model_object_type_init_with_fields(self, registry:RegistryGlobal):
        class TestModel(ModelObjectType):
            class Meta:
                model = sample_model
                field_converter_function = mock_field_converter
                only_fields = ["id", "name"]
        assert hasattr(TestModel, "_meta")
        assert TestModel._meta.model == sample_model
        assert TestModel._meta.fields.keys() == {"id", "name"}
        registries_for_model = registry.get_registry_for_model(sample_model)
        assert 'object_type' in registries_for_model
        assert registries_for_model['object_type'] == TestModel
    
    def test_model_object_type_init_with_exclude_fields(self, registry:RegistryGlobal):
        class TestModel(ModelObjectType):
            class Meta:
                model = sample_model
                field_converter_function = mock_field_converter
                exclude_fields = ["id"]
        assert hasattr(TestModel, "_meta")
        assert TestModel._meta.model == sample_model
        assert TestModel._meta.fields.keys() == {"name", "active"}
        registries_for_model = registry.get_registry_for_model(sample_model)
        assert 'object_type' in registries_for_model
        assert registries_for_model['object_type'] == TestModel
    
    def test_model_object_type_init_with_field_converter(self, registry:RegistryGlobal):
        class TestModel(ModelObjectType):
            class Meta:
                model = sample_model
                field_converter_function = mock_field_converter_to_field
        assert hasattr(TestModel, "_meta")
        assert TestModel._meta.model == sample_model
        assert TestModel._meta.fields.keys() == {"id", "name", "active"}
        assert isinstance(TestModel._meta.fields["id"], graphene.Field)
        registries_for_model = registry.get_registry_for_model(sample_model)
        assert 'object_type' in registries_for_model
        assert registries_for_model['object_type'] == TestModel

    def test_model_object_type_init_with_fields_empty(self, registry:RegistryGlobal):
        class TestModel(ModelObjectType):
            class Meta:
                model = sample_model
                field_converter_function = mock_field_converter
                only_fields = []
        assert hasattr(TestModel, "_meta")
        assert TestModel._meta.model == sample_model
        assert TestModel._meta.fields.keys() == {}
        registries_for_model = registry.get_registry_for_model(sample_model)
        assert 'object_type' in registries_for_model
        assert registries_for_model['object_type'] == TestModel

    # def test_model_object_type_init_with_fields_and_exclude_fields(self, registry:RegistryGlobal):
    # def test_model_object_type_exclude_fields_type_checking
    # def test_model_object_type_only_fields_type_checking
    # def test_model_object_type_field_converter_type_checking
    # def test_model_object_type_field_converter_return_type_checking

    def test_schema(self):
        class SampleModelType(ModelObjectType):
            class Meta:
                model = sample_model
                field_converter_function = mock_field_converter

        schema = graphene.Schema(query=SampleModelType)
        expected = 'schema {\n  query: SampleModelType\n}\n\ntype SampleModelType {\n  """Converted"""\n  id: String\n\n  """Converted"""\n  name: String\n\n  """Converted"""\n  active: String\n}'
        assert str(schema) == expected

class TestModelPaginatedObjectType:

    def test_model_paginated_object_type_init(self, registry:RegistryGlobal):
        class SampleModelType(ModelObjectType):
            class Meta:
                model = sample_model

        class TestModelPaginated(ModelPaginatedObjectType):
            class Meta:
                model_object_type = SampleModelType
        
        assert hasattr(TestModelPaginated, "_meta")
        assert TestModelPaginated._meta.fields.keys() == {"objects", "total", "page", "pages", "has_next", "has_prev", "index_start", "index_end"}
        assert isinstance(TestModelPaginated._meta.fields["objects"].type, graphene.List)
        assert TestModelPaginated._meta.fields["objects"].type.of_type == SampleModelType
        assert TestModelPaginated._meta.fields["total"].type == graphene.Int
        assert TestModelPaginated._meta.fields["page"].type == graphene.Int
        assert TestModelPaginated._meta.fields["pages"].type == graphene.Int
        assert TestModelPaginated._meta.fields["has_next"].type == graphene.Boolean
        assert TestModelPaginated._meta.fields["has_prev"].type == graphene.Boolean
        assert TestModelPaginated._meta.fields["index_start"].type == graphene.Int
        assert TestModelPaginated._meta.fields["index_end"].type == graphene.Int

        registries_for_model = registry.get_registry_for_model(sample_model)
        assert 'paginated_object_type' in registries_for_model
        assert registries_for_model['paginated_object_type'] == TestModelPaginated

    def test_schema(self):
        class SampleModelType(ModelObjectType):
            class Meta:
                model = sample_model

        class TestModelPaginated(ModelPaginatedObjectType):
            class Meta:
                model_object_type = SampleModelType
        
        schema = graphene.Schema(query=TestModelPaginated)
        expected = 'schema {\n  query: TestModelPaginated\n}\n\ntype TestModelPaginated implements PaginationInterface {\n  objects: [SampleModelType]\n  total: Int\n  page: Int\n  pages: Int\n  hasNext: Boolean\n  hasPrev: Boolean\n  indexStart: Int\n  indexEnd: Int\n}\n\n"""Defines a GraphQL Interface for pagination-related attributes."""\ninterface PaginationInterface {\n  total: Int\n  page: Int\n  pages: Int\n  hasNext: Boolean\n  hasPrev: Boolean\n  indexStart: Int\n  indexEnd: Int\n}\n\ntype SampleModelType {\n  id: String\n  name: String\n  active: String\n}'
        assert str(schema) == expected

class TestModelInputObjectType:
    
    def test_model_input_object_type_init_without_type_mutation(self, registry:RegistryGlobal):
        class TestModelInput(ModelInputObjectType):
            class Meta:
                model = sample_model
                field_converter_function = mock_field_converter

        print(TestModelInput)

        # assert hasattr(TestModelInput, "_meta")
        # assert TestModelInput._meta.fields.keys() == {"id", "name", "active"}
        # assert isinstance(TestModelInput._meta.fields["id"], graphene.InputField)
        # assert isinstance(TestModelInput._meta.fields["name"], graphene.InputField)
        # assert isinstance(TestModelInput._meta.fields["active"], graphene.InputField)

        # registries_for_model = registry.get_registry_for_model(sample_model)
        # assert 'input_object_type' in registries_for_model
        # assert registries_for_model['input_object_type'] == TestModelInput

    def test_schema(self):
        class TestModelInput(ModelInputObjectType):
            class Meta:
                model = sample_model
                type_mutation = "create"
                field_converter_function = mock_field_converter_to_input_field

        print(TestModelInput)

