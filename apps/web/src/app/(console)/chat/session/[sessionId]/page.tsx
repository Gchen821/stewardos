"use client";

import { useParams } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import { fetchConversations, fetchMessages, sendChat, type ChatMessage, type Conversation } from "@/lib/api";

export default function SessionPage() {
  const params = useParams<{ sessionId: string }>();
  const sessionId = Number(Array.isArray(params.sessionId) ? params.sessionId[0] : params.sessionId);
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [content, setContent] = useState("");

  async function load() {
    const [conversationRows, messageRows] = await Promise.all([fetchConversations(), fetchMessages(sessionId)]);
    setConversation(conversationRows.find((item) => item.id === sessionId) ?? null);
    setMessages(messageRows);
  }

  useEffect(() => {
    if (!Number.isFinite(sessionId)) return;
    void load();
  }, [sessionId]);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!conversation || !content.trim()) return;
    await sendChat({
      conversation_id: conversation.id,
      target_type: conversation.target_type,
      target_id: conversation.target_id,
      content,
    });
    setContent("");
    await load();
  }

  if (!conversation) {
    return <p className="text-sm text-slate-500">会话不存在。</p>;
  }

  return (
    <div className="space-y-4">
      <header>
        <p className="text-xs text-slate-500">Conversation #{conversation.id}</p>
        <h2 className="text-2xl font-semibold text-slate-900">{conversation.title}</h2>
      </header>

      <div className="space-y-3">
        {messages.map((item) => (
          <div key={item.id} className={item.sender_role === "assistant" ? "flex justify-start" : "flex justify-end"}>
            <div className={item.sender_role === "assistant" ? "max-w-[70%] whitespace-pre-wrap rounded-2xl bg-slate-100 px-4 py-3 text-sm text-slate-900" : "max-w-[70%] whitespace-pre-wrap rounded-2xl bg-slate-900 px-4 py-3 text-sm text-white"}>
              {item.content}
            </div>
          </div>
        ))}
      </div>

      <form onSubmit={onSubmit} className="flex flex-col gap-3 sm:flex-row">
        <textarea value={content} onChange={(e) => setContent(e.target.value)} placeholder="继续输入消息..." className="min-h-20 flex-1 rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm" />
        <button type="submit" className="h-12 rounded-xl bg-slate-900 px-5 text-sm font-medium text-white">发送</button>
      </form>
    </div>
  );
}
