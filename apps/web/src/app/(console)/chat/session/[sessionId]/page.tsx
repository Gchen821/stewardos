"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useMemo, useState } from "react";

import { useStewardStore } from "@/lib/steward-store";

export default function ButlerSessionPage() {
  const params = useParams<{ sessionId: string }>();
  const sessionId = Array.isArray(params.sessionId) ? params.sessionId[0] : params.sessionId;
  const { getThreadById, getThreadMessages, appendMessage } = useStewardStore();
  const [input, setInput] = useState("");

  const thread = getThreadById(sessionId);
  const messages = getThreadMessages(sessionId);
  const title = useMemo(() => thread?.title ?? "主控会话", [thread?.title]);

  if (!thread || thread.scope !== "butler") {
    return (
      <div className="space-y-4">
        <p className="text-sm text-slate-600">未找到该主控会话。</p>
        <Link href="/chat" className="text-sm font-medium text-indigo-700">
          返回主控历史
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
      content: `主控管家已继续处理：${text}`,
    });
    setInput("");
  }

  return (
    <div className="relative mx-auto min-h-[calc(100vh-180px)] w-full max-w-5xl pb-28">
      <section className="min-h-[60vh] px-4 py-3">
        <div className="mb-5">
          <p className="text-xs text-slate-500">主控会话</p>
          <h2 className="text-xl font-semibold text-slate-900">{title}</h2>
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
            placeholder="继续输入消息..."
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
