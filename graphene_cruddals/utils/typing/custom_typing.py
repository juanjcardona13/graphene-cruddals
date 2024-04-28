from enum import Enum
from typing import Any, List, Literal, Optional, Type, TypedDict, Union

import graphene

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
    graphene.Field,
    graphene.InputField,
    graphene.Interface,
    graphene.ObjectType,
    graphene.InputObjectType,
    graphene.Union,
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

NameResolverType = Literal[
    "resolver",
    "pre_resolver",
    "post_resolver",
    "override_total_resolver",
    "mutate",
    "pre_mutate",
    "post_mutate",
    "override_total_mutate",
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


ListInternalInterfaceMetaClassNames = Literal[
    "MetaObjectType",
    "MetaInputObjectType",
    "MetaCreateInputObjectType",
    "MetaUpdateInputObjectType",
    "MetaFilterInputObjectType",
    "MetaOrderByInputObjectType",
]

ListInternalInterfaceTypeNames = Literal[
    "ObjectType",
    "InputObjectType",
    "CreateInputObjectType",
    "UpdateInputObjectType",
    "FilterInputObjectType",
    "OrderByInputObjectType",
]

ListInternalInterfaceFieldsNames = Literal[
    "ModelCreateField",
    "ModelReadField",
    "ModelUpdateField",
    "ModelDeleteField",
    "ModelDeactivateField",
    "ModelActivateField",
    "ModelListField",
    "ModelSearchField",
]

ListInternalInterfaceNameCruddals = Union[
    ListInternalInterfaceMetaClassNames,
    ListInternalInterfaceTypeNames,
    ListInternalInterfaceFieldsNames,
]

# For interfaces,
# is executed first AppInterface, after Model Interface, for both is executed in order of list
INTERNAL_INTERFACE_META_CLASS_NAMES: List[ListInternalInterfaceMetaClassNames] = [
    "MetaObjectType",
    "MetaInputObjectType",
    "MetaCreateInputObjectType",
    "MetaUpdateInputObjectType",
    "MetaFilterInputObjectType",
    "MetaOrderByInputObjectType",
]

CLASS_INTERNAL_INTERFACE_TYPE_NAMES: List[ListInternalInterfaceTypeNames] = [
    "ObjectType",
    "InputObjectType",
    "CreateInputObjectType",
    "UpdateInputObjectType",
    "FilterInputObjectType",
    "OrderByInputObjectType",
]

CLASS_INTERNAL_INTERFACE_FIELDS_NAMES: List[ListInternalInterfaceFieldsNames] = [
    "ModelCreateField",
    "ModelReadField",
    "ModelUpdateField",
    "ModelDeleteField",
    "ModelDeactivateField",
    "ModelActivateField",
    "ModelListField",
    "ModelSearchField",
]

INTERNAL_INTERFACES_NAME_CRUDDALS: List[ListInternalInterfaceNameCruddals] = (
    CLASS_INTERNAL_INTERFACE_FIELDS_NAMES
    + CLASS_INTERNAL_INTERFACE_TYPE_NAMES
    + INTERNAL_INTERFACE_META_CLASS_NAMES
)


class CruddalsInternalInterfaceNames(Enum):
    CREATE_FIELD = "ModelCreateField"
    READ_FIELD = "ModelReadField"
    UPDATE_FIELD = "ModelUpdateField"
    DELETE_FIELD = "ModelDeleteField"
    DEACTIVATE_FIELD = "ModelDeactivateField"
    ACTIVATE_FIELD = "ModelActivateField"
    LIST_FIELD = "ModelListField"
    SEARCH_FIELD = "ModelSearchField"

    OBJECT_TYPE = "ObjectType"
    INPUT_OBJECT_TYPE = "InputObjectType"
    CREATE_INPUT_OBJECT_TYPE = "CreateInputObjectType"
    UPDATE_INPUT_OBJECT_TYPE = "UpdateInputObjectType"
    FILTER_INPUT_OBJECT_TYPE = "FilterInputObjectType"
    ORDER_BY_INPUT_OBJECT_TYPE = "OrderByInputObjectType"


class MetaCruddalsInternalInterfaceNames(Enum):
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
    only_fields: Union[List[str], Literal["__all__"], None]
    exclude_fields: Union[List[str], None]
