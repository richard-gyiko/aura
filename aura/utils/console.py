import time
from typing import AsyncGenerator

from autogen_agentchat.base import Response
from autogen_agentchat.messages import AgentMessage
from autogen_core.components.models import RequestUsage
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text


async def RichConsole(
    stream: AsyncGenerator[AgentMessage | Response, None],
    show_intermediate: bool = True,
) -> None:
    """Consume the stream from  :meth:`~autogen_agentchat.teams.Team.run_stream`
    and print the messages to the console.

    Args:
        stream: The message stream to consume
        show_intermediate: Whether to show intermediate messages (default: True)
    """
    console = Console()
    start_time = time.time()
    total_usage = RequestUsage(prompt_tokens=0, completion_tokens=0)

    async for message in stream:
        if isinstance(message, Response):
            duration = time.time() - start_time
            stats = Text()
            stats.append(
                f"Messages: {len(message.inner_messages)} • ", style="dim cyan"
            )
            stats.append(
                f"Tokens: {total_usage.prompt_tokens}/{total_usage.completion_tokens} • ",
                style="dim cyan",
            )
            stats.append(f"Duration: {duration:.2f}s", style="dim cyan")
            console.print(Markdown(message.chat_message.content), style="turquoise4")
            console.print(stats)
        else:
            # Always update token usage even if not showing intermediate messages
            if message.models_usage:
                total_usage.completion_tokens += message.models_usage.completion_tokens
                total_usage.prompt_tokens += message.models_usage.prompt_tokens

            if show_intermediate:
                content = Text()

                # Add the message source as a header
                content.append(f"{message.source}\n", style="dim")

                # Add the message content
                content.append(f"{message.content}\n", style="dim")

                # Add usage statistics if present
                if message.models_usage:
                    content.append(
                        f"[Tokens: {message.models_usage.prompt_tokens} prompt, {message.models_usage.completion_tokens} completion]",
                        style="dim cyan",
                    )

                console.print(content)
                console.print()  # Add a blank line between messages
