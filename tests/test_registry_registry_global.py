import pytest

import graphene
from graphene_cruddals.registry.registry_global import (
    RegistryGlobal,
    get_global_registry,
    reset_global_registry,
)
from graphene_cruddals.utils.typing.custom_typing import TypeRegistryForFieldEnum


@pytest.fixture
def registry():
    return get_global_registry()


@pytest.fixture
def registry_named():
    return get_global_registry("MyRegistry")


@pytest.fixture
def reset_registry():
    reset_global_registry()


def test_register_model(registry):
    model = {"name": "ModelA"}
    registry.register_model(model, "type_a", "value_a")
    assert registry.get_registry_for_model(model) == {
        "type_a": "value_a"
    }, "Model not registered correctly"


def test_get_all_models(reset_registry, registry):
    registry.register_model({"name": "ModelA"}, "type_a", "value_a")
    registry.register_model({"name": "ModelB"}, "type_b", "value_b")
    assert (
        len(registry.get_all_models_registered()) == 2
    ), "Incorrect number of models registered"


def test_get_all_fields():
    custom_registry = get_global_registry("CustomRegistry")
    custom_registry.register_field(
        ["field1"], TypeRegistryForFieldEnum.OUTPUT.value, graphene.String()
    )
    custom_registry.register_field(
        ["field2"], TypeRegistryForFieldEnum.OUTPUT.value, graphene.String()
    )
    assert (
        len(custom_registry.get_all_fields_registered()) == 2
    ), "Incorrect number of fields registered"


def test_hashable_value_conversions():
    registry = RegistryGlobal()
    assert isinstance(
        registry.get_hashable_value({"key": "value"}), tuple
    ), "Dictionary not converted to tuple"
    assert isinstance(
        registry.get_hashable_value(["item1", "item2"]), tuple
    ), "List not converted to tuple"


def test_global_registry_creation(registry):
    reg = get_global_registry()
    assert isinstance(
        reg, RegistryGlobal
    ), "Global registry instance not created properly"


def test_named_global_registry_creation(registry_named):
    reg = get_global_registry("MyRegistry")
    assert isinstance(
        reg, RegistryGlobal
    ), "Named global registry instance not created properly"
