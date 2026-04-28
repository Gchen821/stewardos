"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import { createAgent, deleteAgent, fetchAgents, toggleAgent, type Agent } from "@/lib/api";

const emptyForm = {
  code: "",
  name: "",
  description: "",
  type: "default",
  runtime_status: "draft",
};

export default function AgentsPage() {
  const [items, setItems] = useState<Agent[]>([]);
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  const filtered = useMemo(
    () =>
      items.filter(
        (item) =>
          item.name.toLowerCase().includes(search.toLowerCase()) ||
          item.code.toLowerCase().includes(search.toLowerCase()),
      ),
    [items, search],
  );

  async function load() {
    try {
      setLoading(true);
      setItems(await fetchAgents());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载 Agent 失败");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    await createAgent(form);
    setForm(emptyForm);
    await load();
  }

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <p className="inline-flex rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">Agent 仓库</p>
        <h2 className="text-3xl font-semibold tracking-tight text-slate-950">Agent 管理</h2>
      </header>

      <section className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
        <form onSubmit={onSubmit} className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
          <input value={form.code} onChange={(e) => setForm((p) => ({ ...p, code: e.target.value }))} placeholder="agent code" className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm" />
          <input value={form.name} onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))} placeholder="name" className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm" />
          <input value={form.description} onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))} placeholder="description" className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm" />
          <input value={form.type} onChange={(e) => setForm((p) => ({ ...p, type: e.target.value }))} placeholder="type" className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm" />
          <button type="submit" className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800">新增 Agent</button>
        </form>
      </section>

      {error ? <p className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
      {loading ? <p className="text-sm text-slate-500">加载中...</p> : null}

      <section className="space-y-3">
        <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="搜索 name/code" className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm sm:max-w-sm" />
      <div className="overflow-x-auto rounded-2xl border border-slate-200">
        <table className="min-w-full divide-y divide-slate-200 bg-white text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-3">Code</th>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Enabled</th>
              <th className="px-4 py-3">Updated</th>
              <th className="px-4 py-3">操作</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filtered.map((item) => (
              <tr key={item.id}>
                <td className="px-4 py-3 font-mono text-xs">{item.code}</td>
                <td className="px-4 py-3"><p className="font-medium">{item.name}</p><p className="text-xs text-slate-500">{item.description}</p></td>
                <td className="px-4 py-3">{item.runtime_status}</td>
                <td className="px-4 py-3">
                  <input type="checkbox" checked={item.enabled} onChange={async (e) => { await toggleAgent(item.id, e.target.checked); await load(); }} />
                </td>
                <td className="px-4 py-3 text-xs text-slate-500">{new Date(item.updated_at).toLocaleString("zh-CN")}</td>
                <td className="px-4 py-3">
                  <button type="button" onClick={async () => { if (window.confirm(`删除 ${item.name} ?`)) { await deleteAgent(item.id); await load(); } }} className="rounded-lg border border-rose-300 px-2 py-1 text-xs text-rose-700">删除</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      </section>
    </div>
  );
}
