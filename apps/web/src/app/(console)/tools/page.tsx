"use client";

import { FormEvent, useEffect, useState } from "react";

import { createTool, deleteTool, fetchTools, toggleTool, type Tool } from "@/lib/api";

const emptyForm = {
  code: "",
  name: "",
  description: "",
  category: "general",
  risk_level: "low",
};

export default function ToolsPage() {
  const [items, setItems] = useState<Tool[]>([]);
  const [form, setForm] = useState(emptyForm);

  async function load() {
    setItems(await fetchTools());
  }

  useEffect(() => {
    void load();
  }, []);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    await createTool(form);
    setForm(emptyForm);
    await load();
  }

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <p className="inline-flex rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">Tool 仓库</p>
        <h2 className="text-3xl font-semibold tracking-tight text-slate-950">Tool 管理</h2>
      </header>

      <form onSubmit={onSubmit} className="grid gap-3 rounded-2xl border border-slate-200 bg-slate-50 p-4 md:grid-cols-6">
        <input value={form.code} onChange={(e) => setForm((p) => ({ ...p, code: e.target.value }))} placeholder="code" className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm" />
        <input value={form.name} onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))} placeholder="name" className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm" />
        <input value={form.description} onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))} placeholder="description" className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm" />
        <input value={form.category} onChange={(e) => setForm((p) => ({ ...p, category: e.target.value }))} placeholder="category" className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm" />
        <input value={form.risk_level} onChange={(e) => setForm((p) => ({ ...p, risk_level: e.target.value }))} placeholder="risk" className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm" />
        <button type="submit" className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-medium text-white">新增 Tool</button>
      </form>

      <div className="overflow-x-auto rounded-2xl border border-slate-200">
        <table className="min-w-full divide-y divide-slate-200 bg-white text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-3">Code</th>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Category</th>
              <th className="px-4 py-3">Risk</th>
              <th className="px-4 py-3">Enabled</th>
              <th className="px-4 py-3">操作</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {items.map((item) => (
              <tr key={item.id}>
                <td className="px-4 py-3 font-mono text-xs">{item.code}</td>
                <td className="px-4 py-3"><p className="font-medium">{item.name}</p><p className="text-xs text-slate-500">{item.description}</p></td>
                <td className="px-4 py-3">{item.category}</td>
                <td className="px-4 py-3">{item.risk_level}</td>
                <td className="px-4 py-3"><input type="checkbox" checked={item.enabled} onChange={async (e) => { await toggleTool(item.id, e.target.checked); await load(); }} /></td>
                <td className="px-4 py-3"><button type="button" onClick={async () => { if (window.confirm(`删除 ${item.name} ?`)) { await deleteTool(item.id); await load(); } }} className="rounded-lg border border-rose-300 px-2 py-1 text-xs text-rose-700">删除</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
