from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import TypedDict
from uuid import UUID

from app.config import get_settings, reload_settings
from app.runtime.llm_loader import LLMLoader
from app.schemas.runtime import LLMProviderRecord, LLMSettingsRead, LLMSettingsUpdate


class ProviderEnvConfig(TypedDict):
    model: str
    fallback_model: str
    base_url: str
    api_key: str
    timeout_seconds: str


PROVIDER_ENV_CONFIGS: dict[str, ProviderEnvConfig] = {
    "auto": {
        "model": "AUTO_LLM_MODEL",
        "fallback_model": "AUTO_LLM_FALLBACK_MODEL",
        "base_url": "AUTO_LLM_BASE_URL",
        "api_key": "AUTO_LLM_API_KEY",
        "timeout_seconds": "AUTO_LLM_TIMEOUT_SECONDS",
    },
    "openai": {
        "model": "OPENAI_LLM_MODEL",
        "fallback_model": "OPENAI_LLM_FALLBACK_MODEL",
        "base_url": "OPENAI_LLM_BASE_URL",
        "api_key": "OPENAI_API_KEY",
        "timeout_seconds": "OPENAI_LLM_TIMEOUT_SECONDS",
    },
    "modelscope": {
        "model": "MODELSCOPE_LLM_MODEL",
        "fallback_model": "MODELSCOPE_LLM_FALLBACK_MODEL",
        "base_url": "MODELSCOPE_LLM_BASE_URL",
        "api_key": "MODELSCOPE_API_KEY",
        "timeout_seconds": "MODELSCOPE_LLM_TIMEOUT_SECONDS",
    },
    "zhipu": {
        "model": "ZHIPU_LLM_MODEL",
        "fallback_model": "ZHIPU_LLM_FALLBACK_MODEL",
        "base_url": "ZHIPU_LLM_BASE_URL",
        "api_key": "ZHIPU_API_KEY",
        "timeout_seconds": "ZHIPU_LLM_TIMEOUT_SECONDS",
    },
    "anthropic": {
        "model": "ANTHROPIC_LLM_MODEL",
        "fallback_model": "ANTHROPIC_LLM_FALLBACK_MODEL",
        "base_url": "ANTHROPIC_LLM_BASE_URL",
        "api_key": "ANTHROPIC_API_KEY",
        "timeout_seconds": "ANTHROPIC_LLM_TIMEOUT_SECONDS",
    },
    "qwen": {
        "model": "QWEN_LLM_MODEL",
        "fallback_model": "QWEN_LLM_FALLBACK_MODEL",
        "base_url": "QWEN_LLM_BASE_URL",
        "api_key": "DASHSCOPE_API_KEY",
        "timeout_seconds": "QWEN_LLM_TIMEOUT_SECONDS",
    },
    "ollama": {
        "model": "OLLAMA_LLM_MODEL",
        "fallback_model": "OLLAMA_LLM_FALLBACK_MODEL",
        "base_url": "OLLAMA_LLM_BASE_URL",
        "api_key": "OLLAMA_LLM_API_KEY",
        "timeout_seconds": "OLLAMA_LLM_TIMEOUT_SECONDS",
    },
    "vllm": {
        "model": "VLLM_LLM_MODEL",
        "fallback_model": "VLLM_LLM_FALLBACK_MODEL",
        "base_url": "VLLM_LLM_BASE_URL",
        "api_key": "VLLM_LLM_API_KEY",
        "timeout_seconds": "VLLM_LLM_TIMEOUT_SECONDS",
    },
    "local": {
        "model": "LOCAL_LLM_MODEL",
        "fallback_model": "LOCAL_LLM_FALLBACK_MODEL",
        "base_url": "LOCAL_LLM_BASE_URL",
        "api_key": "LOCAL_LLM_API_KEY",
        "timeout_seconds": "LOCAL_LLM_TIMEOUT_SECONDS",
    },
}


class LLMSettingsService:
    def __init__(self, user_id: UUID) -> None:
        self.settings = get_settings()
        self.env_path = Path.cwd() / ".env"
        self.user_id = user_id

    def _read_env_map(self) -> dict[str, str]:
        if not self.env_path.exists():
            return {}

        values: dict[str, str] = {}
        for raw_line in self.env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in raw_line:
                continue
            key, _, value = raw_line.partition("=")
            values[key.strip()] = value
        return values

    def _provider_env(self, provider: str) -> ProviderEnvConfig:
        return PROVIDER_ENV_CONFIGS[provider]

    def _get_provider_record(self, provider: str, env_map: dict[str, str]) -> LLMProviderRecord | None:
        provider_env = self._provider_env(provider)
        model = env_map.get(provider_env["model"], "").strip()
        fallback_model = env_map.get(provider_env["fallback_model"], "").strip() or None
        base_url = env_map.get(provider_env["base_url"], "").strip() or None
        api_key = env_map.get(provider_env["api_key"], "").strip() or None
        timeout_raw = env_map.get(provider_env["timeout_seconds"], "").strip()
        timeout_seconds = int(timeout_raw) if timeout_raw.isdigit() else 60

        if not any([model, fallback_model, base_url, api_key, timeout_raw]):
            return None

        return LLMProviderRecord(
            provider=provider,
            model=model,
            fallback_model=fallback_model,
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            api_key=api_key,
            updated_at=datetime.now(UTC).isoformat(),
        )

    def _list_records(self, env_map: dict[str, str]) -> dict[str, LLMProviderRecord]:
        records: dict[str, LLMProviderRecord] = {}
        for provider in PROVIDER_ENV_CONFIGS:
            record = self._get_provider_record(provider, env_map)
            if record is not None:
                records[provider] = record
        return records

    def get_settings_payload(self) -> LLMSettingsRead:
        runtime = LLMLoader().load()
        runtime.api_key = None
        env_map = self._read_env_map()
        current_provider = self.settings.llm_provider
        current_env = self._provider_env(current_provider)
        current_api_key = env_map.get(current_env["api_key"], "").strip() or self.settings.llm_api_key
        records = self._list_records(env_map)

        return LLMSettingsRead(
            provider=current_provider,
            model=self.settings.llm_model,
            fallback_model=self.settings.llm_fallback_model,
            base_url=self.settings.llm_base_url,
            api_key=current_api_key,
            timeout_seconds=self.settings.llm_timeout_seconds,
            api_key_env_name=current_env["api_key"],
            api_key_configured=bool(current_api_key),
            records=records,
            runtime=runtime,
        )

    def update_settings(self, payload: LLMSettingsUpdate) -> LLMSettingsRead:
        env_map = self._read_env_map()
        provider_env = self._provider_env(payload.provider)
        existing_api_key = env_map.get(provider_env["api_key"], "").strip()
        api_key = (payload.api_key or "").strip() or existing_api_key

        updates = {
            "LLM_PROVIDER": payload.provider,
            "LLM_MODEL": payload.model,
            "LLM_MODEL_ID": payload.model,
            "LLM_FALLBACK_MODEL": payload.fallback_model or "",
            "LLM_FALLBACK_MODEL_ID": payload.fallback_model or "",
            "LLM_BASE_URL": payload.base_url or "",
            "LLM_TIMEOUT_SECONDS": str(payload.timeout_seconds),
            "LLM_TIMEOUT": str(payload.timeout_seconds),
            "LLM_API_KEY": api_key,
            provider_env["model"]: payload.model,
            provider_env["fallback_model"]: payload.fallback_model or "",
            provider_env["base_url"]: payload.base_url or "",
            provider_env["timeout_seconds"]: str(payload.timeout_seconds),
            provider_env["api_key"]: api_key,
        }

        self._write_env(updates)
        for key, value in updates.items():
            os.environ[key] = value

        self.settings = reload_settings()
        return self.get_settings_payload()

    def _write_env(self, updates: dict[str, str]) -> None:
        existing_lines = self.env_path.read_text(encoding="utf-8").splitlines() if self.env_path.exists() else []
        seen: set[str] = set()
        next_lines: list[str] = []

        for line in existing_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in line:
                next_lines.append(line)
                continue

            key, _, _ = line.partition("=")
            env_key = key.strip()
            if env_key in updates:
                next_lines.append(f"{env_key}={updates[env_key]}")
                seen.add(env_key)
            else:
                next_lines.append(line)

        if next_lines and next_lines[-1] != "":
            next_lines.append("")

        for key, value in updates.items():
            if key in seen:
                continue
            next_lines.append(f"{key}={value}")

        self.env_path.write_text("\n".join(next_lines).rstrip() + "\n", encoding="utf-8")
