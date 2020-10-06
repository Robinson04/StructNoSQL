from typing import List, Optional, Any, Dict, _GenericAlias, Tuple

from StructNoSQL.dummy_object import DummyObject
from StructNoSQL.dynamodb.models import DatabasePathElement
from StructNoSQL.practical_logger import message_with_vars
from StructNoSQL.query import Query


class TableDataModel:
    pass

class BaseDataModel:
    def __init__(self):
        self.childrens_map: Optional[dict] = None

class MapModel(BaseDataModel):
    _default_primitive_type = dict

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


class BaseItem:
    _table = None
    _database_path: Optional[List[DatabasePathElement]] = None
    _dict_key_expected_type_: Optional[type] = None
    _dict_items_excepted_type: Optional[type or MapModel] = None
    # We set the _database_path as static, so that the assign_internal_mapping_from_class can setup the path only once,
    # only by having access to the inheritor class type, not even the instance. Yet, when set the _database_path
    # statically, the value is not attributed to the BaseField class (which would cause to have multiple classes override
    # the paths of the others), but rather, it is statically set on the class that inherit from BaseField.

    def __init__(self, field_type: Optional[type] = Any, custom_default_value: Optional[Any] = None):
        self._value = None
        self._query = None

        self.map_key_expected_type: Optional[type] = None
        self.map_model: Optional[MapModel] = None

        self._custom_default_value = custom_default_value
        self._field_type = field_type
        if isinstance(self._field_type, _GenericAlias):
            alias_variable_name: Optional[str] = self._field_type.__dict__.get("_name", None)
            if alias_variable_name is not None:
                alias_args: Optional[Tuple] = self._field_type.__dict__.get("__args__", None)

                if alias_variable_name == "Dict":
                    self._field_type = dict
                    self._dict_key_expected_type = alias_args[0]
                    self._dict_items_excepted_type = alias_args[1]

                elif alias_variable_name == "List":
                    raise Exception(f"List not yet implemented.")

    def validate_data(self, load_data_into_objects: bool) -> Optional[Any]:
        from StructNoSQL.validator import validate_data
        validated_data = validate_data(
            value=self._value, item_type_to_return_to=self, load_data_into_objects=load_data_into_objects,
            expected_value_type=self._field_type, map_model=self.map_model,
            dict_items_excepted_type=self.dict_items_excepted_type, dict_excepted_key_type=self.dict_key_expected_type
        )
        self._value = validated_data
        return validated_data

    def populate(self, value: Any):
        self._value = value
        # self.validate_data()
        # print("Finished data validation.")

    def query(self, key_name: str, key_value: str, index_name: Optional[str] = None, query_kwargs: Optional[dict] = None) -> Query:
        for path_element in self._database_path:
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
                    ))

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
    def dict_key_expected_type(self) -> Optional[type]:
        return self._dict_key_expected_type

    @property
    def dict_items_excepted_type(self) -> Optional[type or MapModel]:
        return self._dict_items_excepted_type


class BaseField(BaseItem):
    def __init__(self, name: str, field_type: Optional[type] = None, required: Optional[bool] = False,
                 custom_default_value: Optional[Any] = None, key_name: Optional[str] = None):
        super().__init__(field_type=field_type if field_type is not None else Any, custom_default_value=custom_default_value)
        self._name = name
        self._required = required
        self._key_name = None

        if key_name is not None:
            if field_type == dict or type(field_type) == _GenericAlias:
                self._key_name = key_name
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
            map_item = MapItem(model_type=self.dict_items_excepted_type, parent_field=self)
            return map_item
        else:
            raise Exception(message_with_vars(
                message="Tried to access dict item of a field that was not of type dict, "
                        "Dict or did not properly received the expected type of the dict items.",
                vars_dict={"fieldName": self.field_name, "fieldType": self.field_type,
                           "dictItemsExceptedType": self.dict_items_excepted_type}
            ))

    def __getattr__(self, key):
        item = self.__dict__.get(key, None)
        if item is not None:
            return item
        else:
            if self._field_type == dict:
                dict_expected_type_item = self.dict_items_excepted_type.__dict__.get(key, None)
                if dict_expected_type_item is not None:
                    return dict_expected_type_item
        raise AttributeError()

    def post(self, value: any):
        print(self._database_path)

    @property
    def field_name(self) -> str:
        return self._name

    @property
    def field_type(self) -> type:
        return self._field_type

    @property
    def key_name(self) -> Optional[str]:
        return self._key_name

    @property
    def required(self) -> bool:
        return self._required

    @property
    def value(self) -> Any:
        return self._value

    @property
    def database_path(self):
        return self._database_path

    @property
    def table(self):
        return self._table


class MapItem(BaseField):
    _default_primitive_type = dict

    def __init__(self, model_type: type, parent_field: BaseField):
        super().__init__(name=None, field_type=dict, custom_default_value=dict())
        self.model_type = model_type

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



