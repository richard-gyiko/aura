from typing import List

from langchain_community.agent_toolkits.base import BaseToolkit
from langchain_core.tools import BaseTool

from .entity_create import LanceDBCreateEntity
from .entity_delete import LanceDBDeleteEntity
from .entity_get import LanceDBGetEntity
from .entity_search import LanceDBSearchEntity
from .entity_update import LanceDBUpdateEntity
from .schema_create import LanceDBCreateSchema
from .schema_delete import LanceDBDeleteSchema
from .schema_list import LanceDBListSchemas


class LanceDbToolkit(BaseToolkit):
    """Toolkit for interacting with LanceDB."""

    db_path: str = ".lancedb"

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        return [
            LanceDBCreateEntity(),
            LanceDBDeleteEntity(),
            LanceDBGetEntity(),
            LanceDBSearchEntity(),
            LanceDBUpdateEntity(),
            LanceDBCreateSchema(),
            LanceDBDeleteSchema(),
            LanceDBListSchemas(),
        ]
