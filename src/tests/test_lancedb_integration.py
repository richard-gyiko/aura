from datetime import datetime
from typing import List
import unittest

from ..tools.lancedb._filters import FilterCondition, FilterOperator
from ..tools.lancedb.entity_create import LanceDBCreateEntity
from ..tools.lancedb.entity_delete import LanceDBDeleteEntity
from ..tools.lancedb.entity_get import LanceDBGetEntity
from ..tools.lancedb.entity_search import LanceDBSearchEntity
from ..tools.lancedb.entity_update import LanceDBUpdateEntity
from ..tools.lancedb.schema_add_column import LanceDBAddColumn
from ..tools.lancedb.schema_create import LanceDBCreateSchema
from ..tools.lancedb.schema_delete import LanceDBDeleteSchema
from ..tools.lancedb.schema_drop_column import LanceDBDropColumn
from ..tools.lancedb.schema_list import LanceDBListSchemas


class TestLanceDBIntegration(unittest.TestCase):
    TEST_DB_PATH = "./.tests/lancedb"

    @classmethod
    def setUpClass(cls):
        """Set up test tools"""
        import os
        import shutil

        # Create test directory if it doesn't exist
        os.makedirs(os.path.dirname(cls.TEST_DB_PATH), exist_ok=True)

        # Remove any existing test database
        if os.path.exists(cls.TEST_DB_PATH):
            shutil.rmtree(cls.TEST_DB_PATH)

        cls.schema_tool = LanceDBCreateSchema(db_path=cls.TEST_DB_PATH)
        cls.create_tool = LanceDBCreateEntity(db_path=cls.TEST_DB_PATH)
        cls.get_tool = LanceDBGetEntity(db_path=cls.TEST_DB_PATH)
        cls.search_tool = LanceDBSearchEntity(db_path=cls.TEST_DB_PATH)
        cls.update_tool = LanceDBUpdateEntity(db_path=cls.TEST_DB_PATH)
        cls.delete_tool = LanceDBDeleteEntity(db_path=cls.TEST_DB_PATH)
        cls.list_schemas_tool = LanceDBListSchemas(db_path=cls.TEST_DB_PATH)
        cls.delete_schema_tool = LanceDBDeleteSchema(db_path=cls.TEST_DB_PATH)
        cls.add_column_tool = LanceDBAddColumn(db_path=cls.TEST_DB_PATH)
        cls.drop_column_tool = LanceDBDropColumn(db_path=cls.TEST_DB_PATH)

    def test_0_create_schema(self):
        """Test creating a new schema"""
        schema_description = "A table schema for storing employee information (name, age, salary, hire_date). Table should be called 'employees'."
        result = self.schema_tool._run(schema_description)
        self.assertIn("Successfully created schema", result)
        self.assertIn("employees", result)

        # Verify table exists by trying to open it
        try:
            self.create_tool.open_table("employees")
        except Exception as e:
            self.fail(f"Failed to open employees table after creation: {str(e)}")

    def test_2_create_entity(self):
        """Test creating a new employee entity"""
        test_data = {
            "name": "John Smith",
            "age": 35,
            "salary": 60000,
            "hire_date": datetime(2023, 1, 15),
        }
        result = self.create_tool._run("employees", test_data)
        self.assertIn("Entity created successfully", result)

    def test_3_get_entity(self):
        """Test retrieving an employee by name"""
        conditions: List[FilterCondition] = [
            FilterCondition(
                field="name", operator=FilterOperator.EQUALS, value="John Smith"
            )
        ]
        result = self.get_tool._run("employees", conditions)
        self.assertIn("Found 1 entities matching", result)
        self.assertIn("name: John Smith", result)
        self.assertIn("salary: 60000", result)

    def test_4_search_entity(self):
        """Test semantic search functionality"""
        result = self.search_tool._run(
            table_name="employees",
            query="experienced employee",
            limit=5,
        )
        self.assertIn("John Smith", result)

    def test_5_update_entity(self):
        """Test updating an employee's salary"""
        conditions: List[FilterCondition] = [
            FilterCondition(
                field="name", operator=FilterOperator.EQUALS, value="John Smith"
            )
        ]
        update_data = {
            "salary": 65000,
        }
        result = self.update_tool._run("employees", conditions, update_data)
        self.assertIn("Updated", result)

        # Verify update
        get_result = self.get_tool._run("employees", conditions)
        self.assertIn("65000", get_result)

    def test_6_delete_entity(self):
        """Test deleting an employee"""
        conditions: List[FilterCondition] = [
            FilterCondition(
                field="name", operator=FilterOperator.EQUALS, value="John Smith"
            )
        ]
        result = self.delete_tool._run("employees", conditions)
        self.assertIn("Deleted", result)

        # Verify deletion
        get_result = self.get_tool._run("employees", conditions)
        self.assertIn("Found 0 entities", get_result)

    def test_7_add_column(self):
        """Test adding a new column to the schema"""
        result = self.add_column_tool._run(
            table_name="employees",
            column_name="department",
            column_type="string",
            column_description="Employee's department",
        )
        self.assertIn("Successfully added column", result)

        # Verify column exists by creating a new record with the column
        test_data = {
            "name": "Jane Doe",
            "age": 28,
            "salary": 55000,
            "hire_date": datetime(2024, 1, 1),
            "department": "Engineering",
        }
        create_result = self.create_tool._run("employees", test_data)
        self.assertIn("Entity created successfully", create_result)

        # Verify retrieval with new column
        conditions = [
            FilterCondition(
                field="name", operator=FilterOperator.EQUALS, value="Jane Doe"
            )
        ]
        get_result = self.get_tool._run("employees", conditions)
        self.assertIn("department: Engineering", get_result)

    def test_8_drop_column(self):
        """Test dropping a column from the schema"""
        # First verify the department column exists
        conditions = [
            FilterCondition(
                field="name", operator=FilterOperator.EQUALS, value="Jane Doe"
            )
        ]
        get_result = self.get_tool._run("employees", conditions)
        self.assertIn("department:", get_result)

        # Now drop the column
        result = self.drop_column_tool._run(
            table_name="employees", column_name="department"
        )
        self.assertIn("Successfully dropped column", result)

        # Verify column is gone
        get_result = self.get_tool._run("employees", conditions)
        self.assertNotIn("department:", get_result)

    def test_1_list_schemas(self):
        """Test listing available schemas"""
        schemas = self.list_schemas_tool._run()
        self.assertTrue(
            len(schemas) >= 0, "Expected to be able to list schemas, even if empty"
        )


if __name__ == "__main__":
    unittest.main()
