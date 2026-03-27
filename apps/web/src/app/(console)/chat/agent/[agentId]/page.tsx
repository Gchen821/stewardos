"use client";

import Image from "next/image";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useMemo, useState } from "react";

import { useStewardStore } from "@/lib/steward-store";

export default function AgentChatPage() {
  const params = useParams<{ agentId: string }>();
  const router = useRouter();
  const { agents, listThreads, createThread } = useStewardStore();
  const [input, setInput] = useState("");

  const agentId = Array.isArray(params.agentId) ? params.agentId[0] : params.agentId;
  const agent = useMemo(
    () => agents.find((item) => item.id === agentId),
    [agents, agentId],
  );

  const agentThreads = listThreads("agent", agentId);

  if (!agent) {
    return (
      <div className="space-y-4">
        <p className="text-sm text-slate-600">未找到该 Agent。</p>
        <Link href="/chat" className="text-sm font-medium text-indigo-700">
          返回主控对话
        </Link>
      </div>
    );
  }

  function send() {
    const text = input.trim();
    if (!text) return;
    const threadId = createThread({
      scope: "agent",
      agentId: agent.id,
      firstUserMessage: text,
      assistantReply: `${agent.name} 已收到：${text}，正在执行并整理结果。`,
    });
    setInput("");
    router.push(`/chat/agent/${agent.id}/session/${threadId}`);
  }

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-center gap-3">
        <div className="rounded-xl bg-indigo-100 p-2">
          <Image src={agent.avatar} alt={agent.name} width={24} height={24} />
        </div>
        <div>
          <h2 className="text-2xl font-semibold">{agent.name}</h2>
          <p className="text-sm text-slate-600">{agent.description}</p>
        </div>
        <span className="ml-auto rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-700">
          状态：{agent.status}
        </span>
        <Link
          href="/chat"
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-100"
        >
          返回主控界面
        </Link>
      </header>

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex flex-col gap-3 sm:flex-row">
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder={`输入第一句话创建 ${agent.name} 新会话，发送后自动进入对话页。`}
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
      </section>

      <section className="space-y-2 rounded-2xl border border-slate-200 bg-slate-50 p-4">
        <h3 className="text-lg font-semibold text-slate-900">{agent.name} 历史聊天记录</h3>
        <div className="max-h-[260px] space-y-2 overflow-auto pr-1">
          {agentThreads.length > 0 ? (
            agentThreads.map((thread) => (
              <button
                key={thread.id}
                type="button"
                onClick={() => router.push(`/chat/agent/${agent.id}/session/${thread.id}`)}
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
              暂无历史记录，先输入第一句话创建新会话。
            </p>
          )}
        </div>
      </section>
    </div>
  );
}
