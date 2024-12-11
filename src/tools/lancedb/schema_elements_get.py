from __future__ import annotations

import logging
from typing import Optional

from autogen_core.application.logging import TRACE_LOGGER_NAME
from langchain.callbacks.manager import CallbackManagerForToolRun
from pydantic import BaseModel, Field

from ._base import LanceDbTool


class GetSchemaElementsSchema(BaseModel):
    table_name: str = Field(
        description="Name of the table whose schema elements and info to retrieve"
    )


class LanceDBGetSchemaElements(LanceDbTool):
    name: str = "get_lancedb_schema_elements"
    description: str = (
        "Use this tool to get the schema elements/columns and info for a specific table in LanceDB. "
        "Returns a formatted string describing the fields and their types."
    )
    args_schema: type[BaseModel] = GetSchemaElementsSchema

    _logger = logging.getLogger(f"{TRACE_LOGGER_NAME}.{name}")

    def _run(
        self,
        table_name: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            schema_info = self.get_schema_info(table_name)
            if not schema_info:
                raise ValueError(f"No schema found for table '{table_name}'")

            elements_str = schema_info.schema_elements_to_str(
                schema_info.schema_elements
            )
            return (
                f"Schema elements for table '{table_name}':\n"
                f"Description: {schema_info.description}\n"
                f"Elements:\n{elements_str}"
            )
        except Exception as e:
            self._logger.error(f"Failed to get schema elements: {str(e)}")
            raise

    async def _arun(
        self,
        table_name: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("Async version not implemented")
