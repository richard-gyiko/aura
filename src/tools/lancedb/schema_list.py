from __future__ import annotations

import logging
from typing import List, Optional

from autogen_core.application.logging import TRACE_LOGGER_NAME
from langchain.callbacks.manager import CallbackManagerForToolRun
import pandas as pd
from pydantic import BaseModel

from ._base import LanceDbTool
from ._types import SchemaInfo


class ListSchemasSchema(BaseModel):
    """Empty schema as this tool takes no arguments"""

    pass


class LanceDBListSchemas(LanceDbTool):
    name: str = "list_lancedb_schemas"
    description: str = (
        "Use this tool to list all available schemas in the LanceDB instance. "
        "Returns information about table names, descriptions and their Apache Arrow schemas."
    )
    args_schema: type[BaseModel] = ListSchemasSchema

    _logger = logging.getLogger(f"{TRACE_LOGGER_NAME}.{name}")

    def _run(
        self,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> List[SchemaInfo]:
        try:
            table = self.get_schema_info_table()
            results: pd.DataFrame = table.to_pandas()

            return [SchemaInfo(**row) for _, row in results.iterrows()]
        except Exception as e:
            self._logger.error(f"Failed to list schemas: {str(e)}")
            raise

    async def _arun(
        self,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> List[SchemaInfo]:
        raise NotImplementedError("Async version not implemented")
