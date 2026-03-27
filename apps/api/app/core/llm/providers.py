from app.core.agent.message import AgentMessage
from app.core.llm.gateway import LLMResponse, ModelGateway


class OpenAICompatibleGateway(ModelGateway):
    """Normalized provider entry point for OpenAI-compatible chat APIs."""

    def generate(
        self,
        messages: list[AgentMessage],
        model_hint: str | None = None,
        tools: list[str] | None = None,
        stream: bool = False,
    ) -> LLMResponse:
        _ = (messages, tools, stream)
        return LLMResponse(
            text="Provider gateway placeholder.",
            model=model_hint or "system-default",
        )
