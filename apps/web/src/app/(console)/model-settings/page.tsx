import { API_ROUTES } from "@/lib/api";

export default function ModelSettingsPage() {
  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <p className="inline-flex rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
          模型设置
        </p>
        <h2 className="text-3xl font-semibold tracking-tight text-slate-950">
          模型路由与默认模型
        </h2>
      </header>

      <section className="grid gap-4 lg:grid-cols-2">
        <article className="rounded-2xl border border-slate-200 bg-white p-5">
          <h3 className="text-lg font-semibold">系统默认模型</h3>
          <p className="mt-2 text-sm text-slate-600">gpt-4.1-mini</p>
          <p className="mt-3 text-xs text-slate-500">
            后端将按优先级：会话覆盖 &gt; Agent绑定 &gt; Butler默认 &gt; 系统默认。
          </p>
        </article>
        <article className="rounded-2xl border border-slate-200 bg-white p-5">
          <h3 className="text-lg font-semibold">Fallback 策略</h3>
          <p className="mt-2 text-sm text-slate-600">primary-failed =&gt; fallback-model</p>
          <p className="mt-3 text-xs text-slate-500">所有切换事件记录到 llm_call_logs。</p>
        </article>
      </section>

      <p className="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-3 py-2 text-xs text-slate-600">
        API 预留：{API_ROUTES.modelProviders}
      </p>
    </div>
  );
}
