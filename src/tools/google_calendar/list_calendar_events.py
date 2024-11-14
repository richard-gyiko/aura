from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Type

from autogen_core.application.logging import TRACE_LOGGER_NAME
from dateutil import parser, tz
from googleapiclient.errors import HttpError
from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
from pydantic import BaseModel, Field
from src.utils.timezone import get_local_timezone

from .base import GoogleCalendarBaseTool
from .utils import parse_and_format_datetime


class GetEventsSchema(BaseModel):
    # https://developers.google.com/calendar/api/v3/reference/events/list
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
    max_results: int = Field(
        default=10,
        description="The maximum number of results to return.",
    )
    timezone: Optional[str] = Field(
        default=None,
        description="The timezone in TZ Database Name format, e.g. 'America/New_York'. Defaults to the user's local timezone.",
    )


class GoogleCalendarListEvents(GoogleCalendarBaseTool):
    """Tool for listing events from Google Calendar.

    This tool searches for calendar events across all of the user's selected calendars
    within a specified time range. Results include event details like title, time,
    location and attendees. All times are handled in the user's local timezone by default.
    """

    name: str = "list_google_calendar_events"
    description: str = (
        " Use this tool to search for the user's calendar events."
        " The input must be the start and end datetimes for the search query."
        " Start time is default to the current time. You can also specify the"
        " maximum number of results to return. The output is a JSON list of "
        " all the events in the user's calendar between the start and end times."
    )
    args_schema: Type[BaseModel] = GetEventsSchema

    _logger = logging.getLogger(f"{TRACE_LOGGER_NAME}.{name}")

    def _parse_event(self, event, timezone):
        # convert to local timezone
        start = event["start"].get("dateTime", event["start"].get("date"))
        start = (
            parser.parse(start)
            .astimezone(tz.gettz(timezone))
            .strftime("%Y/%m/%d %H:%M:%S")
        )
        end = event["end"].get("dateTime", event["end"].get("date"))
        end = (
            parser.parse(end)
            .astimezone(tz.gettz(timezone))
            .strftime("%Y/%m/%d %H:%M:%S")
        )
        event_parsed = dict(start=start, end=end)
        for field in ["summary", "description", "location", "hangoutLink", "attendees"]:
            event_parsed[field] = event.get(field, None)
        return event_parsed

    def _get_calendars(self):
        calendars = []
        try:
            calendar_list = self.api_resource.calendarList().list().execute()
            for cal in calendar_list.get("items", []):
                if cal.get("selected", None):
                    calendars.append(cal["id"])
            return calendars
        except HttpError as error:
            self._logger.error(f"Failed to retrieve calendar list: {error}")
            raise

    def _run(
        self,
        start_datetime: str,
        end_datetime: str,
        max_results: int = 10,
        timezone: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> List[Dict[str, Any]]:
        try:
            calendars = self._get_calendars()

            if timezone is None:
                zone_info = get_local_timezone()
                timezone = str(zone_info)

            events = []

            start_rfc, end_rfc, timezone = parse_and_format_datetime(
                start_datetime, end_datetime, timezone
            )

            for cal in calendars:
                events_result = (
                    self.api_resource.events()
                    .list(
                        calendarId=cal,
                        timeMin=start_rfc,
                        timeMax=end_rfc,
                        maxResults=max_results,
                        singleEvents=True,
                        orderBy="startTime",
                        timeZone=timezone,
                    )
                    .execute()
                )
                cal_events = events_result.get("items", [])
                events.extend(cal_events)

            events = sorted(
                events, key=lambda x: x["start"].get("dateTime", x["start"].get("date"))
            )

            return [self._parse_event(e, timezone) for e in events]

        except HttpError as error:
            self._logger.error(f"Failed to retrieve calendar events: {error}")
            raise
        except Exception as e:
            self._logger.error(f"Unexpected error occurred: {str(e)}")
            raise

    async def _arun(
        self,
        start_datetime: str,
        end_datetime: str,
        max_results: int = 10,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> List(Dict[str, Any]):  # type: ignore

        raise NotImplementedError("Async version of this tool is not implemented.")
