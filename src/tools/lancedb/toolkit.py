from typing import List

from langchain_community.agent_toolkits.base import BaseToolkit
from langchain_core.tools import BaseTool

from .entity_create import LanceDBCreateEntity
from .entity_delete import LanceDBDeleteEntity
from .entity_get import LanceDBGetEntity
from .entity_search import LanceDBSearchEntity
from .entity_update import LanceDBUpdateEntity
from .schema_add_column import LanceDBAddColumn
from .schema_create import LanceDBCreateSchema
from .schema_delete import LanceDBDeleteSchema
from .schema_drop_column import LanceDBDropColumn
from .schema_list import LanceDBListSchemas


class LanceDbToolkit(BaseToolkit):
    """Toolkit for interacting with LanceDB."""

    db_path: str = "./.lancedb"

    def __init__(self, db_path: str = ".lancedb"):
        self.db_path = db_path

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        return [
            LanceDBCreateEntity(db_path=self.db_path),
            LanceDBDeleteEntity(db_path=self.db_path),
            LanceDBGetEntity(db_path=self.db_path),
            LanceDBSearchEntity(db_path=self.db_path),
            LanceDBUpdateEntity(db_path=self.db_path),
            LanceDBCreateSchema(db_path=self.db_path),
            LanceDBDeleteSchema(db_path=self.db_path),
            LanceDBListSchemas(db_path=self.db_path),
            LanceDBAddColumn(db_path=self.db_path),
            LanceDBDropColumn(db_path=self.db_path),
        ]
