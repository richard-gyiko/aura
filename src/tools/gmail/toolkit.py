from __future__ import annotations

from typing import List, TYPE_CHECKING

from langchain_community.agent_toolkits.base import BaseToolkit
from langchain_core.tools import BaseTool
from langchain_google_community.gmail.utils import (
    build_resource_service,
)
from pydantic import ConfigDict, Field


from .create_label import GmailCreateLabel
from .delete_label import GmailDeleteLabel
from .edit_label import GmailEditLabel
from .list_labels import GmailListLabels
from .modify_email_labels import GmailModifyEmailLabels


if TYPE_CHECKING:
    # This is for linting and IDE typehints
    from googleapiclient.discovery import Resource  # type: ignore[import]
else:
    try:
        # We do this so pydantic can resolve the types when instantiating
        from googleapiclient.discovery import Resource
    except ImportError:
        pass


SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]


class GmailToolkitExt(BaseToolkit):
    """Toolkit for interacting with Gmail.

    *Security Note*: This toolkit contains tools that can read and modify
        the state of a service; e.g., by reading, creating, updating, deleting
        data associated with this service.

        For example, this toolkit can be used to send emails on behalf of the
        associated account.

        See https://python.langchain.com/docs/security for more information.
    """

    api_resource: Resource = Field(default_factory=build_resource_service)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        return [
            GmailCreateLabel(api_resource=self.api_resource),
            GmailDeleteLabel(api_resource=self.api_resource),
            GmailEditLabel(api_resource=self.api_resource),
            GmailListLabels(api_resource=self.api_resource),
            GmailModifyEmailLabels(api_resource=self.api_resource),
        ]
