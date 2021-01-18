from typing import List, Optional, Any, Dict, _GenericAlias, Tuple

from StructNoSQL.dummy_object import DummyObject
from StructNoSQL.dynamodb.models import DatabasePathElement
from StructNoSQL.practical_logger import message_with_vars
from StructNoSQL.query import Query


class BaseDataModel:
    def __init__(self):
        self.childrens_map: Optional[dict] = None

class MapModel(BaseDataModel):
    _default_primitive_type = dict
    required_fields: list = None

    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs
        # from StructNoSQL import field_loader
        # field_loader.load(class_instance=self, **kwargs)

    def new(self):
        pass

    @property
    def dict(self) -> dict:
        return self.childrens_map if self.childrens_map is not None else self.kwargs

class TableDataModel(MapModel):
    # The TableDataModel inherit from MapModel, to allow easier validation of record data.
    # For example, when the put_one_record function is used, and needs data validation.
    pass


class BaseItem:
    _table = None
    _database_path: Optional[List[DatabasePathElement]] = None
    _dict_key_expected_type: Optional[type] = None
    _dict_items_excepted_type: Optional[type or MapModel] = None
    # We set the _database_path as static, so that the assign_internal_mapping_from_class can setup the path only once,
    # only by having access to the inheritor class type, not even the instance. Yet, when set the _database_path
    # statically, the value is not attributed to the BaseField class (which would cause to have multiple classes override
    # the paths of the others), but rather, it is statically set on the class that inherit from BaseField.

    def __init__(self, field_type: Optional[type] = Any, custom_default_value: Optional[Any] = None):
        # todo: add a file_url field_type
        self._value = None
        self._query = None

        self.map_key_expected_type: Optional[type] = None
        self.map_model: Optional[MapModel or type] = None

        self._custom_default_value = custom_default_value
        self._field_type = field_type
        self._default_field_type = field_type
        if isinstance(self._field_type, (list, tuple)):
            if len(self._field_type) > 0:
                self._default_field_type = self._field_type[0]

        elif isinstance(self._field_type, _GenericAlias):
            alias_variable_name: Optional[str] = self._field_type.__dict__.get("_name", None)
            if alias_variable_name is not None:
                alias_args: Optional[Tuple] = self._field_type.__dict__.get("__args__", None)

                if alias_variable_name == "Dict":
                    self._field_type = dict
                    self._default_field_type = dict
                    self._dict_key_expected_type = alias_args[0]
                    self._dict_items_excepted_type = alias_args[1]

                elif alias_variable_name == "List":
                    raise Exception(f"List not yet implemented.")

    def validate_data(self) -> Tuple[Optional[Any], bool]:
        from StructNoSQL.validator import validate_data
        validated_data, valid = validate_data(
            value=self._value, item_type_to_return_to=self,
            expected_value_type=self._field_type,
        )
        self._value = validated_data
        return validated_data, valid

    def populate(self, value: Any):
        self._value = value
        # self.validate_data()
        # print("Finished data validation.")

    def query(self, key_name: str, key_value: str, fields_paths_to_get: List[str], index_name: Optional[str] = None, query_kwargs: Optional[dict] = None) -> Query:
        """for path_element in self._database_path:
            if "$key$:" in path_element.element_key:
                variable_name = path_element.element_key.replace("$key$:", "")
                if query_kwargs is not None:
                    matching_kwarg = query_kwargs.get(variable_name, None)
                    if matching_kwarg is not None:
                        path_element.element_key = matching_kwarg
                    else:
                        raise Exception(message_with_vars(
                            message="A variable was required but not found in the query_kwargs dict passed to the query function.",
                            vars_dict={"keyVariableName": variable_name, "matchingKwarg": matching_kwarg, "queryKwargs": query_kwargs, "databasePath": self._database_path}
                        ))
                else:
                    raise Exception(message_with_vars(
                        message="A variable was required but not query_kwargs have been passed to the query function.",
                        vars_dict={"keyVariableName": variable_name, "queryKwargs": query_kwargs, "databasePath": self._database_path}
                    ))"""

        self._query = Query(
            variable_validator=self, table=self._table,
            target_database_path=self._database_path,
            key_name=key_name, key_value=key_value, index_name=index_name
        )
        return self._query

    def get_default_value(self):
        if self._custom_default_value is not None:
            return self._custom_default_value
        # We initialize the default field type
        # and return it as the default value.
        return self._field_type()

    @property
    def custom_default_value(self) -> Optional[Any]:
        return self._custom_default_value

    @property
    def value(self) -> Any:
        return self._value

    @property
    def field_type(self) -> Any:
        return self._field_type

    @property
    def default_field_type(self) -> type:
        return self._default_field_type

    @property
    def dict_key_expected_type(self) -> Optional[type]:
        return self._dict_key_expected_type

    @property
    def dict_items_excepted_type(self) -> Optional[type or MapModel]:
        return self._dict_items_excepted_type

    @property
    def database_path(self) -> Optional[List[DatabasePathElement]]:
        return self._database_path

    @property
    def table(self):
        return self._table


class BaseField(BaseItem):
    def __init__(self, name: str, field_type: Optional[Any] = None, required: Optional[bool] = False, not_modifiable: Optional[bool] = False,
                 custom_default_value: Optional[Any] = None, key_name: Optional[str] = None, max_nested_depth: Optional[int] = 32):
        super().__init__(field_type=field_type if field_type is not None else Any, custom_default_value=custom_default_value)
        self._name = name
        self._required = required
        self._key_name = None

        if max_nested_depth is not None and max_nested_depth > 32:
            raise Exception(f"DynamoDB support a maximum depth of nested of items of 32. This is not imposed by StructNoSQL but a platform limitation.\n"
                            f"See : https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Limits.html#limits-attributes")
        self._max_nested = max_nested_depth

        if not_modifiable is True:
            raise Exception(f"Not modifiable not yet implemented")

        if key_name is not None:
            insta = isinstance(field_type, (tuple, list))
            if field_type is dict or type(field_type) is _GenericAlias:
                self._key_name = key_name
            elif isinstance(field_type, (tuple, list)):
                raise Exception(f"Multiple dictionaries are not yet supported.")
                all_items_are_dict = True
                for item in field_type:
                    item_type = type(item)
                    if not isinstance(item, (dict, _GenericAlias)):
                        all_items_are_dict = False
                        break
                if all_items_are_dict is True:
                    self._key_name = key_name
                else:
                    raise Exception(message_with_vars(
                        "key_name cannot be set on a field that is a tuple or list that does not exclusivly contains dict or Dict items",
                        vars_dict={"fieldName": name, "fieldType": field_type, "keyName": key_name}
                    ))
            else:
                raise Exception(message_with_vars(
                    "key_name cannot be set on a field that is not of type dict or Dict",
                    vars_dict={"fieldName": name, "fieldType": field_type, "keyName": key_name}
                ))
        else:
            if field_type == dict or type(field_type) == _GenericAlias:
                self._key_name = f"{name}Key"

    def populate(self, value: any):
        super().populate(value=value)

    @property
    def dict_item(self):
        """ :return: BaseField """
        if self._field_type == dict and self.dict_items_excepted_type is not None:
            map_item = MapItem(parent_field=self, field_type=self.dict_items_excepted_type, model_type=self.dict_items_excepted_type)
            return map_item
        else:
            raise Exception(message_with_vars(
                message="Tried to access dict item of a field that was not of type dict, "
                        "Dict or did not properly received the expected type of the dict items.",
                vars_dict={"fieldName": self.field_name, "fieldType": self.field_type,
                           "dictItemsExceptedType": self.dict_items_excepted_type}
            ))

    def post(self, value: any):
        print(self._database_path)

    @property
    def field_name(self) -> str:
        return self._name

    @property
    def key_name(self) -> Optional[str]:
        return self._key_name

    @property
    def required(self) -> bool:
        return self._required

    @property
    def max_nested(self) -> int:
        # todo: find a better name than max_nested
        return self._max_nested

    def copy(self):
        # return BaseField(name=self._name, field_type=self._field_type, required=self._required, custom_default_value=self._custom_default_value, key_name=self._key_name, max_nested_depth=self._max_nested)
        from copy import copy
        return copy(self)

class MapItem(BaseField):
    _default_primitive_type = dict

    def __init__(self, parent_field: BaseField, model_type: type, field_type: type):
        super().__init__(name=None, field_type=field_type, custom_default_value=field_type())
        self.map_model = model_type

        from StructNoSQL.table import make_dict_key_var_name, try_to_get_primitive_default_type_of_item
        element_key = make_dict_key_var_name(parent_field.key_name)
        default_type = try_to_get_primitive_default_type_of_item(parent_field.dict_items_excepted_type)
        database_path_element = DatabasePathElement(element_key=element_key, default_type=default_type)
        self._database_path = [*parent_field.database_path, database_path_element]
        self._table = parent_field.table


class MapField(BaseField):
    def __init__(self, name: str, model):
        super().__init__(name=name, field_type=dict)
        self.map_model: type(MapModel) = model
        # self.populate(value=model().dict)
        # todo: create models to validate the dicts


class ListField(BaseField):
    def __init__(self, name: str, items_model: Optional[MapModel] = None):
        super().__init__(name=name, field_type=list)
        self._list_items_model = items_model
        # todo: allow to have multiple items_model and that an item can be one of many item models
        # self.populate(value=model().dict)
