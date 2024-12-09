from __future__ import annotations

import logging
from typing import List, Optional

from autogen_core.application.logging import TRACE_LOGGER_NAME
from langchain.callbacks.manager import CallbackManagerForToolRun
from pydantic import BaseModel, Field

from ._base import LanceDbTool
from ._filters import build_where_clause, FilterCondition


class DeleteEntitySchema(BaseModel):
    table_name: str = Field(description="The name of the table to delete entities from")
    conditions: List[FilterCondition] = Field(
        description="List of filter conditions that must ALL be met for rows to be deleted"
    )


class LanceDBDeleteEntity(LanceDbTool):
    """Tool for deleting entities from LanceDB tables.

    This tool allows deletion of entities from specified LanceDB tables.
    """

    name: str = "delete_lancedb_entity"
    description: str = (
        "Use this tool to delete entities from a LanceDB table. "
        "You need to specify the table name and filter conditions to identify entities to delete."
    )
    args_schema: type[BaseModel] = DeleteEntitySchema

    _logger = logging.getLogger(f"{TRACE_LOGGER_NAME}.{name}")

    def _run(
        self,
        table_name: str,
        conditions: List[FilterCondition],
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            table = self.open_table(table_name)
            where_clause = build_where_clause(conditions)

            # Execute delete operation
            deleted_count = table.delete(where_clause)
            return f"Deleted {deleted_count} entities from table {table} where {where_clause}"

        except Exception as e:
            self._logger.error(f"Failed to delete entities: {str(e)}")
            raise

    async def _arun(
        self,
        table: str,
        conditions: List[FilterCondition],
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("Async version not implemented")
