export default function SystemSettingsPage() {
  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <p className="inline-flex rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
          系统设置
        </p>
        <h2 className="text-3xl font-semibold tracking-tight text-slate-950">
          平台级策略与运行开关
        </h2>
      </header>

      <section className="grid gap-4 lg:grid-cols-2">
        <article className="rounded-2xl border border-slate-200 bg-white p-5">
          <h3 className="text-lg font-semibold">安全策略</h3>
          <ul className="mt-3 space-y-2 text-sm text-slate-700">
            <li>开启高风险操作二次确认</li>
            <li>禁止未授权模型覆写</li>
            <li>强制审计日志保留 90 天</li>
          </ul>
        </article>
        <article className="rounded-2xl border border-slate-200 bg-white p-5">
          <h3 className="text-lg font-semibold">运行参数</h3>
          <ul className="mt-3 space-y-2 text-sm text-slate-700">
            <li>默认会话上下文上限：3000 tokens</li>
            <li>深历史压缩阈值：12 轮</li>
            <li>Agent 在线检查周期：30 秒</li>
          </ul>
        </article>
      </section>
    </div>
  );
}
