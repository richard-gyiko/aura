from __future__ import annotations

import logging
from typing import Optional, Type

from autogen_core.application.logging import TRACE_LOGGER_NAME
from googleapiclient.errors import HttpError
from langchain.callbacks.manager import CallbackManagerForToolRun
from pydantic import BaseModel, Field

from .base import GoogleCalendarBaseTool


class DeleteEventSchema(BaseModel):
    event_id: str = Field(
        description="The unique identifier for the calendar event to delete"
    )
    calendar_id: str = Field(
        default="primary",
        description="The calendar ID. Use 'primary' for the primary calendar.",
    )
    send_updates: Optional[str] = Field(
        default="all",
        description=(
            "Guests who should receive notifications about the deletion of the event. "
            "Possible values are: 'all' to notify all guests, 'externalOnly' to notify only "
            "non-Google Calendar guests, or 'none' to send no notifications."
        ),
    )


class GoogleCalendarDeleteEvent(GoogleCalendarBaseTool):
    """Tool for deleting events from Google Calendar.

    This tool allows deletion of calendar events using their event ID.
    By default it operates on the user's primary calendar but can be used
    with other calendars by specifying the calendar ID.
    """

    name: str = "delete_google_calendar_event"
    description: str = (
        "Use this tool to delete an existing calendar event."
        " You need to provide the event ID to delete the specific event."
        " The event ID can be obtained from the list_google_calendar_events tool."
    )
    args_schema: Type[BaseModel] = DeleteEventSchema

    _logger = logging.getLogger(f"{TRACE_LOGGER_NAME}.{name}")

    def _run(
        self,
        event_id: str,
        calendar_id: str = "primary",
        send_updates: str = "all",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            self.api_resource.events().delete(
                calendarId=calendar_id, eventId=event_id, sendUpdates=send_updates
            ).execute()

            return f"Successfully deleted event {event_id}"
        except HttpError as error:
            self._logger.error(f"Failed to delete calendar event: {error}")
            raise
        except Exception as e:
            self._logger.error(f"Unexpected error deleting calendar event: {str(e)}")
            raise

    async def _arun(
        self,
        event_id: str,
        calendar_id: str = "primary",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("Async version of this tool is not implemented.")
