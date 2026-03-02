"""Base agent classes: BaseAgent (no tools) and BaseToolCallingAgent (with tools)."""

from collections.abc import Awaitable, Callable

from langchain.agents import create_agent
from langchain_aws import ChatBedrockConverse
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate

from app.config import settings
from app.consts.models import ModelConsts


class BaseAgent:
    """Base class for agents without tool calling. Use for simple prompt to response agents."""

    def __init__(
        self,
        agent_name: str,
        model_name: str = ModelConsts.CLAUDE_SONNET_4_5,
        status_callback: Callable[[str], Awaitable[None]] | None = None,
    ):
        self.agent_name = agent_name
        self.model_name = model_name
        self.model = ChatBedrockConverse(
            model=model_name,
            region_name=settings.AWS_REGION,
            credentials_profile_name=None,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            max_tokens=8192,
        )
        self.status_callback = status_callback

    async def emit_status(self, message: str) -> None:
        """Emit a status update via the callback."""
        if self.status_callback:
            await self.status_callback(message)

    async def send_prompt(
        self,
        prompt_template: ChatPromptTemplate,
        chat_history: list[HumanMessage | AIMessage] | None = None,
        **kwargs,
    ) -> str:
        """Send a prompt to the model and return the response content."""
        messages = prompt_template.format_messages(
            chat_history=chat_history or [],
            **kwargs,
        )
        response = await self.model.ainvoke(messages)
        content = response.content
        if isinstance(content, str):
            return content
        return str(content)


class BaseToolCallingAgent(BaseAgent):
    """Base class for agents with tool calling. Uses LangChain create_agent (tool-calling graph)."""

    def __init__(
        self,
        agent_name: str,
        tools: list,
        system_prompt: str,
        model_name: str = ModelConsts.CLAUDE_SONNET_4_5,
        status_callback: Callable[[str], Awaitable[None]] | None = None,
        max_iterations: int = 10,
    ):
        super().__init__(agent_name, model_name=model_name, status_callback=status_callback)
        self.tools = tools
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations
        self.graph = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=self.system_prompt,
        )

    async def run(
        self,
        input_text: str,
        chat_history: list[HumanMessage | AIMessage] | None = None,
    ) -> str:
        """Run the agent with the given input and chat history. Returns final AI response text."""
        messages = list(chat_history or []) + [HumanMessage(content=input_text)]
        config = {"recursion_limit": self.max_iterations * 3}
        result = await self.graph.ainvoke({"messages": messages}, config=config)
        out_messages = result.get("messages", [])
        for msg in reversed(out_messages):
            if isinstance(msg, AIMessage) and msg.content:
                content = msg.content
                if isinstance(content, str):
                    return content
                return str(content)
        return ""
