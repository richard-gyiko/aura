from __future__ import annotations

import logging
from typing import Optional, Type

from autogen_core.application.logging import TRACE_LOGGER_NAME
from langchain.callbacks.manager import CallbackManagerForToolRun
from pydantic import BaseModel, Field
from utils.timezone import get_local_timezone

from .base import GoogleCalendarBaseTool
from .utils import parse_and_format_datetime


class CreateEventSchema(BaseModel):
    # https://developers.google.com/calendar/api/v3/reference/events/insert

    # note: modifed the tz desc in the parameters, use local time automatically
    start_datetime: str = Field(
        description=(
            " The start datetime for the event in the following format: "
            ' YYYY-MM-DDTHH:MM:SS, where "T" separates the date and time '
            " components, "
            ' For example: "2023-06-09T10:30:00" represents June 9th, '
            " 2023, at 10:30 AM"
            "Do not include timezone info as it will be automatically processed."
        )
    )
    end_datetime: str = Field(
        description=(
            " The end datetime for the event in the following format: "
            ' YYYY-MM-DDTHH:MM:SS, where "T" separates the date and time '
            " components, "
            ' For example: "2023-06-09T10:30:00" represents June 9th, '
            " 2023, at 10:30 AM"
            "Do not include timezone info as it will be automatically processed."
        )
    )
    summary: str = Field(description="The title of the event.")
    location: Optional[str] = Field(
        default="", description="The location of the event."
    )
    description: Optional[str] = Field(
        default="", description="The description of the event. Optional."
    )
    timezone: Optional[str] = Field(
        default=None,
        description="The timezone in TZ Database Name format, e.g. 'America/New_York'. Defaults to the user's local timezone.",
    )
    attendees: Optional[list[str]] = Field(
        default=None,
        description="List of email addresses of attendees to invite to the event.",
    )


class GoogleCalendarCreateEvent(GoogleCalendarBaseTool):
    """Tool for creating events in Google Calendar.

    This tool allows creation of calendar events in the user's primary calendar
    with support for start/end times, title, location and description.
    All times are handled in the user's local timezone by default.
    """

    name: str = "create_google_calendar_event"
    description: str = (
        " Use this tool to create a new calendar event in user's primary calendar."
        " The input must be the start and end datetime for the event, and"
        " the title of the event. You can also specify the location and description"
    )
    args_schema: Type[BaseModel] = CreateEventSchema

    _logger = logging.getLogger(f"{TRACE_LOGGER_NAME}.{name}")

    def _run(
        self,
        start_datetime: str,
        end_datetime: str,
        summary: str,
        location: str = "",
        description: str = "",
        timezone: str = None,
        attendees: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            if timezone is None:
                zone_info = get_local_timezone()
                timezone = str(zone_info)

            start_rfc, end_rfc, timezone = parse_and_format_datetime(
                start_datetime, end_datetime, timezone
            )

            calendar = "primary"
            body = {
                "summary": summary,
                "start": {"dateTime": start_rfc, "timeZone": timezone},
                "end": {"dateTime": end_rfc, "timeZone": timezone},
            }

            if location != "":
                body["location"] = location
            if description != "":
                body["description"] = description

            if attendees:
                body["attendees"] = [{"email": email} for email in attendees]

            event = (
                self.api_resource.events()
                .insert(calendarId=calendar, body=body)
                .execute()
            )

            return f"Event created: {event.get('htmlLink')} (ID: {event.get('id')})"
        except Exception as e:
            self._logger.error(f"Failed to create calendar event: {str(e)}")
            raise

    async def _arun(
        self,
        start_datetime: str,
        end_datetime: str,
        summary: str,
        location: str = "",
        description: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:

        raise NotImplementedError("Async version of this tool is not implemented.")
