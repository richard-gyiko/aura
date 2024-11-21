import asyncio

from autogen_agentchat.messages import TextMessage
from autogen_core.base import CancellationToken
from rich.console import Console

from .agents.aura import aura
from .utils.console import RichConsole


async def main():
    agent = aura()
    console = Console()

    while True:
        console.print("> ", end="")
        user_input = console.input("")

        if user_input == "exit":
            break

        await RichConsole(
            agent.on_messages_stream(
                [TextMessage(content=user_input, source="user")],
                cancellation_token=CancellationToken(),
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
