import asyncio

from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.base import AgentId
from autogen_core.components.tool_agent import ToolAgent
from autogen_ext.models import OpenAIChatCompletionClient
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

from .agents.gmail_manager_agent import GmailManagerAgent
from .message_protocol.messages import Message
from .tools.tool_factory import get_gmail_tools


async def main():
    load_dotenv()

    tools = get_gmail_tools()

    runtime = SingleThreadedAgentRuntime()

    await ToolAgent.register(
        runtime,
        "gmail_tools_executor_agent",
        lambda: ToolAgent("Gmail Tools Executor Agent", tools),
    )
    await GmailManagerAgent.register(
        runtime,
        "tool_use_agent",
        lambda: GmailManagerAgent(
            OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.01),
            [tool.schema for tool in tools],
            "gmail_tools_executor_agent",
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
