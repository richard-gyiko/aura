import asyncio

from .agents.tool_use_agent import ToolUseAgent

from .tools.tool_factory import get_tools
from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.components.tool_agent import ToolAgent
from autogen_ext.models import OpenAIChatCompletionClient
from autogen_core.base import AgentId
from .contracts.message import Message

from dotenv import load_dotenv


async def main():
    load_dotenv()

    tools = get_tools()

    runtime = SingleThreadedAgentRuntime()

    await ToolAgent.register(
        runtime, "tool_executor_agent", lambda: ToolAgent("tool executor agent", tools)
    )
    await ToolUseAgent.register(
        runtime,
        "tool_use_agent",
        lambda: ToolUseAgent(
            OpenAIChatCompletionClient(model="gpt-4o-mini"),
            [tool.schema for tool in tools],
            "tool_executor_agent",
        ),
    )

    runtime.start()

    # Send a direct message to the tool agent.
    tool_use_agent = AgentId("tool_use_agent", "default")
    response = await runtime.send_message(
        Message("What's my latest email about?"), tool_use_agent
    )
    print(response.content)
    # Stop processing messages.
    await runtime.stop()


if __name__ == "__main__":
    asyncio.run(main())
