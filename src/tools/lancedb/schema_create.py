from __future__ import annotations

import logging
from typing import Optional

from autogen_core.application.logging import TRACE_LOGGER_NAME
from langchain.callbacks.manager import CallbackManagerForToolRun
from pydantic import BaseModel, Field

from ._base import LanceDbTool
from ._schema import generate_schema_info, to_pyarrows_schema


class CreateSchemaSchema(BaseModel):
    description: str = Field(
        description="Description of the table's purpose and contents"
    )


class LanceDBCreateSchema(LanceDbTool):
    name: str = "create_lancedb_schema"
    description: str = (
        "Use this tool to create a new table schema in LanceDB. "
        "Requires table name, description, and Apache Arrow schema string."
    )
    args_schema: type[BaseModel] = CreateSchemaSchema

    _logger = logging.getLogger(f"{TRACE_LOGGER_NAME}.{name}")

    def _run(
        self,
        description: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            # Create schema info entry
            schema_info_response = generate_schema_info(description)
            result = to_pyarrows_schema(
                schema_info_response.schema_elements, vector_size=1536
            )

            print(result)
            self._logger.info(f"Generated pyarrow schema: {result}")

            # Store schema info
            schema_table = self.get_schema_info_table()
            schema_table.add([schema_info_response.to_schema_info()])

            # Create actual table with schema
            db = self._get_db()
            db.create_table(schema_info_response.table_name, schema=result)

            return f"Successfully created schema '{schema_info_response.table_name}'"
        except Exception as e:
            self._logger.error(f"Failed to create schema: {str(e)}")
            raise

    async def _arun(
        self,
        description: str,
        apache_arrow_schema: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("Async version not implemented")
