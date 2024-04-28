from typing import Any, Dict, Hashable, Union
from graphene_cruddals.utils.typing.custom_typing import GRAPHENE_TYPE, TypeRegistryForField, TypeRegistryForModel


class RegistryGlobal:
    """
    A class that represents a global registry for models and fields.
    It stores registries in a hashable format to ensure uniqueness and provide easy access.

    Attributes:
        _model_registry (Dict[str, Any]): A dictionary that stores the registered models.
        _field_registry (Dict[str, Any]): A dictionary that stores the registered fields.
    """

    def __init__(self):
        """
        Initializes the RegistryGlobal instance with empty registries for models and fields.
        """
        self._model_registry = {}
        self._field_registry = {}

    def register_model(self, model: Any, type_to_registry: TypeRegistryForModel, value: Any):
        """
        Registers a model with a specific class under a given type registry.

        Args:
            model (Dict[str, Any]): The model to be registered.
            type_to_registry (TypeRegistryForModel): The type of registry for the model.
            value: (Any): The value to associate with the model.

        Returns:
            None
        """
        model = self.get_hashable_value(model)
        self._model_registry.setdefault(model, {})[type_to_registry] = value

    def get_registry_for_model(self, model: Any) -> Dict[TypeRegistryForModel, Any]:
        """
        Retrieves the registry for a specific model.

        Args:
            model (Dict[str, Any]): The model to retrieve the registry for.

        Returns:
            dict: The registry for the specified model.
        """
        model = self.get_hashable_value(model)
        return self._model_registry.get(model, {})

    def get_all_models_registered(self) -> Dict[str, Any]:
        """
        Retrieves all the registered models.

        Returns:
            dict: A dictionary containing all the registered models.
        """
        return self._model_registry

    def get_all_fields_registered(self) -> Dict[str, Any]:
        """
        Retrieves all the registered fields.

        Returns:
            dict: A dictionary containing all the registered fields.
        """
        return self._field_registry

    def register_field(self, field: Any, type_to_registry: TypeRegistryForField, converted: GRAPHENE_TYPE):
        """
        Registers a field in the registry.

        Args:
            field (Any): The field to be registered.
            type_to_registry (TypeRegistryForField): The type of registry for the field.
            converted: The converted value associated with the field.

        Returns:
            None
        """
        field = self.get_hashable_value(field)
        self._field_registry.setdefault(field, {})[type_to_registry] = converted

    def get_registry_for_field(self, field: Any):
        """
        Retrieves the registry for a specific field.

        Args:
            field (Any): The field to retrieve the registry for.

        Returns:
            dict: The registry for the specified field.
        """
        field = self.get_hashable_value(field)
        return self._field_registry.get(field, {})

    @staticmethod
    def get_hashable_value(value: Any):
        """
        Converts a non-hashable value to a hashable value.

        Args:
            value (Any): The value to be converted.

        Returns:
            Any: The converted hashable value.
        """
        if not isinstance(value, Hashable):
            if isinstance(value, dict):
                value = tuple(value.items())
            elif isinstance(value, list):
                value = tuple(value)
        return value


registry = None


def get_global_registry(name_registry: Union[str, None] = None) -> RegistryGlobal:
    """
    Retrieves or creates a global registry instance by name. If no name is provided, it uses a default global registry.

    Args:
        name_registry (Union[str, None]): The name of the registry to retrieve or create.
    
    Returns:
        RegistryGlobal: The global registry instance.
    """
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
    """
    Resets the global registry to None, effectively clearing all registrations.
    """
    global registry
    registry = None
