from __future__ import annotations

import logging
from typing import List, Optional, Type

from autogen_core.application.logging import TRACE_LOGGER_NAME
from googleapiclient.errors import HttpError
from langchain.callbacks.manager import CallbackManagerForToolRun
from pydantic import BaseModel, Field
from utils.timezone import get_local_timezone

from .base import GoogleCalendarBaseTool
from .utils import parse_and_format_datetime


class EditEventSchema(BaseModel):
    event_id: str = Field(
        description="The unique identifier for the calendar event to edit"
    )
    calendar_id: str = Field(
        default="primary",
        description="The calendar ID. Use 'primary' for the primary calendar.",
    )
    send_updates: Optional[str] = Field(
        default="all",
        description=(
            "Guests who should receive notifications about the event update. "
            "Possible values are: 'all' to notify all guests, 'externalOnly' to notify only "
            "non-Google Calendar guests, or 'none' to send no notifications."
        ),
    )
    supports_attachments: Optional[bool] = Field(
        default=False,
        description="Whether the API client performing operation supports event attachments.",
    )
    conference_data_version: Optional[int] = Field(
        default=0,
        description=(
            "Version number of conference data supported by the API client. "
            "Version 0 assumes no conference data support and ignores conference data in the event's body. "
            "Version 1 enables support for copying of ConferenceData as well as for creating new conferences "
            "using the createRequest field of conferenceData."
        ),
    )
    summary: Optional[str] = Field(
        default=None,
        description="The new title of the event. Leave empty to keep existing title.",
    )
    start_datetime: Optional[str] = Field(
        default=None,
        description=(
            "The new start datetime in format YYYY-MM-DDTHH:MM:SS. "
            "Leave empty to keep existing start time."
        ),
    )
    end_datetime: Optional[str] = Field(
        default=None,
        description=(
            "The new end datetime in format YYYY-MM-DDTHH:MM:SS. "
            "Leave empty to keep existing end time."
        ),
    )
    description: Optional[str] = Field(
        default=None,
        description="The new description of the event. Leave empty to keep existing description.",
    )
    location: Optional[str] = Field(
        default=None,
        description="The new location of the event. Leave empty to keep existing location.",
    )
    add_attendees: Optional[List[str]] = Field(
        default=None, description="List of email addresses to add as attendees."
    )
    remove_attendees: Optional[List[str]] = Field(
        default=None, description="List of email addresses to remove from attendees."
    )
    timezone: Optional[str] = Field(
        default=None,
        description="The timezone in TZ Database Name format. Defaults to user's local timezone.",
    )


class GoogleCalendarEditEvent(GoogleCalendarBaseTool):
    """Tool for editing existing events in Google Calendar.

    This tool allows modification of calendar events including:
    - Changing title (summary)
    - Updating start/end times
    - Modifying description and location
    - Adding/removing attendees
    """

    name: str = "edit_google_calendar_event"
    description: str = (
        "Use this tool to edit an existing calendar event. "
        "You need to provide the event ID and specify which fields to update. "
        "The event ID can be obtained from the list_google_calendar_events tool. "
        "You can update the title, times, description, location, and attendees."
    )
    args_schema: Type[BaseModel] = EditEventSchema

    _logger = logging.getLogger(f"{TRACE_LOGGER_NAME}.{name}")

    def _run(
        self,
        event_id: str,
        calendar_id: str = "primary",
        summary: Optional[str] = None,
        start_datetime: Optional[str] = None,
        end_datetime: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        add_attendees: Optional[List[str]] = None,
        remove_attendees: Optional[List[str]] = None,
        timezone: Optional[str] = None,
        send_updates: str = "all",
        supports_attachments: bool = False,
        conference_data_version: int = 0,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            # Get the existing event
            event = (
                self.api_resource.events()
                .get(calendarId=calendar_id, eventId=event_id)
                .execute()
            )

            # Update fields if provided
            if summary is not None:
                event["summary"] = summary

            if start_datetime is not None and end_datetime is not None:
                if timezone is None:
                    timezone = str(get_local_timezone())

                start_rfc, end_rfc, timezone = parse_and_format_datetime(
                    start_datetime, end_datetime, timezone
                )

                event["start"] = {"dateTime": start_rfc, "timeZone": timezone}
                event["end"] = {"dateTime": end_rfc, "timeZone": timezone}

            if description is not None:
                event["description"] = description

            if location is not None:
                event["location"] = location

            # Handle attendees
            current_attendees = event.get("attendees", [])

            if add_attendees:
                # Add new attendees
                new_attendees = [
                    {"email": email}
                    for email in add_attendees
                    if email not in [a["email"] for a in current_attendees]
                ]
                current_attendees.extend(new_attendees)

            if remove_attendees:
                # Remove specified attendees
                current_attendees = [
                    a for a in current_attendees if a["email"] not in remove_attendees
                ]

            if add_attendees or remove_attendees:
                event["attendees"] = current_attendees

            # Update the event
            updated_event = (
                self.api_resource.events()
                .update(
                    calendarId=calendar_id,
                    eventId=event_id,
                    body=event,
                    sendUpdates=send_updates,
                    supportsAttachments=supports_attachments,
                    conferenceDataVersion=conference_data_version,
                )
                .execute()
            )

            return f"Successfully updated event: {updated_event.get('htmlLink')} (ID: {updated_event.get('id')})"

        except HttpError as error:
            self._logger.error(f"Failed to update calendar event: {error}")
            raise
        except Exception as e:
            self._logger.error(f"Unexpected error updating calendar event: {str(e)}")
            raise

    async def _arun(
        self,
        event_id: str,
        calendar_id: str = "primary",
        summary: Optional[str] = None,
        start_datetime: Optional[str] = None,
        end_datetime: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        add_attendees: Optional[List[str]] = None,
        remove_attendees: Optional[List[str]] = None,
        timezone: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("Async version of this tool is not implemented.")
