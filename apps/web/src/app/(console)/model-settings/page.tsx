"use client";

import { useEffect, useState } from "react";

import { fetchModelRuntimeConfig, type ModelRuntimeConfig } from "@/lib/api";
import { useStewardStore } from "@/lib/steward-store";

export default function ModelSettingsPage() {
  const {
    runtimeTokenUsage,
    resetRuntimeTokenUsage,
  } = useStewardStore();
  const runtimeAvailable = runtimeTokenUsage.totalTokens > 0;
  const topModels = Object.entries(runtimeTokenUsage.byModel)
    .sort((a, b) => b[1].totalTokens - a[1].totalTokens)
    .slice(0, 5);
  const [runtimeConfig, setRuntimeConfig] = useState<ModelRuntimeConfig | null>(null);

  useEffect(() => {
    let canceled = false;
    fetchModelRuntimeConfig()
      .then((data) => {
        if (!canceled) setRuntimeConfig(data);
      })
      .catch(() => {
        if (!canceled) setRuntimeConfig(null);
      });
    return () => {
      canceled = true;
    };
  }, []);

  const currentUsedModel = topModels[0]?.[0] ?? runtimeConfig?.current_model ?? "unknown";
  const fallbackModel = runtimeConfig?.fallback_model ?? "未配置";

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h2 className="text-3xl font-semibold tracking-tight text-slate-950">模型设置</h2>
      </header>

      <section className="grid gap-4 lg:grid-cols-2">
        <article className="rounded-2xl border border-slate-200 bg-white p-5">
          <h3 className="text-lg font-semibold">系统默认模型</h3>
          <p className="mt-2 text-sm text-slate-600">{currentUsedModel}</p>
        </article>
        <article className="rounded-2xl border border-slate-200 bg-white p-5">
          <h3 className="text-lg font-semibold">Fallback 策略</h3>
          <p className="mt-2 text-sm text-slate-600">
            primary-failed =&gt; {fallbackModel}
          </p>
        </article>
      </section>

      <section className="space-y-3 rounded-2xl border border-teal-200 bg-teal-50 p-5">
        <div className="flex items-center justify-between gap-2">
          <p className="text-sm font-medium text-teal-700">运行时 Token 统计</p>
          <button
            type="button"
            onClick={resetRuntimeTokenUsage}
            className="rounded-lg border border-teal-300 bg-white px-3 py-1.5 text-xs font-medium text-teal-700 hover:bg-teal-100"
          >
            清零统计
          </button>
        </div>
        <div className="grid gap-4 lg:grid-cols-3">
          <article className="rounded-2xl border border-teal-200 bg-white p-5">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
              已用总 Token
            </p>
            <p className="mt-2 text-3xl font-semibold text-slate-900">
              {runtimeTokenUsage.totalTokens.toLocaleString("zh-CN")}
            </p>
          </article>
          <article className="rounded-2xl border border-teal-200 bg-white p-5">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
              输入 Token
            </p>
            <p className="mt-2 text-2xl font-semibold text-slate-900">
              {runtimeTokenUsage.promptTokens.toLocaleString("zh-CN")}
            </p>
          </article>
          <article className="rounded-2xl border border-teal-200 bg-white p-5">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
              输出 Token
            </p>
            <p className="mt-2 text-2xl font-semibold text-slate-900">
              {runtimeTokenUsage.completionTokens.toLocaleString("zh-CN")}
            </p>
          </article>
        </div>
        {runtimeAvailable ? (
          <div className="rounded-2xl border border-teal-200 bg-white p-4">
            <p className="text-sm font-semibold text-slate-900">模型分布</p>
            <div className="mt-3 space-y-2">
              {topModels.map(([model, usage]) => (
                <div
                  key={model}
                  className="flex items-center justify-between rounded-lg border border-slate-200 px-3 py-2 text-sm"
                >
                  <span className="font-medium text-slate-800">{model}</span>
                  <span className="text-slate-600">
                    {usage.totalTokens.toLocaleString("zh-CN")} tokens
                  </span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <p className="rounded-xl border border-dashed border-teal-300 bg-white px-3 py-2 text-xs text-teal-700">
            暂无统计数据
          </p>
        )}
      </section>

      {runtimeTokenUsage.updatedAt ? (
        <p className="text-xs text-slate-500">
          最近更新：{new Date(runtimeTokenUsage.updatedAt).toLocaleString("zh-CN")}
        </p>
      ) : null}
    </div>
  );
}
