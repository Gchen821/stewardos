import { API_ROUTES } from "@/lib/api";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <p className="inline-flex rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
          账户设置
        </p>
        <h2 className="text-3xl font-semibold tracking-tight text-slate-950">
          用户与权限设置
        </h2>
      </header>

      <section className="grid gap-4 lg:grid-cols-2">
        <article className="rounded-2xl border border-slate-200 bg-white p-5">
          <h3 className="text-lg font-semibold">账户信息</h3>
          <div className="mt-3 space-y-2 text-sm text-slate-700">
            <p>昵称：User Admin</p>
            <p>角色：Platform Admin</p>
            <p>邮箱：admin@steward.local</p>
          </div>
        </article>

        <article className="rounded-2xl border border-slate-200 bg-white p-5">
          <h3 className="text-lg font-semibold">权限模型</h3>
          <div className="mt-3 space-y-2 text-sm text-slate-700">
            <p>system.model.manage</p>
            <p>agent.manage</p>
            <p>skill.manage</p>
            <p>audit.read</p>
            <p>chat.use_agent</p>
          </div>
        </article>
      </section>

      <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-600">
        后端接口预留：{API_ROUTES.permissions}
      </div>
    </div>
  );
}
