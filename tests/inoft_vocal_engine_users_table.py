import unittest
from typing import Dict, List, Optional
from StructNoSQL import BaseTable, BaseField, MapModel, MapField, TableDataModel, PrimaryIndex, GlobalSecondaryIndex


class TablesOperationsTests(unittest.TestCase):
    def test_users_table(self):

        class UsersTableModel(TableDataModel):
            accountId = BaseField(name="accountId", field_type=str)
            class ProjectModel(MapModel):
                projectName = BaseField(name="projectName", field_type=str, required=False)
                class InstancesInfosModel(MapModel):
                    ya = BaseField(name="ya", field_type=str)
                instancesInfos = MapField(name="instancesInfos", model=InstancesInfosModel)
            projects = BaseField(name="projects", field_type=Dict[str, ProjectModel], key_name="projectId")

        class UsersTable(BaseTable):
            def __init__(self):
                primary_index = PrimaryIndex(hash_key_name="accountId", hash_key_variable_python_type=str)
                globals_secondary_indexes = [
                    GlobalSecondaryIndex(hash_key_name="username", hash_key_variable_python_type=str, projection_type="ALL"),
                    GlobalSecondaryIndex(hash_key_name="email", hash_key_variable_python_type=str, projection_type="ALL"),
                ]
                super().__init__(table_name="inoft-vocal-engine_accounts-data", region_name="eu-west-2", data_model=UsersTableModel(),
                                 primary_index=primary_index, global_secondary_indexes=globals_secondary_indexes, auto_create_table=True)

        users_table = UsersTable()
        projects: List[dict] = list((
            users_table.model.projects.query(key_name="accountId", key_value="5ae5938d-d4b5-41a7-ad33-40f3c1476211").first_value()
        ).values())
        for project in projects:
            # self.assertIn(project["projectName"], ["Anvers 1944"])
            print(f"Project : {project}")

        response_data: Optional[str] = users_table.model.projects.projectName.query(
            key_name="accountId", key_value="5ae5938d-d4b5-41a7-ad33-40f3c1476211",
            query_kwargs={"projectId": "dfb5d805-8f8a-4343-a0c2-b511b4cb0de6"}
        ).first_value()
        print(response_data)



if __name__ == '__main__':
    unittest.main()
