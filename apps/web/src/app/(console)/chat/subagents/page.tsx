"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { fetchAgents, fetchConversations, sendChat, type Agent, type Conversation } from "@/lib/api";

export default function SubAgentChatPage() {
  const router = useRouter();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [agentId, setAgentId] = useState<number | null>(null);
  const [content, setContent] = useState("");
  const [showAgentPicker, setShowAgentPicker] = useState(false);

  async function load() {
    const [agentRows, conversationRows] = await Promise.all([fetchAgents(), fetchConversations()]);
    setAgents(agentRows.filter((item) => item.enabled && !item.is_deleted));
    setConversations(conversationRows);
    setAgentId((prev) => prev ?? agentRows.find((item) => item.enabled && !item.is_deleted)?.id ?? null);
  }

  useEffect(() => {
    void load();
  }, []);

  const selectedAgent = useMemo(
    () => agents.find((item) => item.id === agentId) ?? null,
    [agentId, agents],
  );

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!agentId || !content.trim()) return;
    const result = await sendChat({
      target_type: "agent",
      target_id: agentId,
      content,
    });
    setContent("");
    router.push(`/chat/session/${result.conversation_id}`);
  }

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <p className="inline-flex rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-800">子 Agent 对话</p>
        <h2 className="text-3xl font-semibold tracking-tight text-slate-950">直接对子 Agent 发起会话</h2>
        <p className="text-sm text-slate-600">这里继续走当前真实后端链路。选择一个 Agent，发送消息后进入该会话。</p>
      </header>

      <section className="w-full rounded-3xl border border-slate-200 bg-gradient-to-b from-slate-50 to-white p-5 shadow-sm">
        <form onSubmit={onSubmit} className="space-y-3">
          <button
            type="button"
            onClick={() => setShowAgentPicker(true)}
            className="flex w-full items-center justify-between rounded-2xl border border-slate-300 bg-white px-4 py-3 text-left"
          >
            <div>
              <p className="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">当前 Agent</p>
              <p className="mt-1 text-sm font-medium text-slate-900">
                {selectedAgent ? selectedAgent.name : "点击选择 Agent"}
              </p>
              <p className="mt-1 line-clamp-1 text-xs text-slate-500">
                {selectedAgent ? selectedAgent.description || "暂无描述" : "仅展示已激活的 Agent"}
              </p>
            </div>
            <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-800">
              选择 Agent
            </span>
          </button>
          <div className="mt-4 flex flex-col gap-3 sm:flex-row">
            <textarea value={content} onChange={(e) => setContent(e.target.value)} placeholder="输入第一句话作为聊天主题，发送后自动进入会话页。" className="min-h-24 flex-1 rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm outline-none ring-indigo-200 transition focus:ring" />
            <button type="submit" className="h-12 rounded-xl bg-slate-900 px-5 text-sm font-medium text-white hover:bg-slate-800">发送</button>
          </div>
        </form>
      </section>

      {showAgentPicker ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/45 px-4 py-8">
          <div className="flex max-h-[85vh] w-full max-w-6xl flex-col overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-200 px-6 py-5">
              <div>
                <p className="text-sm font-medium text-amber-700">选择 Agent</p>
                <h3 className="mt-1 text-2xl font-semibold text-slate-950">已激活 Agent 列表</h3>
              </div>
              <button
                type="button"
                onClick={() => setShowAgentPicker(false)}
                className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50"
              >
                关闭
              </button>
            </div>

            <div className="overflow-y-auto px-6 py-6">
              {agents.length ? (
                <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
                  {agents.map((item) => {
                    const active = item.id === agentId;
                    return (
                      <button
                        key={item.id}
                        type="button"
                        onClick={() => {
                          setAgentId(item.id);
                          setShowAgentPicker(false);
                        }}
                        className={`rounded-3xl border p-5 text-left shadow-sm transition ${
                          active
                            ? "border-amber-300 bg-amber-50"
                            : "border-slate-200 bg-white hover:border-amber-200 hover:bg-amber-50/50"
                        }`}
                      >
                        <p className="text-lg font-semibold text-slate-950">{item.name}</p>
                        <p className="mt-3 line-clamp-4 text-sm leading-6 text-slate-600">
                          {item.description || "暂无描述"}
                        </p>
                      </button>
                    );
                  })}
                </div>
              ) : (
                <div className="rounded-3xl border border-dashed border-slate-300 bg-slate-50 px-6 py-12 text-center">
                  <p className="text-sm text-slate-500">当前没有可选的激活 Agent。</p>
                </div>
              )}
            </div>
          </div>
        </div>
      ) : null}

      <section className="grid gap-4 lg:grid-cols-[1.25fr_0.75fr]">
        <div className="space-y-3 rounded-2xl border border-slate-200 bg-white p-4">
          <h3 className="text-lg font-semibold text-slate-900">最近子 Agent 会话</h3>
          <div className="space-y-2">
            {conversations.map((item) => (
              <Link key={item.id} href={`/chat/session/${item.id}`} className="block rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm shadow-sm transition hover:border-teal-300">
                <p className="font-medium text-slate-900">{item.title}</p>
                <p className="mt-1 text-xs text-slate-500">Target Agent ID: {item.target_id} · 更新于 {new Date(item.updated_at).toLocaleString("zh-CN")}</p>
              </Link>
            ))}
          </div>
        </div>
        <div className="space-y-3 rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <h3 className="text-lg font-semibold text-slate-900">执行说明</h3>
          <p className="text-sm text-slate-600">子 Agent 页面负责当前可用的真实执行链路。</p>
          <p className="text-sm text-slate-600">管家页保留原始交互框架和绑定视图，用于后续扩展到总控编排。</p>
        </div>
      </section>
    </div>
  );
}
