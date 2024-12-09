from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from autogen_core.application.logging import TRACE_LOGGER_NAME
from langchain.callbacks.manager import CallbackManagerForToolRun
from litellm import embedding
from pydantic import BaseModel, Field

from ._base import LanceDbTool


class CreateEntitySchema(BaseModel):
    table: str = Field(description="The name of the table to create the entity in")
    data: Dict[str, Any] = Field(description="The entity data to insert")


class LanceDBCreateEntity(LanceDbTool):
    """Tool for creating new entities in LanceDB tables.

    This tool allows creation of new entities in specified LanceDB tables.
    """

    name: str = "create_lancedb_entity"
    description: str = (
        "Use this tool to create a new entity in a LanceDB table. "
        "You need to specify the table name and the entity data."
    )
    args_schema: type[BaseModel] = CreateEntitySchema

    _logger = logging.getLogger(f"{TRACE_LOGGER_NAME}.{name}")

    def _run(
        self,
        table: str,
        data: Dict[str, Any],
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            schema_info = self.get_schema_info(table)
            if not schema_info:
                raise ValueError(f"No schema found for table {table}")

            embedded_fields = [
                field for field in schema_info.schema_elements if field.embedded
            ]

            # Handle embeddings
            if (len(embedded_fields) > 0) and (len(data) > 0):
                embedding_text = ""

                for field in embedded_fields:
                    if field.field_name in data:
                        embedding_text += f" {data[field.field_name]}"

                embedding_response = embedding(
                    model="text-embedding-3-small",
                    input=embedding_text,
                    dimensions=1536,
                )
                data["vector"] = embedding_response.data[0]["embedding"]

            db = self.open_table(table)

            # Convert data to DataFrame using schema-aware conversion from SchemaInfo
            df = schema_info.create_dataframe(data)

            # Add data to table
            db.add(df)

            # Here we would connect to LanceDB and insert the data
            # This is a placeholder for actual implementation
            return f"Entity created successfully in table {table}"

        except Exception as e:
            self._logger.error(f"Failed to create entity: {str(e)}")
            raise

    async def _arun(
        self,
        table: str,
        data: Dict[str, Any],
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("Async version not implemented")
