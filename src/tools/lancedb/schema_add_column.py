from __future__ import annotations

import logging
from typing import Optional

from autogen_core.application.logging import TRACE_LOGGER_NAME
from langchain.callbacks.manager import CallbackManagerForToolRun
from pydantic import BaseModel, Field

from ._base import LanceDbTool
from ._types import SchemaElement


class AddColumnSchema(BaseModel):
    table_name: str = Field(description="Name of the table to modify")
    column_name: str = Field(description="Name of the new column to add")
    column_type: str = Field(description="Data type of the new column")
    column_description: str = Field(
        description="Description of the new column's purpose"
    )


class LanceDBAddColumn(LanceDbTool):
    name: str = "add_column_to_schema"
    description: str = (
        "Use this tool to add a new column to an existing table schema in LanceDB. "
        "Requires table name, column name, data type, and column description."
    )
    args_schema: type[BaseModel] = AddColumnSchema

    _logger = logging.getLogger(f"{TRACE_LOGGER_NAME}.{name}")

    def _run(
        self,
        table_name: str,
        column_name: str,
        column_type: str,
        column_description: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            # Get existing schema info
            schema_info = self.get_schema_info(table_name)
            if not schema_info:
                raise ValueError(f"Table '{table_name}' not found")

            # Create new schema element
            new_column = SchemaElement(
                field_name=column_name,
                data_type=column_type,
                embedded=False,  # Default to false for new columns
            )

            # Add new column to schema
            elements = schema_info.schema_elements
            elements.append(new_column)
            schema_info.update_schema_elements(elements)

            # Update schema info table
            schema_table = self.get_schema_info_table()
            schema_table.add([schema_info], mode="overwrite")

            # Update actual table schema
            db = self._get_db()
            table = db.open_table(table_name)
            table.add_columns({column_name: f"CAST(NULL as {column_type})"})

            return f"Successfully added column '{column_name}' to table '{table_name}'"
        except Exception as e:
            self._logger.error(f"Failed to add column: {str(e)}")
            raise

    async def _arun(
        self,
        table_name: str,
        column_name: str,
        column_type: str,
        column_description: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("Async version not implemented")
