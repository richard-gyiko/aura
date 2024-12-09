from datetime import date
import unittest

from .tools.lancedb.entity_create import LanceDBCreateEntity
from .tools.lancedb.schema_create import LanceDBCreateSchema


class TestLanceDB(unittest.TestCase):
    def test_create_employee_schema_and_entity(self):
        # Test schema creation
        schema_description = "A table schema for storing employee information (name, age, salary, hire_date). Table should be called 'employees'."
        schema_tool = LanceDBCreateSchema()
        schema_result = schema_tool._run(schema_description)
        self.assertIsNotNone(schema_result)
        self.assertIn("Successfully created schema", schema_result)

        # Test entity creation
        entity_tool = LanceDBCreateEntity()
        test_data = {
            "name": "John Doe",
            "age": 30,
            "salary": 50000,
            "hire_date": date(2022, 2, 2)
        }
        add_result = entity_tool._run("employees", test_data)
        self.assertIsNotNone(add_result)
        self.assertIn("Entity created successfully", add_result)


if __name__ == '__main__':
    unittest.main()
