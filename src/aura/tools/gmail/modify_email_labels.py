from __future__ import annotations

import logging
from typing import List, Optional

from autogen_core import TRACE_LOGGER_NAME
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain_google_community.gmail.base import GmailBaseTool
from pydantic import BaseModel, Field


class ModifyEmailLabelsSchema(BaseModel):
    message_id: str = Field(
        description="The ID of the email message to modify labels for."
    )
    add_labels: Optional[List[str]] = Field(
        default=None,
        description="List of label IDs to add to the message. You can add up to 100 labels.",
    )
    remove_labels: Optional[List[str]] = Field(
        default=None,
        description="List of label IDs to remove from the message. You can remove up to 100 labels.",
    )


class GmailModifyEmailLabels(GmailBaseTool):
    """Tool for modifying labels on Gmail email messages.

    This tool allows adding and removing labels from existing Gmail email messages.
    You can modify up to 100 labels at a time.
    """

    name: str = "modify_gmail_email_labels"
    description: str = (
        "Use this tool to modify the labels on an existing Gmail message. "
        "You can add and/or remove labels using their label IDs. "
        "You can modify up to 100 labels in a single operation."
    )
    args_schema: type[BaseModel] = ModifyEmailLabelsSchema

    _logger = logging.getLogger(f"{TRACE_LOGGER_NAME}.{name}")

    def _run(
        self,
        message_id: str,
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            # Prepare the modification request
            body = {}
            if add_labels:
                body["addLabelIds"] = add_labels
            if remove_labels:
                body["removeLabelIds"] = remove_labels

            # Execute the modification
            result = (
                self.api_resource.users()
                .messages()
                .modify(userId="me", id=message_id, body=body)
                .execute()
            )

            # Return success message with updated label IDs
            return f"Successfully modified labels for message {message_id}. Current labels: {result.get('labelIds', [])}"

        except Exception as e:
            self._logger.error(f"Failed to modify labels: {str(e)}")
            raise

    async def _arun(
        self,
        message_id: str,
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("Async version of this tool is not implemented.")
