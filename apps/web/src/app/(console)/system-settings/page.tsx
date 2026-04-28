"use client";

import { useEffect, useState } from "react";

import { fetchRuntimeInfo } from "@/lib/api";

export default function SystemSettingsPage() {
  const [info, setInfo] = useState<{ mode: string } | null>(null);

  useEffect(() => {
    fetchRuntimeInfo().then(setInfo).catch(() => setInfo(null));
  }, []);

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <p className="inline-flex rounded-full bg-teal-100 px-3 py-1 text-xs font-medium text-teal-800">系统设置</p>
        <h2 className="text-3xl font-semibold tracking-tight text-slate-950">运行模式与部署信息</h2>
      </header>
      <section className="rounded-2xl border border-teal-200 bg-white p-5">
        <h3 className="text-lg font-semibold">当前模式</h3>
        <p className="mt-2 text-sm text-slate-600">{info?.mode ?? "single-agent-runtime"}</p>
        <p className="mt-4 text-sm text-slate-600">当前只开放子 Agent chat。管家 Agent 保留为未来总控和编排入口。</p>
        <p className="mt-2 text-sm text-slate-600">资产内容存本地文件系统，数据库仅存元数据、绑定关系、会话和运行记录。</p>
      </section>
    </div>
  );
}
