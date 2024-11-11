from typing import List
from zoneinfo import ZoneInfo

from autogen_core.base import AgentId, MessageContext
from autogen_core.components import message_handler, RoutedAgent
from autogen_core.components.model_context import BufferedChatCompletionContext
from autogen_core.components.models import (
    AssistantMessage,
    ChatCompletionClient,
    LLMMessage,
    SystemMessage,
    UserMessage,
)
from autogen_core.components.tool_agent import tool_agent_caller_loop
from autogen_core.components.tools import ToolSchema
from src.message_protocol.messages import Message
from tzlocal import get_localzone


class GoogleAssistant(RoutedAgent):
    def _get_timezone(self) -> ZoneInfo:
        """Get the current system timezone."""
        return ZoneInfo(str(get_localzone()))

    def __init__(
        self,
        model_client: ChatCompletionClient,
        tool_schema: List[ToolSchema],
        tool_agent_type: str,
    ) -> None:
        super().__init__("An agent with tools")
        self._system_messages: List[LLMMessage] = [
            SystemMessage(
                """You are a helpful AI assistant. You are responsible for managing mailing and calendar on behalf of the user on the Google platform.
                   When you retieve email messages or calendar events, always include the identifier of these entities, so these can be reffered to later.
                   The user's current timezone is {}. Make sure to use this timezone when working with dates and times.
                """.format(
                    str(self._get_timezone())
                ),
            ),
        ]
        self._model_client = model_client
        self._tool_schema = tool_schema
        self._tool_agent_id = AgentId(tool_agent_type, self.id.key)
        self._model_context = BufferedChatCompletionContext(buffer_size=5)

    @message_handler
    async def handle_user_message(
        self, message: Message, ctx: MessageContext
    ) -> Message:
        user_message = UserMessage(content=message.content, source="user")

        await self._model_context.add_message(user_message)

        # Create a session of messages.
        session: List[LLMMessage] = (
            self._system_messages + await self._model_context.get_messages()
        )

        # Run the caller loop to handle tool calls.
        messages = await tool_agent_caller_loop(
            self,
            tool_agent_id=self._tool_agent_id,
            model_client=self._model_client,
            input_messages=session,
            tool_schema=self._tool_schema,
            cancellation_token=ctx.cancellation_token,
        )

        assert isinstance(messages[-1].content, str)

        await self._model_context.add_message(
            AssistantMessage(content=messages[-1].content, source=self.metadata["type"])
        )

        # Return the final response.
        return Message(content=messages[-1].content)