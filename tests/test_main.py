import pytest

import graphene
from graphene_cruddals.main import (
    BaseCruddals,
    BuilderCruddalsModel,
    CruddalsBuilderConfig,
)
from graphene_cruddals.operation_fields.main import (
    ModelActivateField,
    ModelCreateUpdateField,
    ModelDeactivateField,
    ModelDeleteField,
    ModelListField,
    ModelReadField,
    ModelSearchField,
)
from graphene_cruddals.registry.registry_global import RegistryGlobal
from graphene_cruddals.types.main import (
    ModelInputObjectType,
    ModelObjectType,
    ModelOrderByInputObjectType,
    ModelPaginatedObjectType,
    ModelSearchInputObjectType,
)
from graphene_cruddals.utils.main import build_class
from graphene_cruddals.utils.typing.custom_typing import GRAPHENE_TYPE

mock_database = [
    {"id": 1, "name": "test1", "active": True},
    {"id": 2, "name": "test2", "active": False},
    {"id": 3, "name": "test3", "active": True},
]


class MockModel:
    id: int
    name: str
    active: bool


class Model:
    id: int


def mock_resolver_create_models(root, info, **kwargs):
    if "input" in kwargs:
        list_models = kwargs.get("input", [])
        for model in list_models:
            model["id"] = len(mock_database) + 1
            mock_database.append(model)
    return {"objects": mock_database}


def mock_resolver_read_models(root, info, **kwargs):
    if "where" in kwargs:
        where = kwargs.get("where", {})
        for model in mock_database:
            if model.get("id") == where.get("id"):
                return model
    return None


def mock_resolver_update_models(root, info, **kwargs):
    if "input" in kwargs:
        list_models = kwargs.get("input", [])
        for model in list_models:
            for i, db_model in enumerate(mock_database):
                if model.get("id") == db_model.get("id"):
                    mock_database[i] = model
    return {"objects": mock_database}


def mock_resolver_delete_models(root, info, **kwargs):
    if "where" in kwargs:
        where = kwargs.get("where", {})
        for i, model in enumerate(mock_database):
            if model.get("id") == where.get("id"):
                mock_database.pop(i)
    return {"objects": mock_database}


def mock_resolver_deactivate_models(root, info, **kwargs):
    if "where" in kwargs:
        where = kwargs.get("where", {})
        for model in mock_database:
            if model.get("id") == where.get("id"):
                model["active"] = False
    return {"objects": mock_database}


def mock_resolver_activate_models(root, info, **kwargs):
    if "where" in kwargs:
        where = kwargs.get("where", {})
        for model in mock_database:
            if model.get("id") == where.get("id"):
                model["active"] = True
    return {"objects": mock_database}


def mock_resolver_list_models(root, info, **kwargs):
    return mock_database


def mock_resolver_search_models(root, info, **kwargs):
    return {"total": len(mock_database), "objects": mock_database}


class InterfaceO11:
    """ObjectType With Meta OnlyFields"""

    class ObjectType:
        class Meta:
            only_fields = ("id",)


class InterfaceO12:
    """ObjectType With Meta ExcludeFields"""

    class ObjectType:
        class Meta:
            exclude_fields = ("id",)


class InterfaceO13:
    """ObjectType With Extra Field"""

    class ObjectType:
        extra_field_1 = graphene.String()

        @staticmethod
        def resolve_extra_field_1(root, info):
            return "extra_field"


class InterfaceO14:
    """ObjectType With Extra Field Override"""

    class ObjectType:
        active = graphene.Int()


class InterfaceO21:
    """ObjectType With Meta OnlyFields"""

    class ObjectType:
        class Meta:
            only_fields = ("name",)


class InterfaceO22:
    """ObjectType With Meta ExcludeFields"""

    class ObjectType:
        class Meta:
            exclude_fields = ("name",)


class InterfaceO23:
    """ObjectType With Extra Field"""

    class ObjectType:
        extra_field_2 = graphene.String()

        @staticmethod
        def resolve_extra_field_2(root, info):
            return "extra_field"


class InterfaceO24:
    """ObjectType With Extra Field Override"""

    class ObjectType:
        active = graphene.Int()


class Interface5:
    """Input ObjectType With MetaOnlyFields"""

    class InputObjectType:
        class Meta:
            only_fields = ("id", "name")


class Interface6:
    """Input ObjectType With MetaExcludeFields"""

    class InputObjectType:
        class Meta:
            exclude_fields = ("id", "name")


class Interface7:
    """Input ObjectType With ExtraArguments"""

    class InputObjectType:
        extra_argument = graphene.String()


class Interface8:
    """Input ObjectType With ExtraArgumentsOverride"""

    class InputObjectType:
        active = graphene.Int()


class Interface9:
    """CreateInputObjectTypeWithMetaOnlyFields"""

    class CreateInputObjectType:
        class Meta:
            only_fields = ("id", "name")


class Interface10:
    """CreateInputObjectTypeWithMetaExcludeFields"""

    class CreateInputObjectType:
        class Meta:
            exclude_fields = ("id", "name")


class Interface11:
    """CreateInputObjectTypeWithExtraArguments"""

    class CreateInputObjectType:
        extra_argument = graphene.String()


class Interface12:
    """CreateInputObjectTypeWithExtraArgumentsOverride"""

    class CreateInputObjectType:
        active = graphene.Int()


class Interface13:
    """UpdateInputObjectTypeWithMetaOnlyFields"""

    class UpdateInputObjectType:
        class Meta:
            only_fields = ("id", "name")


class Interface14:
    """UpdateInputObjectTypeWithMetaExcludeFields"""

    class UpdateInputObjectType:
        class Meta:
            exclude_fields = ("id", "name")


class Interface15:
    """UpdateInputObjectTypeWithExtraArguments"""

    class UpdateInputObjectType:
        extra_argument = graphene.String()


class Interface16:
    """UpdateInputObjectTypeWithExtraArgumentsOverride"""

    class UpdateInputObjectType:
        active = graphene.Int()


class Interface17:
    """SearchInputObjectTypeWithMetaOnlyFields"""

    class SearchInputObjectType:
        class Meta:
            only_fields = ("id", "name")


class Interface18:
    """SearchInputObjectTypeWithMetaExcludeFields"""

    class SearchInputObjectType:
        class Meta:
            exclude_fields = ("id", "name")


class Interface19:
    """SearchInputObjectTypeWithExtraArguments"""

    class SearchInputObjectType:
        extra_argument = graphene.String()


class Interface20:
    """SearchInputObjectTypeWithExtraArgumentsOverride"""

    class SearchInputObjectType:
        active = graphene.Int()


class Interface21:
    """OrderByInputObjectTypeWithMetaOnlyFields"""

    class OrderByInputObjectType:
        class Meta:
            only_fields = ("id", "name")


class Interface22:
    """OrderByInputObjectTypeWithMetaExcludeFields"""

    class OrderByInputObjectType:
        class Meta:
            exclude_fields = ("id", "name")


class Interface23:
    """OrderByInputObjectTypeWithExtraArguments"""

    class OrderByInputObjectType:
        extra_argument = graphene.String()


class Interface24:
    """OrderByInputObjectTypeWithExtraArgumentsOverride"""

    class OrderByInputObjectType:
        active = graphene.Int()


class Interface25:
    """ModelCreateField With MetaArguments"""

    class ModelCreateField:
        class Meta:
            arguments = {"extra_create_argument": graphene.String()}


class Interface26:
    """ModelCreateField With PreMutate"""

    class ModelCreateField:
        @staticmethod
        def pre_mutate(root, info, **kwargs):
            return (root, info, kwargs)


class Interface27:
    """ModelCreateField With PostMutate"""

    class ModelCreateField:
        @staticmethod
        def post_mutate(root, info, **kwargs):
            return kwargs.get("CRUDDALS_RESPONSE", None)


class Interface28:
    """ModelCreateField With Mutate"""

    class ModelCreateField:
        @staticmethod
        def mutate(root, info, **kwargs):
            return kwargs.get("CRUDDALS_RESPONSE", None)


class Interface29:
    """ModelCreateField With OverrideTotalMutate"""

    class ModelCreateField:
        @staticmethod
        def override_total_mutate(root, info, **kwargs):
            return []


class Interface30:
    """ReadField With MetaArguments"""

    class ReadField:
        class Meta:
            arguments = {"extra_read_argument": graphene.String()}


class Interface31:
    """Read Field With PreResolver"""

    class ReadField:
        @staticmethod
        def pre_resolver(root, info, **kwargs):
            return (root, info, kwargs)


class Interface32:
    """ReadField With PostResolver"""

    class ReadField:
        @staticmethod
        def post_resolver(root, info, **kwargs):
            return kwargs.get("CRUDDALS_RESPONSE", None)


class Interface33:
    """ReadField With Resolver"""

    class ReadField:
        @staticmethod
        def resolver(root, info, **kwargs):
            return kwargs.get("CRUDDALS_RESPONSE", None)


class Interface34:
    """ReadField With OverrideTotalResolver"""

    class ReadField:
        @staticmethod
        def override_total_resolver(root, info, **kwargs):
            return {}


class Interface35:
    """ModelUpdateField With MetaArguments"""

    class ModelUpdateField:
        class Meta:
            arguments = {"extra_create_argument": graphene.String()}


class Interface36:
    """ModelUpdateField With PreMutate"""

    class ModelUpdateField:
        @staticmethod
        def pre_mutate(root, info, **kwargs):
            return (root, info, kwargs)


class Interface37:
    """ModelUpdateField With PostMutate"""

    class ModelUpdateField:
        @staticmethod
        def post_mutate(root, info, **kwargs):
            return kwargs.get("CRUDDALS_RESPONSE", None)


class Interface38:
    """ModelUpdateField With Mutate"""

    class ModelUpdateField:
        @staticmethod
        def mutate(root, info, **kwargs):
            return kwargs.get("CRUDDALS_RESPONSE", None)


class Interface39:
    """ModelUpdateField With OverrideTotalMutate"""

    class ModelUpdateField:
        @staticmethod
        def override_total_mutate(root, info, **kwargs):
            return []


class Interface40:
    """DeleteField With MetaArguments"""

    class DeleteField:
        class Meta:
            arguments = {"extra_create_argument": graphene.String()}


class Interface41:
    """DeleteField With PreMutate"""

    class DeleteField:
        @staticmethod
        def pre_mutate(root, info, **kwargs):
            return (root, info, kwargs)


class Interface42:
    """DeleteField With PostMutate"""

    class DeleteField:
        @staticmethod
        def post_mutate(root, info, **kwargs):
            return kwargs.get("CRUDDALS_RESPONSE", None)


class Interface43:
    """DeleteField With Mutate"""

    class DeleteField:
        @staticmethod
        def mutate(root, info, **kwargs):
            return kwargs.get("CRUDDALS_RESPONSE", None)


class Interface44:
    """DeleteField With OverrideTotalMutate"""

    class DeleteField:
        @staticmethod
        def override_total_mutate(root, info, **kwargs):
            return []


class Interface45:
    """DeactivateField With MetaArguments"""

    class DeactivateField:
        class Meta:
            arguments = {"extra_create_argument": graphene.String()}


class Interface46:
    """DeactivateField With PreMutate"""

    class DeactivateField:
        @staticmethod
        def pre_mutate(root, info, **kwargs):
            return (root, info, kwargs)


class Interface47:
    """DeactivateField With PostMutate"""

    class DeactivateField:
        @staticmethod
        def post_mutate(root, info, **kwargs):
            return kwargs.get("CRUDDALS_RESPONSE", None)


class Interface48:
    """DeactivateField With Mutate"""

    class DeactivateField:
        @staticmethod
        def mutate(root, info, **kwargs):
            return kwargs.get("CRUDDALS_RESPONSE", None)


class Interface49:
    """DeactivateField With OverrideTotalMutate"""

    class DeactivateField:
        @staticmethod
        def override_total_mutate(root, info, **kwargs):
            return []


class Interface50:
    """ActivateField With MetaArguments"""

    class ActivateField:
        class Meta:
            arguments = {"extra_create_argument": graphene.String()}


class Interface51:
    """ActivateField With PreMutate"""

    class ActivateField:
        @staticmethod
        def pre_mutate(root, info, **kwargs):
            return (root, info, kwargs)


class Interface52:
    """ActivateField With PostMutate"""

    class ActivateField:
        @staticmethod
        def post_mutate(root, info, **kwargs):
            return kwargs.get("CRUDDALS_RESPONSE", None)


class Interface53:
    """ActivateField With Mutate"""

    class ActivateField:
        @staticmethod
        def mutate(root, info, **kwargs):
            return kwargs.get("CRUDDALS_RESPONSE", None)


class Interface54:
    """ActivateField With OverrideTotalMutate"""

    class ActivateField:
        @staticmethod
        def override_total_mutate(root, info, **kwargs):
            return []


class Interface55:
    """ListField With MetaArguments"""

    class ReadField:
        class Meta:
            arguments = {"extra_read_argument": graphene.String()}


class Interface56:
    """List Field With PreResolver"""

    class ReadField:
        @staticmethod
        def pre_resolver(root, info, **kwargs):
            return (root, info, kwargs)


class Interface57:
    """ListField With PostResolver"""

    class ReadField:
        @staticmethod
        def post_resolver(root, info, **kwargs):
            return kwargs.get("CRUDDALS_RESPONSE", None)


class Interface58:
    """ListField With Resolver"""

    class ReadField:
        @staticmethod
        def resolver(root, info, **kwargs):
            return kwargs.get("CRUDDALS_RESPONSE", None)


class Interface59:
    """ListField With OverrideTotalResolver"""

    class ReadField:
        @staticmethod
        def override_total_resolver(root, info, **kwargs):
            return {}


class Interface60:
    """SearchField With MetaArguments"""

    class ReadField:
        class Meta:
            arguments = {"extra_read_argument": graphene.String()}


class Interface61:
    """SearchField With PreResolver"""

    class ReadField:
        @staticmethod
        def pre_resolver(root, info, **kwargs):
            return (root, info, kwargs)


class Interface62:
    """SearchField With PostResolver"""

    class ReadField:
        @staticmethod
        def post_resolver(root, info, **kwargs):
            return kwargs.get("CRUDDALS_RESPONSE", None)


class Interface63:
    """SearchField With Resolver"""

    class ReadField:
        @staticmethod
        def resolver(root, info, **kwargs):
            return kwargs.get("CRUDDALS_RESPONSE", None)


class Interface64:
    """SearchField With OverrideTotalResolver"""

    class ReadField:
        @staticmethod
        def override_total_resolver(root, info, **kwargs):
            return {}


def mock_converter_field_function(
    name: str, field, model, registry: RegistryGlobal
) -> GRAPHENE_TYPE:
    if field == int:
        return graphene.Int()
    elif field == str:
        return graphene.String()
    elif field == bool:
        return graphene.Boolean()
    return graphene.String()


def mock_get_fields(cls):
    try:
        return cls.__annotations__
    except AttributeError:
        return {
            name: field
            for name, field in cls.__dict__.items()
            if not name.startswith("__") and not callable(field)
        }


dict_converters = {
    "get_fields_for_output": mock_get_fields,
    "get_fields_for_input": mock_get_fields,
    "get_fields_for_create_input": mock_get_fields,
    "get_fields_for_update_input": mock_get_fields,
    "get_fields_for_filter": mock_get_fields,
    "get_fields_for_order_by": mock_get_fields,
    "output_field_converter_function": mock_converter_field_function,
    "input_field_converter_function": mock_converter_field_function,
    "create_input_field_converter_function": mock_converter_field_function,
    "update_input_field_converter_function": mock_converter_field_function,
    "filter_field_converter_function": mock_converter_field_function,
    "order_by_field_converter_function": mock_converter_field_function,
}

dict_resolvers = {
    "create_resolver": mock_resolver_create_models,
    "read_resolver": mock_resolver_read_models,
    "update_resolver": mock_resolver_update_models,
    "delete_resolver": mock_resolver_delete_models,
    "deactivate_resolver": mock_resolver_deactivate_models,
    "activate_resolver": mock_resolver_activate_models,
    "list_resolver": mock_resolver_list_models,
    "search_resolver": mock_resolver_search_models,
}

mock_model_config_without_interfaces = CruddalsBuilderConfig(
    model=MockModel, pascal_case_name="TestModel", **dict_converters, **dict_resolvers
)

mock_model_config_with_interfaceO11 = CruddalsBuilderConfig(
    model=MockModel,
    pascal_case_name="TestModel",
    cruddals_interfaces=(InterfaceO11,),
    **dict_converters,
    **dict_resolvers,
)

mock_model_config_with_interfaceO12 = CruddalsBuilderConfig(
    model=MockModel,
    pascal_case_name="TestModel",
    cruddals_interfaces=(InterfaceO12,),
    **dict_converters,
    **dict_resolvers,
)


class TestCruddalsBuilderConfig:
    def test_requires_model(self):
        with pytest.raises(ValueError) as exc_info:
            CruddalsBuilderConfig(
                model=None,  # type: ignore
                pascal_case_name="TestModel",
                **dict_converters,
                **dict_resolvers,
            )
        assert "model is required" in str(exc_info.value)

    def test_requires_pascal_case_name(self):
        with pytest.raises(ValueError) as exc_info:

            class A:
                pass

            CruddalsBuilderConfig(
                model=A, pascal_case_name="", **dict_converters, **dict_resolvers
            )
        assert "pascal_case_name is required" in str(exc_info.value)

    def test_sets_plural_name_if_not_provided(self):
        config = CruddalsBuilderConfig(
            model=Model,
            pascal_case_name="Model",
            **dict_converters,
            **dict_resolvers,
        )
        assert config.plural_pascal_case_name == "Models"

    def test_sets_plural_name_if_provided(self):
        config = CruddalsBuilderConfig(
            model=Model,
            pascal_case_name="Entity",
            plural_pascal_case_name="Entities",
            **dict_converters,
            **dict_resolvers,
        )
        assert config.plural_pascal_case_name == "Entities"

    def test_sets_prefix(self):
        config = CruddalsBuilderConfig(
            model=Model,
            pascal_case_name="Entity",
            prefix="test",
            **dict_converters,
            **dict_resolvers,
        )
        assert config.prefix == "test"

    def test_sets_suffix(self):
        config = CruddalsBuilderConfig(
            model=Model,
            pascal_case_name="Entity",
            suffix="test",
            **dict_converters,
            **dict_resolvers,
        )
        assert config.suffix == "test"


class TestBaseCruddals:
    def test_add_cruddals_model_to_request(self):
        info = build_class(name="Info", bases=(object,), attrs={})
        cruddals_model = BaseCruddals()
        BaseCruddals.add_cruddals_model_to_request(info, cruddals_model)
        assert info.context.CruddalsModel == cruddals_model  # type: ignore

    def test_add_cruddals_model_to_request_with_context(self):
        info = build_class(name="Info", bases=(object,), attrs={"context": None})
        cruddals_model = BaseCruddals()
        BaseCruddals.add_cruddals_model_to_request(info, cruddals_model)
        assert info.context.CruddalsModel == cruddals_model

    def test_get_function_lists_with_empty_extra_pre_post_resolvers(self):
        base_cruddals = BaseCruddals()
        extra_pre_post_resolvers = {}
        key = "pre_resolver"
        functions = base_cruddals.get_function_lists(key, extra_pre_post_resolvers)
        assert functions == []

    def test_get_function_lists_with_single_function_in_extra_pre_post_resolvers(self):
        base_cruddals = BaseCruddals()
        extra_pre_post_resolvers = {"pre_resolver": lambda: None}
        key = "pre_resolver"
        functions = base_cruddals.get_function_lists(key, extra_pre_post_resolvers)
        assert functions == [extra_pre_post_resolvers["pre_resolver"]]

    def test_get_function_lists_with_multiple_functions_in_extra_pre_post_resolvers(
        self
    ):
        base_cruddals = BaseCruddals()
        extra_pre_post_resolvers = {"pre_mutate": [lambda: None, lambda: None]}
        key = "pre_mutate"
        functions = base_cruddals.get_function_lists(key, extra_pre_post_resolvers)
        assert functions == extra_pre_post_resolvers["pre_mutate"]

    def test_get_pre_and_post_resolves_with_empty_extra_pre_post_resolvers(self):
        base_cruddals = BaseCruddals()
        extra_pre_post_resolvers = {}
        name_function = "resolver"
        pre_resolves, post_resolves = base_cruddals.get_pre_and_post_resolves(
            extra_pre_post_resolvers, name_function
        )
        assert pre_resolves == []
        assert post_resolves == []

    def test_get_pre_and_post_resolves_with_functions_in_extra_pre_post_resolvers(self):
        base_cruddals = BaseCruddals()
        extra_pre_post_resolvers = {
            "pre_resolver": [lambda: None],
            "post_resolver": [lambda: None, lambda: None],
        }
        name_function = "resolver"
        pre_resolves, post_resolves = base_cruddals.get_pre_and_post_resolves(
            extra_pre_post_resolvers, name_function
        )
        assert pre_resolves == extra_pre_post_resolvers["pre_resolver"]
        assert post_resolves == extra_pre_post_resolvers["post_resolver"]

    def test_get_last_element_with_existing_key(self):
        base_cruddals = BaseCruddals()
        key = "key"
        obj = {key: [1, 2, 3]}
        last_element = base_cruddals.get_last_element(key, obj)
        assert last_element == 3

    def test_get_last_element_with_non_existing_key(self):
        base_cruddals = BaseCruddals()
        key = "key"
        obj = {}
        last_element = base_cruddals.get_last_element(key, obj, default="default")
        assert last_element == "default"

    def test_get_last_element_with_non_list_value(self):
        base_cruddals = BaseCruddals()
        key = "key"
        obj = {key: "single value"}
        last_element = base_cruddals.get_last_element(key, obj)
        assert last_element == "single value"

    def test_wrap_resolver_with_pre_post_resolvers(self):
        base_cruddals = BaseCruddals()

        def default_resolver(root, info, **kw):
            return None

        extra_pre_post_resolvers = {
            "pre_resolver": [lambda root, info, **kw: None],
            "post_resolver": [lambda root, info, **kw: None],
        }
        name_function = "resolver"
        wrapped_resolver = base_cruddals.wrap_resolver_with_pre_post_resolvers(
            default_resolver, extra_pre_post_resolvers, name_function
        )
        assert callable(wrapped_resolver)

    def test_wrap_resolver_with_pre_post_resolvers_execution(self):
        base_cruddals = BaseCruddals()

        def default_resolver(root, info, **kw):
            return "default response"

        def pre_resolver(root, info, **kw):
            return (root, info, {**kw, "pre_modified": True})

        def post_resolver(root, info, **kw):
            return "post modified " + kw["CRUDDALS_RESPONSE"]

        extra_pre_post_resolvers = {
            "pre_resolver": [pre_resolver],
            "post_resolver": [post_resolver],
        }
        name_function = "resolver"
        wrapped_resolver = base_cruddals.wrap_resolver_with_pre_post_resolvers(
            default_resolver, extra_pre_post_resolvers, name_function
        )

        # Simulate calling the wrapped resolver with GraphQL's root and info objects
        root = {}
        # info should object, not dict
        info = build_class(name="Info", bases=(object,), attrs={})
        response = wrapped_resolver(root, info)
        assert response == "post modified default response"


class TestBuilderCruddalsModel:
    def test_init(self):
        builder = BuilderCruddalsModel(mock_model_config_without_interfaces)

        assert builder.model == MockModel
        assert builder.prefix == ""
        assert builder.suffix == ""
        expected_plural_name = "TestModels"
        assert builder.cruddals_config.plural_pascal_case_name == expected_plural_name
        assert (
            builder.model_name_in_different_case["plural_pascal_case"]
            == expected_plural_name
        )
        assert builder.cruddals_config == mock_model_config_without_interfaces
        assert builder.model_name_in_different_case == {
            "snake_case": "test_model",
            "plural_snake_case": "test_models",
            "camel_case": "testModel",
            "plural_camel_case": "testModels",
            "pascal_case": "TestModel",
            "plural_pascal_case": "TestModels",
        }
        assert isinstance(builder.registry, RegistryGlobal)
        assert issubclass(builder.model_as_object_type, ModelObjectType)
        assert issubclass(
            builder.model_as_paginated_object_type, ModelPaginatedObjectType
        )
        assert issubclass(builder.model_as_input_object_type, ModelInputObjectType)
        assert issubclass(
            builder.model_as_create_input_object_type, ModelInputObjectType
        )
        assert issubclass(
            builder.model_as_update_input_object_type, ModelInputObjectType
        )
        assert issubclass(
            builder.model_as_filter_input_object_type, ModelSearchInputObjectType
        )
        assert issubclass(
            builder.model_as_order_by_input_object_type, ModelOrderByInputObjectType
        )
        assert isinstance(builder.create_field, ModelCreateUpdateField)
        assert isinstance(builder.read_field, ModelReadField)
        assert isinstance(builder.update_field, ModelCreateUpdateField)
        assert isinstance(builder.delete_field, ModelDeleteField)
        assert isinstance(builder.deactivate_field, ModelDeactivateField)
        assert isinstance(builder.activate_field, ModelActivateField)
        assert isinstance(builder.list_field, ModelListField)
        assert isinstance(builder.search_field, ModelSearchField)

    def test_get_model_object_type(self):
        builder = BuilderCruddalsModel(mock_model_config_without_interfaces)
        dict_of_internal_interface_attr = {}
        result = builder._get_model_object_type(dict_of_internal_interface_attr)
        assert issubclass(result, graphene.ObjectType)

    def test_get_internal_interface_attrs_empty(self):
        builder = BuilderCruddalsModel(mock_model_config_with_interfaceO11)
        result = builder.get_internal_interface_attrs()
        assert result == {}

    def test_get_internal_interface_attrs_include_meta(self):
        builder = BuilderCruddalsModel(mock_model_config_with_interfaceO11)
        result = builder.get_internal_interface_attrs(InterfaceO11.ObjectType, True)
        assert result == {"only_fields": ("id",)}

    def test_get_internal_interface_attrs_not_include_meta(self):
        builder = BuilderCruddalsModel(mock_model_config_with_interfaceO11)
        result = builder.get_internal_interface_attrs(InterfaceO11.ObjectType, False)
        assert result == {}

    def test_get_internal_interface_meta_attrs_empty(self):
        builder = BuilderCruddalsModel(mock_model_config_with_interfaceO11)
        result = builder.get_internal_interface_meta_attrs()
        assert result == {}

    def test_get_internal_interface_meta_attrs(self):
        builder = BuilderCruddalsModel(mock_model_config_with_interfaceO11)
        result = builder.get_internal_interface_meta_attrs(InterfaceO11.ObjectType)
        assert result == {"only_fields": ("id",)}
