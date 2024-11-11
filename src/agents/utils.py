from autogen_core.components.models import (
    AssistantMessage,
    FunctionExecutionResultMessage,
    LLMMessage,
    SystemMessage,
    UserMessage,
)
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Create a single console instance
console = Console()


def print_message(llm_message: LLMMessage):
    """Print an LLM message with appropriate formatting and colors.

    Args:
        llm_message: The message to print
    """
    if isinstance(llm_message, SystemMessage):
        console.print(Panel(llm_message.content, title="System", style="blue"))
    elif isinstance(llm_message, UserMessage):
        content = llm_message.content
        if isinstance(content, list):
            # Handle list of str/Image
            content = "\n".join(str(item) for item in content)

        title = Text(f"User ({llm_message.source})")
        console.print(Panel(content, title=title, style="green"))
    elif isinstance(llm_message, AssistantMessage):
        content = llm_message.content
        if isinstance(content, list):
            # Handle list of FunctionCall
            function_calls = []
            for call in content:
                call_str = f"Function: {call.name}\n"
                call_str += f"ID: {call.id}\n"
                call_str += f"Arguments: {call.arguments}"
                function_calls.append(call_str)
            content = "\n\n".join(function_calls)

        title = Text(f"Assistant ({llm_message.source})")
        console.print(Panel(content, title=title, style="yellow"))
    elif isinstance(llm_message, FunctionExecutionResultMessage):
        results = []
        for result in llm_message.content:
            result_str = f"Call ID: {result.call_id}\n"
            result_str += f"Result: {result.content}"
            results.append(result_str)

        content = "\n\n".join(results)
        console.print(Panel(content, title="Function Results", style="magenta"))
    else:
        console.print(
            Panel(str(llm_message), title="Unknown Message Type", style="white")
        )
