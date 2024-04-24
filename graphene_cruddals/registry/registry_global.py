from typing import Any, Hashable, Union
from utils.typing.custom_typing import TypeRegistryForField, TypeRegistryForModel


class RegistryGlobal:

    def __init__(self):
        self._model_registry = {}
        self._field_registry = {}

    def register_model( self, model: Any, type_to_registry: TypeRegistryForModel, cls ):
        model = self.get_hashable_value(model)
        self._model_registry.setdefault(model, {})[type_to_registry] = cls

    def get_registry_for_model(self, model: Any):
        model = self.get_hashable_value(model)
        return self._model_registry.get(model)

    def get_all_models_registered(self):
        return self._model_registry

    def get_all_fields_registered(self):
        return self._field_registry

    def register_field( self, field: Any, type_to_registry: TypeRegistryForField, converted ):
        field = self.get_hashable_value(field)
        self._field_registry.setdefault(field, {})[type_to_registry] = converted

    def get_registry_for_field(self, field: Any):
        field = self.get_hashable_value(field)
        return self._field_registry.get(field)

    @staticmethod
    def get_hashable_value(value: Any):
        if not isinstance(value, Hashable):
            if isinstance(value, dict):
                value = tuple(value.items())
            elif isinstance(value, list):
                value = tuple(value)
        return value


registry = None


def get_global_registry(name_registry: Union[str, None] = None) -> RegistryGlobal:
    if name_registry:
        custom_registry = globals().get(name_registry)
        if not custom_registry:
            globals()[name_registry] = RegistryGlobal()
        return globals()[name_registry]
    else:
        global registry
        if not registry:
            registry = RegistryGlobal()
        return registry


def reset_global_registry():
    global registry
    registry = None
