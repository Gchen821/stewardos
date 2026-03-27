"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

import { apiPlanNote } from "@/lib/api";
import { useStewardStore } from "@/lib/steward-store";

export default function ChatPage() {
  const {
    agents,
    upsertAgent,
    listThreads,
    createThread,
  } = useStewardStore();
  const router = useRouter();
  const searchParams = useSearchParams();
  const conversationId = searchParams.get("conversation");

  const [input, setInput] = useState("");
  const [showPlusMenu, setShowPlusMenu] = useState(false);
  const [showAgentPicker, setShowAgentPicker] = useState(false);
  const [selectedAgentIds, setSelectedAgentIds] = useState<string[]>(
    agents
      .filter((item) => item.enabled && item.permissionEnabled && item.status === "online")
      .map((item) => item.id),
  );
  const [activeAgentId, setActiveAgentId] = useState<string | null>(
    agents.find((item) => item.enabled && item.permissionEnabled && item.status === "online")
      ?.id ?? null,
  );

  const enabledAgents = agents.filter(
    (item) => item.enabled && item.permissionEnabled && item.status === "online",
  );
  const currentAgent = enabledAgents.find((item) => item.id === activeAgentId) ?? enabledAgents[0];
  const butlerThreads = listThreads("butler");

  function toggleAgentSelection(agentId: string) {
    const found = agents.find((item) => item.id === agentId);
    if (!found) return;

    const isSelected = selectedAgentIds.includes(agentId);
    if (isSelected) {
      setSelectedAgentIds((prev) => prev.filter((id) => id !== agentId));
      setActiveAgentId((prev) => (prev === agentId ? null : prev));
      return;
    }

    upsertAgent({
      ...found,
      status: "online",
      enabled: true,
      permissionEnabled: true,
    });

    setSelectedAgentIds((prev) =>
      prev.includes(agentId) ? prev : [...prev, agentId],
    );
    setActiveAgentId(agentId);
  }

  function send() {
    const text = input.trim();
    if (!text) return;
    const threadId = createThread({
      scope: "butler",
      firstUserMessage: text,
      assistantReply: `主控管家已收到：${text}，正在拆解任务并准备分派。`,
    });
    setInput("");
    router.push(`/chat/session/${threadId}`);
  }

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <p className="inline-flex rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-800">
          主控管家对话
        </p>
        <h2 className="text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">
          统一任务入口
        </h2>
        <p className="text-sm text-slate-600 sm:text-base">{apiPlanNote}</p>
        {conversationId ? (
          <p className="text-xs text-slate-500">当前会话：{conversationId}</p>
        ) : null}
      </header>

      <section className="w-full rounded-3xl border border-slate-200 bg-gradient-to-b from-slate-50 to-white p-5 shadow-sm">
        <div className="mt-4 flex flex-col gap-3 sm:flex-row">
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="输入第一句话作为聊天主题，发送后自动进入会话页。"
            className="min-h-24 flex-1 rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm outline-none ring-indigo-200 transition focus:ring"
          />
          <button
            type="button"
            onClick={send}
            className="h-12 rounded-xl bg-slate-900 px-5 text-sm font-medium text-white hover:bg-slate-800"
          >
            发送
          </button>
        </div>
        <div className="mt-3 flex items-center justify-between">
          <div className="relative">
            <button
              type="button"
              onClick={() => setShowPlusMenu((prev) => !prev)}
              className="flex h-9 w-9 items-center justify-center rounded-full border border-slate-300 bg-white text-xl text-slate-700 hover:bg-slate-100"
            >
              +
            </button>
            {showPlusMenu ? (
              <div className="absolute left-0 top-11 z-20 w-40 rounded-xl border border-slate-200 bg-white p-2 shadow-lg">
                <button
                  type="button"
                  onClick={() => {
                    setShowAgentPicker(true);
                    setShowPlusMenu(false);
                  }}
                  className="w-full rounded-lg px-3 py-2 text-left text-sm text-slate-700 hover:bg-slate-100"
                >
                  添加 Agent
                </button>
              </div>
            ) : null}
          </div>
          <p className="text-xs text-slate-500">
            当前选中 Agent：{currentAgent ? currentAgent.name : "未选择"}
          </p>
        </div>
      </section>

      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-semibold text-slate-900">已启用子 Agent</h3>
          <span className="text-xs text-slate-500">
            共 {enabledAgents.length} 个可直接对话
          </span>
        </div>
        <div className="flex w-full gap-4 overflow-x-auto pb-2">
          {enabledAgents.map((agent) => (
            <Link
              key={agent.id}
              href={`/chat/agent/${agent.id}`}
              onClick={() => setActiveAgentId(agent.id)}
              className="group relative z-0 min-w-[280px] flex-1 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:z-10 hover:border-indigo-400 hover:shadow-lg"
            >
              <div className="flex items-start gap-3">
                <div className="rounded-xl bg-indigo-50 p-2">
                  <Image src={agent.avatar} alt={agent.name} width={24} height={24} />
                </div>
                <div className="space-y-1">
                  <p className="font-semibold text-slate-900 group-hover:text-indigo-700">
                    {agent.name}
                  </p>
                  <p className="text-sm text-slate-600">{agent.description}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      <section className="space-y-2 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900">主控历史聊天记录</h3>
        <div className="max-h-[260px] space-y-2 overflow-auto pr-1">
          {butlerThreads.length > 0 ? (
            butlerThreads.map((thread) => (
              <button
                key={thread.id}
                type="button"
                onClick={() => router.push(`/chat/session/${thread.id}`)}
                className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-left text-sm shadow-sm transition hover:border-indigo-300"
              >
                <p className="font-medium text-slate-900">{thread.title}</p>
                <p className="mt-1 text-xs text-slate-500">
                  {thread.messageCount} 条消息 · 最近更新 {new Date(thread.updatedAt).toLocaleString("zh-CN")}
                </p>
              </button>
            ))
          ) : (
            <p className="rounded-xl border border-dashed border-slate-300 bg-white px-4 py-5 text-sm text-slate-500">
              暂无历史记录，直接输入第一句话即可创建新会话。
            </p>
          )}
        </div>
      </section>

      {showAgentPicker ? (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-slate-900/50 p-4">
          <div className="w-full max-w-4xl rounded-3xl border border-slate-200 bg-white p-5 shadow-2xl">
            <div className="flex items-center justify-between">
              <h4 className="text-xl font-semibold text-slate-900">添加 Agent</h4>
              <button
                type="button"
                onClick={() => setShowAgentPicker(false)}
                className="rounded-lg border border-slate-300 px-3 py-1 text-sm text-slate-700 hover:bg-slate-100"
              >
                关闭
              </button>
            </div>
            <p className="mt-2 text-sm text-slate-500">
              点击 Agent 卡片即可加入主控会话。选中卡片会高亮为绿色并带对勾。
            </p>
            <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {agents.map((agent) => {
                const selected = selectedAgentIds.includes(agent.id);
                return (
                  <button
                    type="button"
                    key={agent.id}
                    onClick={() => toggleAgentSelection(agent.id)}
                    className={
                      selected
                        ? "rounded-2xl border border-emerald-300 bg-emerald-50 p-4 text-left shadow-sm"
                        : "rounded-2xl border border-slate-200 bg-white p-4 text-left shadow-sm hover:border-indigo-300"
                    }
                  >
                    <div className="flex items-start gap-3">
                      <div className="rounded-xl bg-indigo-50 p-2">
                        <Image src={agent.avatar} alt={agent.name} width={22} height={22} />
                      </div>
                      <div className="min-w-0">
                        <p className="font-semibold text-slate-900">{agent.name}</p>
                        <p className="mt-1 text-xs text-slate-600">{agent.description}</p>
                      </div>
                      {selected ? (
                        <span className="ml-auto rounded-full bg-emerald-600 px-2 py-0.5 text-xs font-semibold text-white">
                          ✓
                        </span>
                      ) : null}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
