from __future__ import annotations

import logging
from typing import List, Optional

from autogen_core.application.logging import TRACE_LOGGER_NAME
from langchain.callbacks.manager import CallbackManagerForToolRun
from pydantic import BaseModel, Field

from ._base import LanceDbTool


class SearchEntitySchema(BaseModel):
    table: str = Field(description="The name of the table to search entities in")
    vector: List[float] = Field(description="The vector to search for similar entities")
    limit: int = Field(default=10, description="Maximum number of results to return")
    where: Optional[str] = Field(
        None, description="Optional SQL WHERE clause to filter results"
    )


class LanceDBSearchEntity(LanceDbTool):
    """Tool for searching entities in LanceDB tables using vector similarity.

    This tool allows vector similarity search in specified LanceDB tables.
    """

    name: str = "search_lancedb_entity"
    description: str = (
        "Use this tool to search for similar entities in a LanceDB table using vector similarity. "
        "You need to specify the table name, search vector, and optionally a WHERE clause and limit."
    )
    args_schema: type[BaseModel] = SearchEntitySchema

    _logger = logging.getLogger(f"{TRACE_LOGGER_NAME}.{name}")

    def _run(
        self,
        table: str,
        vector: List[float],
        limit: int = 10,
        where: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            table = self.open_table(table)

            # Here we would connect to LanceDB and perform vector search
            # This is a placeholder for actual implementation
            filter_msg = f" where {where}" if where else ""
            return f"Found {limit} similar entities in table {table}{filter_msg}"

        except Exception as e:
            self._logger.error(f"Failed to search entities: {str(e)}")
            raise

    async def _arun(
        self,
        table: str,
        vector: List[float],
        limit: int = 10,
        where: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("Async version not implemented")
