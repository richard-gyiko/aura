from autogen_ext.tools import LangChainToolAdapter
from langchain_google_community import GmailToolkit
from langchain_google_community.gmail.utils import (
    build_resource_service as build_gmail_resource_service,
)

from .google_calendar.tookit import GoogleCalendarToolkit
from .google_calendar.utils import (
    build_resource_service as build_google_calendar_resource_service,
)
from .utilities.get_current_time import GetCurrentTime


def get_gmail_tools(scopes: list[str]):
    gmailTookit = GmailToolkit(api_resource=build_gmail_resource_service(scopes=scopes))
    tools = gmailTookit.get_tools()

    autogen_tools = [LangChainToolAdapter(tool) for tool in tools]

    return autogen_tools


def get_google_calendar_tools(scopes: list[str]):
    google_calendar_toolkit = GoogleCalendarToolkit(
        api_resource=build_google_calendar_resource_service(scopes=scopes)
    )
    tools = google_calendar_toolkit.get_tools()

    autogen_tools = [LangChainToolAdapter(tool) for tool in tools]

    return autogen_tools


def get_utility_tools():
    tools = [
        GetCurrentTime(),
    ]

    autogen_tools = [LangChainToolAdapter(tool) for tool in tools]

    return autogen_tools
