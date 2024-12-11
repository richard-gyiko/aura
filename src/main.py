import asyncio

from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from dotenv import load_dotenv

# from .agents.aura import aura
from .agents.data_operator import data_operator
from .utils.console import RichConsole


async def main():
    # agent = aura()
    agent = data_operator()

    while True:
        try:
            user_input = input("> ")

            if user_input == "exit":
                break

            await RichConsole(
                stream=agent.on_messages_stream(
                    [TextMessage(content=user_input, source="user")],
                    cancellation_token=CancellationToken(),
                ),
                show_intermediate=True,
            )
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
