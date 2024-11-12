import asyncio

from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.base import AgentId
from autogen_core.components.tool_agent import ToolAgent
from autogen_ext.models import OpenAIChatCompletionClient
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

from .agents.google_assistant import GoogleAssistant
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

ENABLE_TRACING = False


async def main():
    load_dotenv()

    tools = (
        get_gmail_tools(SCOPES)
        + get_google_calendar_tools(SCOPES)
        + get_utility_tools()
    )

    runtime = SingleThreadedAgentRuntime(
        tracer_provider=configure_otlp_tracing() if ENABLE_TRACING else None
    )

    await ToolAgent.register(
        runtime,
        "gmail_tools_executor_agent",
        lambda: ToolAgent("Gmail Tools Executor Agent", tools),
    )
    await GoogleAssistant.register(
        runtime,
        "tool_use_agent",
        lambda: GoogleAssistant(
            OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.01),
            [tool.schema for tool in tools],
            "gmail_tools_executor_agent",
            print_internal_dialogues=True,
        ),
    )

    runtime.start()

    # Send a direct message to the tool agent.
    tool_use_agent = AgentId("tool_use_agent", "default")

    while True:
        user_input = input("User: ")

        if user_input == "exit":
            break

        response = await runtime.send_message(Message(user_input), tool_use_agent)

        Console().print(Markdown(response.content))

    # Stop processing messages.
    await runtime.stop()


if __name__ == "__main__":
    asyncio.run(main())
