from pathlib import Path
from autogen_ext.tools.langchain import LangChainToolAdapter
from autogen_ext_mcp.tools import get_tools_from_mcp_server
from langchain_google_community import GmailToolkit
from langchain_google_community.gmail.utils import (
    build_resource_service as build_gmail_resource_service,
)
from mcp import StdioServerParameters

from .gmail.toolkit import GmailToolkitExt
from .google_calendar.tookit import GoogleCalendarToolkit
from .google_calendar.utils import (
    build_resource_service as build_google_calendar_resource_service,
)
from .utilities.get_current_time import GetCurrentTime


file_system_server = StdioServerParameters(
    command="npx.cmd",
    args=[
        "-y",
        "@modelcontextprotocol/server-filesystem",
        str(Path.home() / "Desktop" / "aura"),
    ],
)


async def get_file_system_tools():
    return await get_tools_from_mcp_server(file_system_server)


def get_gmail_tools(scopes: list[str]):
    api_resource = build_gmail_resource_service(scopes=scopes)

    gmailTookit = GmailToolkit(api_resource=api_resource)
    gmailToolkitExt = GmailToolkitExt(api_resource=api_resource)

    tools = gmailTookit.get_tools() + gmailToolkitExt.get_tools()

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
