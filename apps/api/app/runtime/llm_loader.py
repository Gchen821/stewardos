import os

from app.config import get_settings
from app.schemas.runtime import LLMRuntimeConfig


class LLMLoader:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _provider_api_key(self, provider: str | None) -> str | None:
        mapping = {
            "modelscope": self.settings.modelscope_api_key,
            "openai": self.settings.openai_api_key,
            "zhipu": self.settings.zhipu_api_key,
            "anthropic": self.settings.anthropic_api_key,
            "qwen": self.settings.dashscope_api_key,
        }
        return mapping.get(provider or "")

    def _auto_detect_provider(self, api_key: str | None, base_url: str | None) -> str:
        if self.settings.modelscope_api_key:
            return "modelscope"
        if self.settings.openai_api_key:
            return "openai"
        if self.settings.zhipu_api_key:
            return "zhipu"
        if self.settings.anthropic_api_key:
            return "anthropic"
        if self.settings.dashscope_api_key:
            return "qwen"

        actual_api_key = api_key or self.settings.llm_api_key
        actual_base_url = base_url or self.settings.llm_base_url

        if actual_base_url:
            base_url_lower = actual_base_url.lower()
            if "api-inference.modelscope.cn" in base_url_lower:
                return "modelscope"
            if "open.bigmodel.cn" in base_url_lower:
                return "zhipu"
            if "api.anthropic.com" in base_url_lower:
                return "anthropic"
            if "dashscope" in base_url_lower or "aliyuncs.com" in base_url_lower:
                return "qwen"
            if "api.openai.com" in base_url_lower or "/v1" in base_url_lower:
                return "openai"
            if "localhost" in base_url_lower or "127.0.0.1" in base_url_lower:
                if ":11434" in base_url_lower:
                    return "ollama"
                if ":8000" in base_url_lower:
                    return "vllm"
                return "local"

        if actual_api_key:
            if actual_api_key.startswith("ms-"):
                return "modelscope"
            if actual_api_key.startswith("sk-ant-"):
                return "anthropic"
            if actual_api_key.startswith("sk-"):
                return "openai"

        return "auto"

    def load(self) -> LLMRuntimeConfig:
        provider = self.settings.llm_provider
        if provider == "auto":
            provider = self._auto_detect_provider(self.settings.llm_api_key, self.settings.llm_base_url)
        api_key = self.settings.llm_api_key or self._provider_api_key(provider) or os.getenv("OPENAI_API_KEY")
        return LLMRuntimeConfig(
            provider=provider,
            model=self.settings.llm_model,
            fallback_model=self.settings.llm_fallback_model,
            api_key=api_key,
            base_url=self.settings.llm_base_url,
            timeout_seconds=self.settings.llm_timeout_seconds,
        )
