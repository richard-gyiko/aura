import asyncio
import logging

from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.application.logging import TRACE_LOGGER_NAME
from autogen_core.base import AgentId
from autogen_core.components.tool_agent import ToolAgent
from autogen_ext.models import OpenAIChatCompletionClient
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

from .agents.aura import Aura
from .message_protocol.messages import Message
from .tools.tool_factory import (
    get_gmail_tools,
    get_google_calendar_tools,
    get_utility_tools,
)
from .tracing import configure_otlp_tracing

# We are giving the combined scopes because one of the tools will first navigate to the user constent page so we can ask for the scopes in a single go.
SCOPES = [
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]

ENABLE_OTEL_TRACING = False
ENABLE_TRACE_LOGGING = True

if ENABLE_TRACE_LOGGING:
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(TRACE_LOGGER_NAME)
    logger.setLevel(logging.DEBUG)


async def main():
    load_dotenv()

    tools = (
        get_gmail_tools(SCOPES)
        + get_google_calendar_tools(SCOPES)
        + get_utility_tools()
    )

    runtime = SingleThreadedAgentRuntime(
        tracer_provider=configure_otlp_tracing() if ENABLE_OTEL_TRACING else None
    )

    await ToolAgent.register(
        runtime,
        "tool_executor_agent",
        lambda: ToolAgent("Tools Executor Agent", tools),
    )
    await Aura.register(
        runtime,
        "tool_use_agent",
        lambda: Aura(
            OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.01),
            [tool.schema for tool in tools],
            "tool_executor_agent",
            print_internal_dialogues=False,
        ),
    )

    runtime.start()

    # Send a direct message to the tool agent.
    tool_use_agent = AgentId("tool_use_agent", "default")

    console = Console()

    while True:
        # User input with emoji indicator
        console.print("> ", end="")
        user_input = console.input("")

        if user_input == "exit":
            break

        response = await runtime.send_message(Message(user_input), tool_use_agent)

        # AI response with emoji and styling
        console.print(Markdown(response.content), style="light_sea_green")
        console.print()  # Extra line after response for better readability

    # Stop processing messages.
    await runtime.stop()


if __name__ == "__main__":
    asyncio.run(main())
