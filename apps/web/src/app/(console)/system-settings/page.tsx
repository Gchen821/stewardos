"use client";

import { useMemo, useRef, useState } from "react";

import { useStewardStore } from "@/lib/steward-store";

export default function SystemSettingsPage() {
  const { repositoryConfig, updateRepositoryConfig, resetRepositoryConfig } = useStewardStore();
  const [savedTipVisible, setSavedTipVisible] = useState(false);
  const saveTipTimerRef = useRef<number | undefined>(undefined);

  const previewPaths = useMemo(
    () => ({
      agents: `${repositoryConfig.rootPath.replace(/\/$/, "")}/${repositoryConfig.agentsDir}`,
      skills: `${repositoryConfig.rootPath.replace(/\/$/, "")}/${repositoryConfig.skillsDir}`,
      tools: `${repositoryConfig.rootPath.replace(/\/$/, "")}/${repositoryConfig.toolsDir}`,
    }),
    [repositoryConfig],
  );

  function updateAndTip(next: Partial<typeof repositoryConfig>) {
    updateRepositoryConfig(next);
    setSavedTipVisible(true);
    if (saveTipTimerRef.current) {
      window.clearTimeout(saveTipTimerRef.current);
    }
    saveTipTimerRef.current = window.setTimeout(() => {
      setSavedTipVisible(false);
    }, 1200);
  }

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <p className="inline-flex rounded-full bg-teal-100 px-3 py-1 text-xs font-medium text-teal-800">
          系统设置
        </p>
        <h2 className="text-3xl font-semibold tracking-tight text-slate-950">
          平台级策略与运行开关
        </h2>
        <p className="text-sm text-slate-600">
          仓库路径修改后即时生效并自动持久化到本地，无需额外保存操作。
        </p>
      </header>

      <section className="grid gap-4 lg:grid-cols-2">
        <article className="rounded-2xl border border-teal-200 bg-white p-5">
          <h3 className="text-lg font-semibold">安全策略</h3>
          <ul className="mt-3 space-y-2 text-sm text-slate-700">
            <li>开启高风险操作二次确认</li>
            <li>禁止未授权模型覆写</li>
            <li>强制审计日志保留 90 天</li>
          </ul>
        </article>
        <article className="rounded-2xl border border-teal-200 bg-white p-5">
          <h3 className="text-lg font-semibold">运行参数</h3>
          <ul className="mt-3 space-y-2 text-sm text-slate-700">
            <li>默认会话上下文上限：3000 tokens</li>
            <li>深历史压缩阈值：12 轮</li>
            <li>Agent 在线检查周期：30 秒</li>
          </ul>
        </article>
      </section>

      <section className="rounded-2xl border border-teal-200 bg-white p-5">
        <div className="flex items-center justify-between gap-3">
          <h3 className="text-lg font-semibold">仓库位置配置</h3>
          <div className="flex items-center gap-2">
            {savedTipVisible ? (
              <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-700">
                已实时保存
              </span>
            ) : null}
            <button
              type="button"
              onClick={() => {
                resetRepositoryConfig();
                setSavedTipVisible(true);
              }}
              className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-100"
            >
              恢复默认
            </button>
          </div>
        </div>

        <div className="mt-4 grid gap-3 md:grid-cols-2">
          <label className="space-y-1">
            <span className="text-xs font-medium text-slate-600">根路径</span>
            <input
              value={repositoryConfig.rootPath}
              onChange={(event) => updateAndTip({ rootPath: event.target.value })}
              className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none ring-teal-200 focus:ring"
              placeholder="/workspace/repositories"
            />
          </label>
          <label className="space-y-1">
            <span className="text-xs font-medium text-slate-600">Agents 目录</span>
            <input
              value={repositoryConfig.agentsDir}
              onChange={(event) => updateAndTip({ agentsDir: event.target.value })}
              className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none ring-teal-200 focus:ring"
              placeholder="agents"
            />
          </label>
          <label className="space-y-1">
            <span className="text-xs font-medium text-slate-600">Skills 目录</span>
            <input
              value={repositoryConfig.skillsDir}
              onChange={(event) => updateAndTip({ skillsDir: event.target.value })}
              className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none ring-teal-200 focus:ring"
              placeholder="skills"
            />
          </label>
          <label className="space-y-1">
            <span className="text-xs font-medium text-slate-600">Tools 目录</span>
            <input
              value={repositoryConfig.toolsDir}
              onChange={(event) => updateAndTip({ toolsDir: event.target.value })}
              className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none ring-teal-200 focus:ring"
              placeholder="tools"
            />
          </label>
        </div>

        <label className="mt-4 flex items-center gap-2 text-sm text-slate-700">
          <input
            type="checkbox"
            checked={repositoryConfig.autoBootstrap}
            onChange={(event) => updateAndTip({ autoBootstrap: event.target.checked })}
          />
          启动时自动写入示例仓库资源（auto bootstrap）
        </label>

        <div className="mt-4 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-3 text-xs text-slate-600">
          <p>Agent 仓库：{previewPaths.agents}</p>
          <p>Skill 仓库：{previewPaths.skills}</p>
          <p>Tool 仓库：{previewPaths.tools}</p>
          <p className="mt-2 text-amber-700">
            当前为前端实时配置原型（本地持久化）。下一步可接入后端接口同步到 `.env` / 配置中心。
          </p>
        </div>
      </section>
    </div>
  );
}
