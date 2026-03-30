"use client";

import { FormEvent, useMemo, useState } from "react";

import { API_ROUTES } from "@/lib/api";
import type { AgentRecord } from "@/lib/types";
import { useStewardStore } from "@/lib/steward-store";

const emptyForm: AgentRecord = {
  id: "",
  name: "",
  description: "",
  avatar: "/globe.svg",
  status: "draft",
  enabled: false,
  permissionEnabled: false,
  updatedAt: "",
};

export default function AgentsPage() {
  const {
    agents,
    upsertAgent,
    deleteAgent,
    toggleAgentEnabled,
    toggleAgentPermission,
  } = useStewardStore();
  const [form, setForm] = useState<AgentRecord>(emptyForm);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  const filtered = useMemo(
    () =>
      agents.filter(
        (item) =>
          item.name.toLowerCase().includes(search.toLowerCase()) ||
          item.id.toLowerCase().includes(search.toLowerCase()),
      ),
    [agents, search],
  );

  function submit(event: FormEvent) {
    event.preventDefault();
    if (!form.id || !form.name) return;
    upsertAgent(form);
    setForm(emptyForm);
    setEditingId(null);
  }

  function edit(item: AgentRecord) {
    setForm(item);
    setEditingId(item.id);
  }

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <p className="inline-flex rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
          Agent 仓库
        </p>
        <h2 className="text-3xl font-semibold tracking-tight text-slate-950">
          Agent 管理与权限启用
        </h2>
      </header>

      <section className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
        <form onSubmit={submit} className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
          <input
            value={form.id}
            onChange={(event) => setForm((prev) => ({ ...prev, id: event.target.value }))}
            placeholder="agent id"
            className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm"
          />
          <input
            value={form.name}
            onChange={(event) =>
              setForm((prev) => ({ ...prev, name: event.target.value }))
            }
            placeholder="name"
            className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm"
          />
          <input
            value={form.description}
            onChange={(event) =>
              setForm((prev) => ({ ...prev, description: event.target.value }))
            }
            placeholder="description"
            className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm"
          />
          <select
            value={form.status}
            onChange={(event) =>
              setForm((prev) => ({
                ...prev,
                status: event.target.value as AgentRecord["status"],
              }))
            }
            className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm"
          >
            <option value="draft">draft</option>
            <option value="online">online</option>
            <option value="offline">offline</option>
          </select>
          <button
            type="submit"
            className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
          >
            {editingId ? "更新 Agent" : "新增 Agent"}
          </button>
        </form>
      </section>

      <section className="space-y-3">
        <input
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="搜索 name/id"
          className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm sm:max-w-sm"
        />
        <div className="overflow-x-auto rounded-2xl border border-slate-200">
          <table className="min-w-full divide-y divide-slate-200 bg-white text-sm">
            <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-3">ID</th>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">启用</th>
                <th className="px-4 py-3">权限</th>
                <th className="px-4 py-3">Updated</th>
                <th className="px-4 py-3">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((item) => (
                <tr key={item.id}>
                  <td className="px-4 py-3 font-mono text-xs text-slate-600">{item.id}</td>
                  <td className="px-4 py-3">
                    <p className="font-medium text-slate-900">{item.name}</p>
                    <p className="text-xs text-slate-500">{item.description}</p>
                  </td>
                  <td className="px-4 py-3">{item.status}</td>
                  <td className="px-4 py-3">
                    <input
                      type="checkbox"
                      checked={item.enabled}
                      onChange={(event) =>
                        toggleAgentEnabled(item.id, event.target.checked)
                      }
                    />
                  </td>
                  <td className="px-4 py-3">
                    <input
                      type="checkbox"
                      checked={item.permissionEnabled}
                      onChange={(event) =>
                        toggleAgentPermission(item.id, event.target.checked)
                      }
                    />
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-500">{item.updatedAt}</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => edit(item)}
                        className="rounded-lg border border-slate-300 px-2 py-1 text-xs"
                      >
                        编辑
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          if (window.confirm(`确认删除 Agent「${item.name}」吗？`)) {
                            deleteAgent(item.id);
                          }
                        }}
                        className="rounded-lg border border-rose-300 px-2 py-1 text-xs text-rose-700"
                      >
                        删除
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <p className="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-3 py-2 text-xs text-slate-600">
        API 预留：{API_ROUTES.agents}
      </p>
    </div>
  );
}
