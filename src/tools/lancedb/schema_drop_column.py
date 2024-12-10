from __future__ import annotations

import logging
from typing import Optional

from autogen_core.application.logging import TRACE_LOGGER_NAME
from langchain.callbacks.manager import CallbackManagerForToolRun
from pydantic import BaseModel, Field

from ._base import LanceDbTool


class DropColumnSchema(BaseModel):
    table_name: str = Field(description="Name of the table to modify")
    column_name: str = Field(description="Name of the column to drop")


class LanceDBDropColumn(LanceDbTool):
    name: str = "drop_column_from_schema"
    description: str = (
        "Use this tool to remove a column from an existing table schema in LanceDB. "
        "Requires table name and column name."
    )
    args_schema: type[BaseModel] = DropColumnSchema

    _logger = logging.getLogger(f"{TRACE_LOGGER_NAME}.{name}")

    def _run(
        self,
        table_name: str,
        column_name: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            # Get existing schema info
            schema_info = self.get_schema_info(table_name)
            if not schema_info:
                raise ValueError(f"Table '{table_name}' not found")

            # Remove the column from schema elements
            elements = schema_info.schema_elements
            original_length = len(elements)
            updated_elements = [
                element for element in elements if element.field_name != column_name
            ]

            if len(updated_elements) == original_length:
                raise ValueError(
                    f"Column '{column_name}' not found in table '{table_name}'"
                )

            # Update schema elements and schema info table
            schema_info.update_schema_elements(updated_elements)
            schema_table = self.get_schema_info_table()
            schema_table.add([schema_info], mode="overwrite")

            # Update actual table schema
            db = self._get_db()
            table = db.open_table(table_name)
            table.drop_columns([column_name])

            return (
                f"Successfully dropped column '{column_name}' from table '{table_name}'"
            )
        except Exception as e:
            self._logger.error(f"Failed to drop column: {str(e)}")
            raise

    async def _arun(
        self,
        table_name: str,
        column_name: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("Async version not implemented")
