import graphene
from enum import Enum
from typing import Any, Type, TypedDict, Union, List, Literal, Optional


GRAPHENE_TYPE = Union[
    graphene.Scalar,
    graphene.String,
    graphene.ID,
    graphene.Int,
    graphene.Float,
    graphene.Boolean,
    graphene.Date,
    graphene.DateTime,
    graphene.Time,
    graphene.Decimal,
    graphene.JSONString,
    graphene.UUID,
    graphene.List,
    graphene.NonNull,
    graphene.Enum,
    graphene.Argument,
    graphene.Dynamic,
]

class ModifyArgument(TypedDict):
    type_: Union[Any, None]
    name: Union[str, None]
    required: Union[bool, None]
    description: Union[str, None]
    hidden: Union[bool, None]


FunctionType = Literal[
    "create", "read", "update", "delete", "deactivate", "activate", "list", "search"
]


CamelFunctionType = Literal[
    "Create", "Read", "Update", "Delete", "Deactivate", "Activate", "List", "Search"
]


TypesMutation = Literal["create_update", "create", "update"]


TypeRegistryForModel = Literal[
    "object_type",
    "paginated_object_type",
    "input_object_type",
    "input_object_type_for_create",
    "input_object_type_for_update",
    "input_object_type_for_search",
    "input_object_type_for_order_by",
    "input_object_type_for_connect",
    "input_object_type_for_connect_disconnect",
    "cruddals",
]


TypeRegistryForField = Literal[
    "output",
    "input_for_create_update",
    "input_for_create",
    "input_for_update",
    "input_for_search",
    "input_for_order_by",
]


class TypeRegistryForModelEnum(Enum):
    OBJECT_TYPE = "object_type"
    PAGINATED_OBJECT_TYPE = "paginated_object_type"
    INPUT_OBJECT_TYPE = "input_object_type"
    INPUT_OBJECT_TYPE_FOR_CREATE = "input_object_type_for_create"
    INPUT_OBJECT_TYPE_FOR_UPDATE = "input_object_type_for_update"
    INPUT_OBJECT_TYPE_FOR_SEARCH = "input_object_type_for_search"
    INPUT_OBJECT_TYPE_FOR_ORDER_BY = "input_object_type_for_order_by"
    INPUT_OBJECT_TYPE_FOR_CONNECT = "input_object_type_for_connect"
    INPUT_OBJECT_TYPE_FOR_CONNECT_DISCONNECT = (
        "input_object_type_for_connect_disconnect"
    )
    CRUDDALS = "cruddals"


class TypeRegistryForFieldEnum(Enum):
    OUTPUT = "output"
    INPUT_FOR_CREATE_UPDATE = "input_for_create_update"
    INPUT_FOR_CREATE = "input_for_create"
    INPUT_FOR_UPDATE = "input_for_update"
    INPUT_FOR_SEARCH = "input_for_search"
    INPUT_FOR_ORDER_BY = "input_for_order_by"


# For interfaces,
# is executed first AppInterface, after Model Interface, for both is executed in order of list
INTERFACE_META_CLASS_TYPE_NAMES = [
    "MetaObjectType",
    "MetaInputObjectType",
    "MetaCreateInputObjectType",
    "MetaUpdateInputObjectType",
    "MetaFilterInputObjectType",
    "MetaOrderByInputObjectType",
]

CLASS_INTERFACE_TYPE_NAMES = [
    "ObjectType",
    "InputObjectType",
    "CreateInputObjectType",
    "UpdateInputObjectType",
    "FilterInputObjectType",
    "OrderByInputObjectType",
]

CLASS_INTERFACE_FIELDS_NAMES = [
    "CreateField",
    "ReadField",
    "UpdateField",
    "DeleteField",
    "DeactivateField",
    "ActivateField",
    "ListField",
    "SearchField",
]

INTERFACES_NAME_CRUDDALS = CLASS_INTERFACE_FIELDS_NAMES + CLASS_INTERFACE_TYPE_NAMES + INTERFACE_META_CLASS_TYPE_NAMES


class CruddalsInterfaceNames(Enum):
    """
    An enumeration class that defines the names of the interfaces for CRUDDALS operations
    and object types in the Cruddals system.

    Attributes:
    - CREATE_FIELD: The name of the interface for creating a field.
    - READ_FIELD: The name of the interface for reading a field.
    - UPDATE_FIELD: The name of the interface for updating a field.
    - DELETE_FIELD: The name of the interface for deleting a field.
    - DEACTIVATE_FIELD: The name of the interface for deactivating a field.
    - ACTIVATE_FIELD: The name of the interface for activating a field.
    - LIST_FIELD: The name of the interface for listing fields.
    - SEARCH_FIELD: The name of the interface for searching fields.
    - OBJECT_TYPE: The name of the interface for object types.
    - INPUT_OBJECT_TYPE: The name of the interface for input object types.
    - CREATE_INPUT_OBJECT_TYPE: The name of the interface for creating input object types.
    - UPDATE_INPUT_OBJECT_TYPE: The name of the interface for updating input object types.
    - FILTER_INPUT_OBJECT_TYPE: The name of the interface for filtering input object types.
    - ORDER_BY_INPUT_OBJECT_TYPE: The name of the interface for ordering by input object types.
    """

    CREATE_FIELD = "CreateField"
    READ_FIELD = "ReadField"
    UPDATE_FIELD = "UpdateField"
    DELETE_FIELD = "DeleteField"
    DEACTIVATE_FIELD = "DeactivateField"
    ACTIVATE_FIELD = "ActivateField"
    LIST_FIELD = "ListField"
    SEARCH_FIELD = "SearchField"

    OBJECT_TYPE = "ObjectType"
    INPUT_OBJECT_TYPE = "InputObjectType"
    CREATE_INPUT_OBJECT_TYPE = "CreateInputObjectType"
    UPDATE_INPUT_OBJECT_TYPE = "UpdateInputObjectType"
    FILTER_INPUT_OBJECT_TYPE = "FilterInputObjectType"
    ORDER_BY_INPUT_OBJECT_TYPE = "OrderByInputObjectType"


class MetaCruddalsInterfaceNames(Enum):
    META_OBJECT_TYPE = "MetaObjectType"
    META_INPUT_OBJECT_TYPE = "MetaInputObjectType"
    META_CREATE_INPUT_OBJECT_TYPE = "MetaCreateInputObjectType"
    META_UPDATE_INPUT_OBJECT_TYPE = "MetaUpdateInputObjectType"
    META_FILTER_INPUT_OBJECT_TYPE = "MetaFilterInputObjectType"
    META_ORDER_BY_INPUT_OBJECT_TYPE = "MetaOrderByInputObjectType"


class NameCaseType(TypedDict):
    snake_case: str
    plural_snake_case: str
    camel_case: str
    plural_camel_case: str
    pascal_case: str
    plural_pascal_case: str


class RootFieldsType(TypedDict):
    query: Type[graphene.ObjectType]
    mutation: Optional[Type[graphene.ObjectType]]
    # subscription: Optional[Type[graphene.ObjectType]]


class TypesMutationEnum(Enum):
    CREATE = "create"
    UPDATE = "update"
    CREATE_UPDATE = "create_update"


class MetaAttrs(TypedDict):
    only: Union[List[str], Literal["__all__"], None] # For support of graphene-django
    only_fields: Union[List[str], Literal["__all__"], None] # For support of graphene-django
    fields: Union[List[str], Literal["__all__"], None]
    exclude: Union[List[str], None] # For support of graphene-django
    exclude_fields: Union[List[str], None]
