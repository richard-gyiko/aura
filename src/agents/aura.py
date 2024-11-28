from zoneinfo import ZoneInfo

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models import OpenAIChatCompletionClient
from src.tools.tool_factory import (
    get_gmail_tools,
    get_google_calendar_tools,
    get_utility_tools,
)
from tzlocal import get_localzone

SCOPES = [
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]


SYSTEM_PROMPT_TEMPLATE = """
You are a versatile and efficient AI assistant specialized in managing the user's email and calendar.
Your primary responsibilities include:
- **Email Management**: Retrieve, organize, and manage email messages. Always include a unique identifier for each message to ensure easy reference.
- **Calendar Management**: Schedule, update, and retrieve calendar events while resolving conflicts or overlaps.
Guidelines:
- Adhere to the specified timezone for all date and time-related tasks: {timezone}.
- Provide clear, concise, and user-friendly responses, prioritizing accuracy and convenience.
- Proactively notify the user of important updates, conflicts, or pending actions in their email or calendar.
- User your tools available to be aware of the current time and date.
"""


def _get_timezone() -> ZoneInfo:
    """Get the current system timezone."""
    return ZoneInfo(str(get_localzone()))


def aura() -> AssistantAgent:
    tools = (
        get_gmail_tools(SCOPES)
        + get_google_calendar_tools(SCOPES)
        + get_utility_tools()
    )

    assistant = AssistantAgent(
        name="aura",
        model_client=OpenAIChatCompletionClient(
            model="gpt-4o-mini",
            temperature=0.01,
        ),
        tools=tools,
        system_message=SYSTEM_PROMPT_TEMPLATE.format(timezone=str(_get_timezone())),
    )

    return assistant
