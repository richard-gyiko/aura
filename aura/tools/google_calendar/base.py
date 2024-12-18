from typing import TYPE_CHECKING

from langchain_community.tools.gmail.utils import (
    build_resource_service,
)
from langchain_core.tools import BaseTool
from pydantic import Field


if TYPE_CHECKING:
    # This is for linting and IDE typehints
    from googleapiclient.discovery import Resource
else:
    try:
        # We do this so pydantic can resolve the types when instantiating
        from googleapiclient.discovery import Resource
    except ImportError:
        pass


class GoogleCalendarBaseTool(BaseTool):
    """Base class for Google Calendar tools."""

    api_resource: Resource = Field(default_factory=build_resource_service)

    @classmethod
    def from_api_resource(cls, api_resource: Resource) -> "GoogleCalendarBaseTool":
        """Create a tool from an api resource.

        Args:
            api_resource: The api resource to use.

        Returns:
            A tool.
        """
        return cls(api_resource=api_resource)
