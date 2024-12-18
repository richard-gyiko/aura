from __future__ import annotations

import logging
from typing import Optional, Type

from autogen_core.application.logging import TRACE_LOGGER_NAME
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain_google_community.gmail.base import GmailBaseTool
from pydantic import BaseModel


class ListLabelsSchema(BaseModel):
    pass


class GmailListLabels(GmailBaseTool):
    """Tool for listing all Gmail labels.

    This tool retrieves all labels from the user's Gmail account,
    including system labels and user-created labels.
    """

    name: str = "list_gmail_labels"
    description: str = (
        "Use this tool to get a list of all labels in the Gmail account. "
        "Returns both system labels and user-created labels with their IDs."
    )
    args_schema: Type[BaseModel] = ListLabelsSchema

    _logger = logging.getLogger(f"{TRACE_LOGGER_NAME}.{name}")

    def _run(
        self,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            results = self.api_resource.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])

            if not labels:
                return "No labels found."

            label_info = []
            for label in labels:
                label_info.append(f"ID: {label['id']} - Name: {label['name']}")

            return "\n".join(label_info)

        except Exception as e:
            self._logger.error(f"Failed to list labels: {str(e)}")
            raise

    async def _arun(
        self,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("Async version of this tool is not implemented.")
