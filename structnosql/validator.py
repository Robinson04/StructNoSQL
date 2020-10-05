from typing import Optional, _GenericAlias, Tuple, List, Any
from StructNoSQL.fields import BaseItem, MapModel
from StructNoSQL.field_loader import load as field_load
from StructNoSQL.practical_logger import exceptions_with_vars_message


def validate_data(value, expected_value_type: type, load_data_into_objects: bool,
                  item_type_to_return_to: Optional[BaseItem] = None,
                  map_model: Optional[MapModel] = None,
                  dict_excepted_key_type: Optional[type] = None, dict_value_excepted_type: Optional[type] = None,
                  list_items_models: Optional[MapModel] = None) -> Any:

    value_type = type(value)
    if not _types_match(type_to_check=value_type, expected_type=expected_value_type):
        print(exceptions_with_vars_message(
            message=f"Primitive value did not match expected type. Value of None is being returned.",
            vars_dict={"value": value, "valueType": value_type, "expectedValueType": expected_value_type}
        ))
        return None

    """if isinstance(expected_value_type, type):
        _raise_if_types_did_not_match(type_to_check=value_type, expected_type=expected_value_type)
    else:
        if isinstance(expected_value_type, _GenericAlias):
            alias_variable_name: Optional[str] = expected_value_type.__dict__.get("_name", None)
            if alias_variable_name is not None:
                alias_args: Optional[Tuple] = expected_value_type.__dict__.get("__args__", None)

                if alias_variable_name == "Dict":
                    _raise_if_types_did_not_match(type_to_check=value_type, expected_type=dict)

                    if alias_args is not None and len(alias_args) == 2:
                        dict_key_expected_type = alias_args[0]
                        dict_item_expected_type = alias_args[1]
                        for key, item in value.items():
                            _raise_if_types_did_not_match(type_to_check=type(key), expected_type=dict_key_expected_type)
                            if MapModel in dict_item_expected_type.__bases__:
                                value[key] = dict_item_expected_type(**item)
                                print(value)

                elif alias_variable_name == "List":
                    raise Exception(f"List not yet implemented.")"""


    if value_type == dict:
        value: dict
        if item_type_to_return_to is not None and item_type_to_return_to.map_model is not None:
            item_keys_to_pop: List[str] = list()
            for key, item in value.items():
                item_matching_validation_model_variable: Optional[BaseItem] = item_type_to_return_to.map_model.__dict__.get(key, None)
                if item_matching_validation_model_variable is not None:
                    item = validate_data(
                        value=item, item_type_to_return_to=item_matching_validation_model_variable,
                        expected_value_type=item_matching_validation_model_variable.field_type,
                        load_data_into_objects=load_data_into_objects
                    )
                    if item is not None:
                        if load_data_into_objects is True:
                            item, kwargs_not_consumed = field_load(class_type=item_type_to_return_to.map_model, **value)
                        value[key] = item
                    else:
                        item_keys_to_pop.append(key)
                else:
                    raise Exception(f"No map validator was found.")

            if load_data_into_objects is True:
                populated_object, kwargs_not_consumed = field_load(class_type=item_type_to_return_to.map_model, **value)
                print(populated_object)
        else:
            item_keys_to_pop: List[str] = list()
            for key, item in value.items():
                if dict_excepted_key_type is not None:
                    key_type = type(key)
                    if not _types_match(type_to_check=key_type, expected_type=dict_excepted_key_type):
                        print(exceptions_with_vars_message(
                            message=f"Key of an item in a dict did not match expected key type. Item will be removed from data.",
                            vars_dict={"key": key, "item": item, "keyType": key_type, "expectedKeyType": dict_excepted_key_type}
                        ))
                        item_keys_to_pop.append(key)
                        continue

                if dict_value_excepted_type is not None:
                    if MapModel in dict_value_excepted_type.__bases__:
                        item_type = type(item)
                        if not _types_match(type_to_check=item_type, expected_type=dict):
                            print(exceptions_with_vars_message(
                                message=f"Received data that should be set inside a nested MapModel was not of type dict. Item will be removed from data.",
                                vars_dict={"key": key, "item": item, "itemType": item_type}
                            ))
                            item_keys_to_pop.append(key)
                            continue
                        item: dict

                        element_item_keys_to_pop: List[str] = list()
                        for element_item_key, element_item_value in item.items():
                            element_item_matching_validation_model_variable: Optional[BaseItem] = dict_value_excepted_type.__dict__.get(element_item_key, None)
                            if element_item_matching_validation_model_variable is not None:
                                element_item_value = validate_data(
                                    value=element_item_value, item_type_to_return_to=element_item_matching_validation_model_variable,
                                    expected_value_type=element_item_matching_validation_model_variable.field_type,
                                    load_data_into_objects=load_data_into_objects
                                )
                                if element_item_value is not None:
                                    if load_data_into_objects is True:
                                        element_item_value, kwargs_not_consumed = field_load(class_instance=item_type_to_return_to, **element_item_value)
                                    item[element_item_key] = element_item_value
                                else:
                                    if element_item_matching_validation_model_variable.required is not True:
                                        element_item_keys_to_pop.append(element_item_key)
                                    else:
                                        item_keys_to_pop.append(key)
                                        break
                            else:
                                element_item_keys_to_pop.append(element_item_key)
                                print(exceptions_with_vars_message(
                                    message=f"No map validator was found in a nested item of a dict. Item will be removed from data.",
                                    vars_dict={"elementItemKey": element_item_key, "elementItemValue": element_item_value}
                                ))
                        for element_item_key_to_pop in element_item_keys_to_pop:
                            item.pop(element_item_key_to_pop)
                    else:
                        if not _types_match(type_to_check=type(item), expected_type=dict_value_excepted_type):
                            item_keys_to_pop.append(key)
                            print(exceptions_with_vars_message(
                                message=f"Value of nested item of dict did not match expected type. Item will be removed from data.",
                                vars_dict={"item": item, "itemKey": key, "expectedItemValueType": dict_value_excepted_type}
                            ))
                else:
                    if load_data_into_objects is True:
                        item, kwargs_not_consumed = field_load(class_type=item_type_to_return_to.map_model, **value)
                    value[key] = item

        for item_key_to_pop in item_keys_to_pop:
            value.pop(item_key_to_pop)


    elif value_type == list:
        value: list
        if list_items_models is not None:
            indexes_to_pop: List[int] = list()
            for i, item in enumerate(value):
                matching_validation_model_variable: Optional[BaseItem] = map_model.__dict__.get(key, None)
                if matching_validation_model_variable is not None:
                    item = validate_data(
                        value=item, expected_value_type=matching_validation_model_variable.field_type,
                        load_data_into_objects=load_data_into_objects
                    )
                    if item is None:
                        indexes_to_pop.append(i)
                else:
                    indexes_to_pop.append(i)
                    print(exceptions_with_vars_message(
                        message=f"No map validator was found in a nested item of a list. Value will be removed from data.",
                        vars_dict={"listValue": value, "item": item, "itemIndex": i}
                    ))

    return value


def _types_match(type_to_check: type, expected_type: type) -> bool:
    if type_to_check != expected_type:
        return False
    return True

def _raise_if_types_did_not_match(type_to_check: type, expected_type: type):
    raise Exception(f"Deprecated")
    if type_to_check != expected_type:
        raise Exception(f"Data validation exception. The types of an item did not match"
                        f"\n  type_to_check:{type_to_check}"
                        f"\n  expected_type:{expected_type}")