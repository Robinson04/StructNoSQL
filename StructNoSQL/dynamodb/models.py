from dataclasses import dataclass
from typing import Optional, Any, List, Dict


@dataclass
class DatabasePathElement:
    element_key: str
    default_type: type
    custom_default_value: Optional[Any] = None

    def get_default_value(self) -> Any:
        if self.custom_default_value is not None:
            return self.custom_default_value
        if self.default_type is Any:
            return None
        return self.default_type()


@dataclass
class FieldSetter:
    field_path: str
    value_to_set: Any
    query_kwargs: Optional[dict] = None

@dataclass
class UnsafeFieldSetter:
    value_to_set: Any
    safe_base_field_path: Optional[str] = None
    unsafe_path_continuation: Optional[List[DatabasePathElement]] = None
    query_kwargs: Optional[dict] = None


@dataclass
class FieldGetter:
    field_path: str
    query_kwargs: Optional[dict] = None


@dataclass
class FieldRemover:
    field_path: str
    query_kwargs: Optional[dict] = None


@dataclass
class DynamoDBMapObjectSetter:
    field_path_elements: List[DatabasePathElement]
    value_to_set: Any


@dataclass
class MapItemInitializer:
    path_target: str
    last_item_element_key: str
    item_default_value: Any
    expression_attribute_names: Dict[str, str]

@dataclass
class MapItemInitializerContainer:
    item: MapItemInitializer
    nexts_in_line: Dict[str, Any]
