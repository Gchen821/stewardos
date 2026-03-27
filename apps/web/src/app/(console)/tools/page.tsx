import { API_ROUTES, apiPlanNote } from "@/lib/api";

const tools = [
  { name: "Memory Tool", desc: "工作记忆与结构化笔记写入能力", status: "planned" },
  { name: "RAG Tool", desc: "检索证据注入上下文", status: "planned" },
  { name: "MCP Tool", desc: "外部工具协议适配", status: "planned" },
  { name: "Terminal Tool", desc: "受控命令执行", status: "planned" },
];

export default function ToolsPage() {
  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <p className="inline-flex rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
          Tools 仓库
        </p>
        <h2 className="text-3xl font-semibold tracking-tight text-slate-950">
          工具能力目录
        </h2>
        <p className="text-sm text-slate-600">{apiPlanNote}</p>
      </header>

      <div className="grid gap-4 sm:grid-cols-2">
        {tools.map((item) => (
          <article
            key={item.name}
            className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
          >
            <p className="text-xs uppercase tracking-wide text-slate-500">{item.status}</p>
            <h3 className="mt-2 text-xl font-semibold">{item.name}</h3>
            <p className="mt-2 text-sm text-slate-600">{item.desc}</p>
          </article>
        ))}
      </div>

      <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-600">
        后端接口预留：{API_ROUTES.skills}、{API_ROUTES.modelProviders}
      </div>
    </div>
  );
}
