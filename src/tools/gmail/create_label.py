from __future__ import annotations

import logging
from typing import Optional

from autogen_core.application.logging import TRACE_LOGGER_NAME
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain_google_community.gmail.base import GmailBaseTool
from pydantic import BaseModel, Field


class CreateLabelSchema(BaseModel):
    name: str = Field(description="The display name of the label to create")
    message_list_visibility: Optional[str] = Field(
        default="show",
        description="Show/hide the label in the message list [show, hide]",
    )
    label_list_visibility: Optional[str] = Field(
        default="labelShow",
        description="Show/hide the label in the label list [labelShow, labelHide]",
    )


class GmailCreateLabel(GmailBaseTool):
    """Tool for creating new Gmail labels.

    This tool allows creation of new labels in Gmail with customizable
    visibility settings.
    """

    name: str = "create_gmail_label"
    description: str = (
        "Use this tool to create a new label in Gmail. "
        "You can specify the label name and visibility settings."
    )
    args_schema: type[BaseModel] = CreateLabelSchema

    _logger = logging.getLogger(f"{TRACE_LOGGER_NAME}.{name}")

    def _run(
        self,
        name: str,
        message_list_visibility: str = "show",
        label_list_visibility: str = "labelShow",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            label = {
                "name": name,
                "messageListVisibility": message_list_visibility,
                "labelListVisibility": label_list_visibility,
            }

            result = (
                self.api_resource.users()
                .labels()
                .create(userId="me", body=label)
                .execute()
            )

            return f"Label created successfully. ID: {result['id']}, Name: {result['name']}"

        except Exception as e:
            self._logger.error(f"Failed to create label: {str(e)}")
            raise

    async def _arun(
        self,
        name: str,
        message_list_visibility: str = "show",
        label_list_visibility: str = "labelShow",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("Async version of this tool is not implemented.")
