"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useMemo, useState } from "react";

import { useStewardStore } from "@/lib/steward-store";

export default function AgentSessionPage() {
  const params = useParams<{ agentId: string; sessionId: string }>();
  const agentId = Array.isArray(params.agentId) ? params.agentId[0] : params.agentId;
  const sessionId = Array.isArray(params.sessionId) ? params.sessionId[0] : params.sessionId;

  const { agents, getThreadById, getThreadMessages, appendMessage } = useStewardStore();
  const [input, setInput] = useState("");

  const agent = agents.find((item) => item.id === agentId);
  const thread = getThreadById(sessionId);
  const messages = getThreadMessages(sessionId);
  const title = useMemo(() => thread?.title ?? "子 Agent 会话", [thread?.title]);

  if (!agent || !thread || thread.scope !== "agent" || thread.agentId !== agentId) {
    return (
      <div className="space-y-4">
        <p className="text-sm text-slate-600">未找到该 Agent 会话。</p>
        <Link href={`/chat/agent/${agentId}`} className="text-sm font-medium text-indigo-700">
          返回 Agent 历史
        </Link>
      </div>
    );
  }

  function send() {
    const text = input.trim();
    if (!text) return;
    appendMessage({ threadId: sessionId, role: "user", content: text });
    appendMessage({
      threadId: sessionId,
      role: "assistant",
      content: `${agent.name} 正在继续处理：${text}`,
    });
    setInput("");
  }

  return (
    <div className="relative mx-auto min-h-[calc(100vh-180px)] w-full max-w-5xl pb-28">
      <section className="min-h-[60vh] px-4 py-3">
        <div className="mb-5 flex items-start justify-between gap-3">
          <div>
            <p className="text-xs text-slate-500">{agent.name} 会话</p>
            <h2 className="text-xl font-semibold text-slate-900">{title}</h2>
          </div>
          <Link
            href="/chat"
            className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-100"
          >
            返回主控界面
          </Link>
        </div>
        <div className="space-y-3">
          {messages.map((item) => (
            <div key={item.id} className={item.role === "assistant" ? "flex justify-start" : "flex justify-end"}>
              <div
                className={
                  item.role === "assistant"
                    ? "max-w-[50%] w-fit whitespace-pre-wrap break-words rounded-2xl bg-slate-100 px-4 py-3 text-sm text-slate-900"
                    : "max-w-[50%] w-fit whitespace-pre-wrap break-words rounded-2xl bg-slate-900 px-4 py-3 text-sm text-white"
                }
              >
                {item.content}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="fixed bottom-6 left-1/2 z-20 w-[min(820px,calc(100%-2rem))] -translate-x-1/2 rounded-2xl border border-slate-200 bg-white/95 p-3 shadow-lg backdrop-blur">
        <div className="flex flex-col gap-3 sm:flex-row">
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder={`继续给 ${agent.name} 发送消息...`}
            className="min-h-16 flex-1 rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm outline-none ring-indigo-200 transition focus:ring"
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
    </div>
  );
}
