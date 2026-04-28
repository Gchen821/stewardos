"use client";

import { type FormEvent, useEffect, useState } from "react";

import { fetchLLMSettings, updateLLMSettings, type LLMSettings } from "@/lib/api";

const PROVIDER_PRESETS = {
  auto: { label: "自动检测", baseUrl: "", model: "gpt-4o-mini" },
  openai: { label: "OpenAI", baseUrl: "https://api.openai.com/v1", model: "gpt-4o-mini" },
  modelscope: { label: "ModelScope", baseUrl: "https://api-inference.modelscope.cn/v1/", model: "Qwen/Qwen2.5-72B-Instruct" },
  zhipu: { label: "智谱 AI", baseUrl: "https://open.bigmodel.cn/api/paas/v4/", model: "glm-4.5" },
  anthropic: { label: "Anthropic", baseUrl: "https://api.anthropic.com", model: "claude-3-5-sonnet-latest" },
  qwen: { label: "通义千问", baseUrl: "https://dashscope.aliyuncs.com/compatible-mode/v1", model: "qwen-plus" },
  ollama: { label: "Ollama", baseUrl: "http://127.0.0.1:11434/v1", model: "qwen2.5:7b" },
  vllm: { label: "vLLM", baseUrl: "http://127.0.0.1:8000/v1", model: "Qwen/Qwen2.5-7B-Instruct" },
  local: { label: "本地 OpenAI 兼容接口", baseUrl: "http://127.0.0.1:8000/v1", model: "local-model" },
} as const;

const PROVIDER_ENV_KEYS: Record<keyof typeof PROVIDER_PRESETS, string> = {
  auto: "AUTO_LLM_API_KEY",
  openai: "OPENAI_API_KEY",
  modelscope: "MODELSCOPE_API_KEY",
  zhipu: "ZHIPU_API_KEY",
  anthropic: "ANTHROPIC_API_KEY",
  qwen: "DASHSCOPE_API_KEY",
  ollama: "OLLAMA_LLM_API_KEY",
  vllm: "VLLM_LLM_API_KEY",
  local: "LOCAL_LLM_API_KEY",
};

export default function ModelSettingsPage() {
  const [settings, setSettings] = useState<LLMSettings | null>(null);
  const [provider, setProvider] = useState<keyof typeof PROVIDER_PRESETS>("auto");
  const [providerMenuOpen, setProviderMenuOpen] = useState(false);
  const [model, setModel] = useState("");
  const [fallbackModel, setFallbackModel] = useState("");
  const [baseUrl, setBaseUrl] = useState("");
  const [timeoutSeconds, setTimeoutSeconds] = useState("60");
  const [apiKey, setApiKey] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchLLMSettings()
      .then((result) => {
        setSettings(result);
        setProvider((result.provider in PROVIDER_PRESETS ? result.provider : "auto") as keyof typeof PROVIDER_PRESETS);
        setModel(result.model);
        setFallbackModel(result.fallback_model ?? "");
        setBaseUrl(result.base_url ?? "");
        setApiKey(result.api_key ?? "");
        setTimeoutSeconds(String(result.timeout_seconds));
      })
      .catch(() => setSettings(null));
  }, []);

  function applyProviderRecord(nextProvider: keyof typeof PROVIDER_PRESETS) {
    const record = settings?.records[nextProvider];
    const preset = PROVIDER_PRESETS[nextProvider];
    setProvider(nextProvider);
    setProviderMenuOpen(false);
    setModel(record?.model ?? preset.model);
    setFallbackModel(record?.fallback_model ?? "");
    setBaseUrl(record?.base_url ?? preset.baseUrl);
    setApiKey(record?.api_key ?? "");
    setTimeoutSeconds(String(record?.timeout_seconds ?? 60));
    setMessage(null);
    setError(null);
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setMessage(null);
    setError(null);

    try {
      const result = await updateLLMSettings({
        provider,
        model,
        fallback_model: fallbackModel || null,
        base_url: baseUrl || null,
        timeout_seconds: Number(timeoutSeconds) || 60,
        api_key: apiKey,
      });
      setSettings(result);
      setFallbackModel(result.fallback_model ?? "");
      setApiKey(result.api_key ?? "");
      setMessage(".env 已更新，运行时配置已热加载");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "保存失败");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h2 className="text-3xl font-semibold tracking-tight text-slate-950">模型设置</h2>
        <p className="text-sm text-slate-600">先选择模型格式，再填写模型名、API Key、Base URL 等参数。保存后会热加载到 `.env`。</p>
      </header>
      <form onSubmit={onSubmit} className="space-y-5 rounded-3xl border border-slate-200 bg-white p-6">
        <div className="grid gap-4 lg:grid-cols-2">
          <label className="space-y-2 lg:col-span-2">
            <span className="text-sm font-medium text-slate-700">模型格式</span>
            <div className="relative">
              <button
                type="button"
                onClick={() => setProviderMenuOpen((open) => !open)}
                className="flex w-full items-center justify-between rounded-2xl border border-slate-200 bg-[linear-gradient(135deg,_#f8fafc_0%,_#ecfeff_100%)] px-4 py-3 text-left text-sm font-medium text-slate-900 outline-none"
              >
                <span className="flex items-center gap-3">
                  <span className="inline-flex h-8 min-w-8 items-center justify-center rounded-full bg-white px-2 text-xs font-semibold text-teal-700 shadow-sm">
                    {PROVIDER_PRESETS[provider].label.slice(0, 2).toUpperCase()}
                  </span>
                  <span>{PROVIDER_PRESETS[provider].label}</span>
                </span>
                <span className={`text-slate-400 transition ${providerMenuOpen ? "rotate-180" : ""}`}>⌄</span>
              </button>
              {providerMenuOpen ? (
                <div className="absolute z-20 mt-2 w-full overflow-hidden rounded-2xl border border-slate-200 bg-white p-2 shadow-[0_18px_50px_rgba(15,23,42,0.14)]">
                  <div className="max-h-72 space-y-1 overflow-y-auto">
                    {Object.entries(PROVIDER_PRESETS).map(([key, item]) => {
                      const active = key === provider;
                      return (
                        <button
                          key={key}
                          type="button"
                          onClick={() => applyProviderRecord(key as keyof typeof PROVIDER_PRESETS)}
                          className={`flex w-full items-start gap-3 rounded-xl px-3 py-3 text-left transition ${
                            active
                              ? "bg-teal-50 text-teal-900"
                              : "text-slate-700 hover:bg-slate-50"
                          }`}
                        >
                          <span
                            className={`inline-flex h-9 min-w-9 items-center justify-center rounded-full text-xs font-semibold ${
                              active ? "bg-teal-700 text-white" : "bg-slate-100 text-slate-600"
                            }`}
                          >
                            {item.label.slice(0, 2).toUpperCase()}
                          </span>
                          <span className="min-w-0">
                            <span className="block text-sm font-medium">{item.label}</span>
                            <span className="mt-0.5 block truncate text-xs text-slate-500">
                              {item.baseUrl || "自动识别当前环境中的模型服务"}
                            </span>
                          </span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              ) : null}
            </div>
            <p className="text-xs text-slate-500">切换后会自动回填该类型最近一次保存的配置。</p>
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">模型名称</span>
            <input
              value={model}
              onChange={(event) => setModel(event.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none"
              placeholder="输入模型名称"
            />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Fallback 模型</span>
            <input
              value={fallbackModel}
              onChange={(event) => setFallbackModel(event.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none"
              placeholder="同一供应商下的备用模型"
            />
            <p className="text-xs text-slate-500">当前仅支持同一供应商内的 fallback。</p>
          </label>

          <label className="space-y-2 lg:col-span-2">
            <span className="text-sm font-medium text-slate-700">Base URL</span>
            <input
              value={baseUrl}
              onChange={(event) => setBaseUrl(event.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none"
              placeholder="输入 OpenAI 兼容接口地址"
            />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">API Key</span>
            <input
              type="password"
              value={apiKey}
              onChange={(event) => setApiKey(event.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none"
              placeholder={PROVIDER_ENV_KEYS[provider]}
            />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">超时时间（秒）</span>
            <input
              type="number"
              min="1"
              value={timeoutSeconds}
              onChange={(event) => setTimeoutSeconds(event.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none"
            />
          </label>
        </div>

        {message ? <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{message}</div> : null}
        {error ? <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div> : null}

        <div className="flex flex-wrap items-center gap-3">
          <button
            type="submit"
            disabled={saving}
            className="rounded-2xl bg-slate-950 px-5 py-3 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {saving ? "保存中..." : "保存并热加载"}
          </button>
        </div>
      </form>

      <article className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
        <h3 className="text-lg font-semibold text-slate-900">当前运行模型</h3>
        <div className="mt-3 space-y-2 text-sm text-slate-600">
          <p>Provider：{settings?.runtime.provider ?? "-"}</p>
          <p>Model：{settings?.runtime.model ?? "-"}</p>
          <p>Fallback：{settings?.runtime.fallback_model ?? "-"}</p>
          <p>Base URL：{settings?.runtime.base_url ?? "-"}</p>
          <p>Timeout：{settings?.runtime.timeout_seconds ?? "-"}</p>
        </div>
      </article>
    </div>
  );
}
