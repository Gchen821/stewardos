"""Provider gateway implementations and mapping to runtime LLM client."""

from app.core.agent.message import AgentMessage
from app.core.llm.client import HelloAgentsLLM
from app.core.llm.gateway import LLMResponse, ModelGateway


class OpenAICompatibleGateway(ModelGateway):
    """OpenAI-compatible gateway backed by `HelloAgentsLLM`."""

    def __init__(self, llm_client: HelloAgentsLLM | None = None) -> None:
        self.llm_client = llm_client

    def generate(
        self,
        messages: list[AgentMessage],
        model_hint: str | None = None,
        tools: list[str] | None = None,
        stream: bool = False,
    ) -> LLMResponse:
        _ = (tools, stream)
        if self.llm_client is not None:
            payload = [{"role": m.role.value, "content": m.content} for m in messages]
            raw = self.llm_client.invoke(payload)
            return LLMResponse(
                text=raw.content,
                model=raw.model or (model_hint or "system-default"),
                usage=raw.usage,
            )
        return LLMResponse(
            text="Provider gateway placeholder.",
            model=model_hint or "system-default",
        )
