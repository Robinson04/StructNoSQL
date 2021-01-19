import unittest
from StructNoSQL import BaseField, MapModel
from StructNoSQL.exceptions import InvalidFieldNameException
from tests.users_table import UsersTable, TEST_ACCOUNT_ID, TEST_PROJECT_ID, UsersTableModel


class TestReservedChars(unittest.TestCase):
    def test_left_bracket_char(self):
        def init_table():
            class TableModel:
                accountId = BaseField(name='accountId', field_type=str, required=True)
                restrictedRightBracket = BaseField(name='restrictedRightBracket_[e', field_type=str, required=False)
            users_table = UsersTable(data_model=TableModel())
        self.assertRaises(InvalidFieldNameException, init_table)

    def test_right_bracket_char(self):
        def init_table():
            class TableModel:
                accountId = BaseField(name='accountId', field_type=str, required=True)
                restrictedLeftBracket = BaseField(name='restrictedLeftBracket_]e', field_type=str, required=False)
            users_table = UsersTable(data_model=TableModel())
        self.assertRaises(InvalidFieldNameException, init_table)

    def test_left_curly_bracket_char(self):
        def init_table():
            class TableModel:
                accountId = BaseField(name='accountId', field_type=str, required=True)
                restrictedRightBracket = BaseField(name='restrictedRightBracket_{e', field_type=str, required=False)
            users_table = UsersTable(data_model=TableModel())
        self.assertRaises(InvalidFieldNameException, init_table)

    def test_right_curly_bracket_char(self):
        def init_table():
            class TableModel:
                accountId = BaseField(name='accountId', field_type=str, required=True)
                restrictedLeftBracket = BaseField(name='restrictedLeftBracket_}e', field_type=str, required=False)
            users_table = UsersTable(data_model=TableModel())
        self.assertRaises(InvalidFieldNameException, init_table)


if __name__ == '__main__':
    unittest.main()
