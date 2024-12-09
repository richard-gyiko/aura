from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from autogen_core.application.logging import TRACE_LOGGER_NAME
from langchain.callbacks.manager import CallbackManagerForToolRun
from litellm import embedding
from pydantic import BaseModel, Field

from ._base import LanceDbTool
from ._filters import build_where_clause, FilterCondition


class UpdateEntitySchema(BaseModel):
    table_name: str = Field(description="The name of the table to update the entity in")
    conditions: List[FilterCondition] = Field(
        description="List of filter conditions that must ALL be met for rows to be updated"
    )
    data: Dict[str, Any] = Field(description="The new data to update entities with")


class LanceDBUpdateEntity(LanceDbTool):
    """Tool for updating entities in LanceDB tables.

    This tool allows updating existing entities in specified LanceDB tables.
    """

    name: str = "update_lancedb_entity"
    description: str = (
        "Use this tool to update entities in a LanceDB table. "
        "You need to specify the table name, WHERE clause to identify entities, and the new data."
    )
    args_schema: type[BaseModel] = UpdateEntitySchema

    _logger = logging.getLogger(f"{TRACE_LOGGER_NAME}.{name}")

    def _run(
        self,
        table_name: str,
        conditions: List[FilterCondition],
        data: Dict[str, Any],
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            table = self.open_table(table_name)

            # Get schema info for proper data handling
            schema_info = self.get_schema_info(table_name)
            if not schema_info:
                raise ValueError(f"No schema found for table {table_name}")

            # Handle embeddings if needed
            embedded_fields = [
                field for field in schema_info.schema_elements if field.embedded
            ]
            if len(embedded_fields) > 0:
                embedding_text = ""
                for field in embedded_fields:
                    if field.field_name in data:
                        embedding_text += f" {data[field.field_name]}"

                if embedding_text:
                    embedding_response = embedding(
                        model="text-embedding-3-small",
                        input=embedding_text,
                        dimensions=1536,
                    )
                    data["vector"] = embedding_response.data[0]["embedding"]

            # Convert data using schema-aware conversion
            df = schema_info.create_dataframe(data)

            # Build where clause and execute update operation
            where_clause = build_where_clause(conditions)
            # Convert DataFrame to dict for update
            update_dict = df.iloc[0].to_dict()
            updated_count = table.update(where=where_clause, values=update_dict)
            return f"Updated {updated_count} entities in table {table} where {where_clause}"

        except Exception as e:
            self._logger.error(f"Failed to update entities: {str(e)}")
            raise

    async def _arun(
        self,
        table: str,
        conditions: List[FilterCondition],
        data: Dict[str, Any],
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("Async version not implemented")
