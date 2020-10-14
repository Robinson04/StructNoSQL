from dataclasses import dataclass
from typing import Optional, Any, List


@dataclass
class DatabasePathElement:
    element_key: str
    default_type: type
    custom_default_value: Optional[Any] = None

    def get_default_value(self) -> Any:
        if self.custom_default_value is not None:
            return self.custom_default_value
        return self.default_type()


@dataclass
class FieldSetter:
    target_path: str
    value_to_set: Any
    query_kwargs: Optional[dict] = None


@dataclass
class FieldGetter:
    target_path: str
    query_kwargs: Optional[dict] = None


@dataclass
class DynamoDBMapObjectSetter:
    target_path_elements: List[DatabasePathElement]
    value_to_set: Any
