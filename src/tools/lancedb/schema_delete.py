from __future__ import annotations

import logging
from typing import Optional

from autogen_core.application.logging import TRACE_LOGGER_NAME
from langchain.callbacks.manager import CallbackManagerForToolRun
from pydantic import BaseModel, Field

from ._base import LanceDbTool


class DeleteSchemaSchema(BaseModel):
    table_name: str = Field(description="The name of the table to delete")


class LanceDBDeleteSchema(LanceDbTool):
    name: str = "delete_lancedb_schema"
    description: str = (
        "Use this tool to delete a table and its schema from LanceDB. "
        "This will permanently remove the table and all its data."
    )
    args_schema: type[BaseModel] = DeleteSchemaSchema

    _logger = logging.getLogger(f"{TRACE_LOGGER_NAME}.{name}")

    def _run(
        self,
        table_name: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            # Delete schema info
            schema_table = self.get_schema_info_table()
            schema_table.delete(f"table_name = '{table_name}'")

            # Delete actual table
            db = self._get_db()
            db.drop_table(table_name)

            return f"Successfully deleted table {table_name} and its schema"
        except Exception as e:
            self._logger.error(f"Failed to delete schema: {str(e)}")
            raise

    async def _arun(
        self,
        table_name: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("Async version not implemented")
