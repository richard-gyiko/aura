from __future__ import annotations

import logging
from typing import Optional

from autogen_core.application.logging import TRACE_LOGGER_NAME
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain_google_community.gmail.base import GmailBaseTool
from pydantic import BaseModel, Field


class EditLabelSchema(BaseModel):
    label_id: str = Field(
        description="The ID of the label to edit"
    )
    new_name: Optional[str] = Field(
        default=None,
        description="The new display name for the label"
    )
    message_list_visibility: Optional[str] = Field(
        default=None,
        description="Show/hide the label in the message list [show, hide]"
    )
    label_list_visibility: Optional[str] = Field(
        default=None,
        description="Show/hide the label in the label list [labelShow, labelHide]"
    )


class GmailEditLabel(GmailBaseTool):
    """Tool for editing existing Gmail labels.

    This tool allows modification of existing labels including their name
    and visibility settings.
    """

    name: str = "edit_gmail_label"
    description: str = (
        "Use this tool to modify an existing label in Gmail. "
        "You can change the label name and visibility settings."
    )
    args_schema: type[BaseModel] = EditLabelSchema

    _logger = logging.getLogger(f"{TRACE_LOGGER_NAME}.{name}")

    def _run(
        self,
        label_id: str,
        new_name: Optional[str] = None,
        message_list_visibility: Optional[str] = None,
        label_list_visibility: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            # Get current label to update only changed fields
            current_label = (
                self.api_resource.users()
                .labels()
                .get(userId='me', id=label_id)
                .execute()
            )

            # Update only provided fields
            if new_name is not None:
                current_label['name'] = new_name
            if message_list_visibility is not None:
                current_label['messageListVisibility'] = message_list_visibility
            if label_list_visibility is not None:
                current_label['labelListVisibility'] = label_list_visibility

            result = (
                self.api_resource.users()
                .labels()
                .update(userId='me', id=label_id, body=current_label)
                .execute()
            )

            return f"Label updated successfully. ID: {result['id']}, Name: {result['name']}"

        except Exception as e:
            self._logger.error(f"Failed to edit label: {str(e)}")
            raise

    async def _arun(
        self,
        label_id: str,
        new_name: Optional[str] = None,
        message_list_visibility: Optional[str] = None,
        label_list_visibility: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("Async version of this tool is not implemented.")
