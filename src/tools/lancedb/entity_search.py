from __future__ import annotations

import logging
from typing import List, Optional

from autogen_core.application.logging import TRACE_LOGGER_NAME
from langchain.callbacks.manager import CallbackManagerForToolRun
from litellm import embedding
from pydantic import BaseModel, Field

from ._base import LanceDbTool
from ._filters import build_where_clause, FilterCondition


class SearchEntitySchema(BaseModel):
    table_name: str = Field(description="The name of the table to search entities in")
    query: str = Field(
        description="Query vector to find similar entities using vector similarity search"
    )
    limit: int = Field(default=10, description="Maximum number of results to return")
    conditions: Optional[List[FilterCondition]] = Field(
        None,
        description="Optional pre-filter conditions that must ALL be met before semantic search",
    )


class LanceDBSearchEntity(LanceDbTool):
    """Tool for searching entities in LanceDB tables using vector similarity.

    This tool allows vector similarity search in specified LanceDB tables using query vectors.
    """

    name: str = "search_lancedb_entity"
    description: str = (
        "Use this tool to search for entities in a LanceDB table using vector similarity search. "
        "Provide a query to find similar vectors in the table. "
        "Optional pre-filters can be applied before the semantic search. "
        "Specify the table name, search text, and optionally filter conditions and result limit."
    )
    args_schema: type[BaseModel] = SearchEntitySchema

    _logger = logging.getLogger(f"{TRACE_LOGGER_NAME}.{name}")

    def _run(
        self,
        table_name: str,
        query: str,
        limit: int = 10,
        conditions: Optional[List[FilterCondition]] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            table = self.open_table(table_name)

            # Get schema info for embedding handling
            schema_info = self.get_schema_info(table_name)
            if not schema_info:
                raise ValueError(f"No schema found for table {table_name}")

            # Generate embedding for query
            embedding_response = embedding(
                model="text-embedding-3-small",
                input=query,
                dimensions=1536,
            )
            query_vector = embedding_response.data[0]["embedding"]

            # Start with base vector search
            db_query = table.search(query_vector)

            # Apply pre-filters if specified
            if conditions:
                where_clause = build_where_clause(conditions)
                db_query = db_query.where(where_clause)

            # Execute search with limit
            results = db_query.limit(limit).to_list()

            prefilter_msg = (
                f" with pre-filter {build_where_clause(conditions)}"
                if conditions
                else ""
            )
            return f"Found {len(results)} entities in table {table} using vector similarity search{prefilter_msg}: {results}"

        except Exception as e:
            self._logger.error(f"Failed to search entities: {str(e)}")
            raise

    async def _arun(
        self,
        table_name: str,
        query: str,
        limit: int = 10,
        conditions: Optional[List[FilterCondition]] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("Async version not implemented")
