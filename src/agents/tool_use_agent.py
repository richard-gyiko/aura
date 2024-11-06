from typing import List

from autogen_core.base import AgentId, MessageContext
from autogen_core.components import RoutedAgent, message_handler
from autogen_core.components.models import (
    ChatCompletionClient,
    LLMMessage,
    SystemMessage,
    UserMessage,
)
from autogen_core.components.tool_agent import tool_agent_caller_loop
from autogen_core.components.tools import ToolSchema

from src.message_protocol.messages import Message


class ToolUseAgent(RoutedAgent):
    def __init__(
        self,
        model_client: ChatCompletionClient,
        tool_schema: List[ToolSchema],
        tool_agent_type: str,
    ) -> None:
        super().__init__("An agent with tools")
        self._system_messages: List[LLMMessage] = [
            SystemMessage("You are a helpful AI assistant.")
        ]
        self._model_client = model_client
        self._tool_schema = tool_schema
        self._tool_agent_id = AgentId(tool_agent_type, self.id.key)

    @message_handler
    async def handle_user_message(
        self, message: Message, ctx: MessageContext
    ) -> Message:
        # Create a session of messages.
        session: List[LLMMessage] = [
            UserMessage(content=message.content, source="user")
        ]
        # Run the caller loop to handle tool calls.
        messages = await tool_agent_caller_loop(
            self,
            tool_agent_id=self._tool_agent_id,
            model_client=self._model_client,
            input_messages=session,
            tool_schema=self._tool_schema,
            cancellation_token=ctx.cancellation_token,
        )
        # Return the final response.
        assert isinstance(messages[-1].content, str)
        return Message(content=messages[-1].content)
