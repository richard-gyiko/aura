from __future__ import annotations

import logging
from typing import Optional

from autogen_core import TRACE_LOGGER_NAME
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain_google_community.gmail.base import GmailBaseTool
from pydantic import BaseModel, Field


class DeleteLabelSchema(BaseModel):
    label_id: str = Field(description="The ID of the label to delete")


class GmailDeleteLabel(GmailBaseTool):
    """Tool for deleting Gmail labels.

    This tool allows deletion of user-created labels from Gmail.
    System labels cannot be deleted.
    """

    name: str = "delete_gmail_label"
    description: str = (
        "Use this tool to delete a label from Gmail. "
        "Note: System labels cannot be deleted."
    )
    args_schema: type[BaseModel] = DeleteLabelSchema

    _logger = logging.getLogger(f"{TRACE_LOGGER_NAME}.{name}")

    def _run(
        self,
        label_id: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            self.api_resource.users().labels().delete(
                userId="me", id=label_id
            ).execute()

            return f"Label {label_id} deleted successfully."

        except Exception as e:
            self._logger.error(f"Failed to delete label: {str(e)}")
            raise

    async def _arun(
        self,
        label_id: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("Async version of this tool is not implemented.")
