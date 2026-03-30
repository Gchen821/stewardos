"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { type KeyboardEvent, useEffect, useMemo, useRef, useState } from "react";

import { getApiBaseUrl, streamButlerChat } from "@/lib/api";
import { useStewardStore } from "@/lib/steward-store";

export default function ButlerSessionPage() {
  const params = useParams<{ sessionId: string }>();
  const sessionId = Array.isArray(params.sessionId) ? params.sessionId[0] : params.sessionId;
  const {
    getThreadById,
    getThreadMessages,
    appendMessage,
    recordRuntimeTokenUsage,
  } = useStewardStore();
  const [input, setInput] = useState("");
  const [streamingText, setStreamingText] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamError, setStreamError] = useState<string | null>(null);
  const autoSentRef = useRef(false);
  const messageViewportRef = useRef<HTMLDivElement | null>(null);
  const streamAbortRef = useRef<AbortController | null>(null);
  const activeRequestIdRef = useRef(0);

  const thread = getThreadById(sessionId);
  const messages = getThreadMessages(sessionId);
  const title = useMemo(() => thread?.title ?? "主控会话", [thread?.title]);
  const isButlerThread = Boolean(thread && thread.scope === "butler");

  async function sendWithApi(text: string, appendUser: boolean, force = false) {
    if (!text.trim() || (!force && isStreaming)) return;
    if (!getApiBaseUrl()) {
      setStreamError("未配置 NEXT_PUBLIC_API_BASE_URL，无法调用后端接口。");
      return;
    }
    setStreamError(null);
    setIsStreaming(true);
    setStreamingText("");

    if (appendUser) {
      appendMessage({ threadId: sessionId, role: "user", content: text });
    }

    let assistantBuffer = "";
    const requestId = Date.now();
    activeRequestIdRef.current = requestId;
    const controller = new AbortController();
    streamAbortRef.current = controller;
    try {
      await streamButlerChat({
        conversationId: sessionId,
        content: text,
        signal: controller.signal,
        onDelta: (delta) => {
          if (activeRequestIdRef.current !== requestId) return;
          assistantBuffer += delta;
          setStreamingText((prev) => prev + delta);
        },
        onDone: (event) => {
          if (activeRequestIdRef.current !== requestId) return;
          const assistantText = assistantBuffer.trim();
          if (assistantText) {
            appendMessage({
              threadId: sessionId,
              role: "assistant",
              content: assistantText,
            });
          }
          const usage = event.metadata?.agent?.usage;
          if (usage) {
            const selectedModel =
              event.selected_model
              ?? event.metadata?.agent?.selected_model
              ?? "unknown";
            recordRuntimeTokenUsage({
              model: selectedModel,
              promptTokens: usage.prompt_tokens ?? 0,
              completionTokens: usage.completion_tokens ?? 0,
              totalTokens: usage.total_tokens,
            });
          }
        },
        onError: (message) => {
          if (activeRequestIdRef.current !== requestId) return;
          setStreamError(message);
        },
      });
    } catch (error) {
      if (activeRequestIdRef.current !== requestId) {
        return;
      }
      if (error instanceof Error && error.name === "AbortError") {
        const partialText = assistantBuffer.trim();
        if (partialText) {
          appendMessage({
            threadId: sessionId,
            role: "assistant",
            content: partialText,
          });
        }
        return;
      }
      const message = error instanceof Error ? error.message : "会话请求失败";
      setStreamError(message);
    } finally {
      if (activeRequestIdRef.current === requestId) {
        streamAbortRef.current = null;
        setIsStreaming(false);
        setStreamingText("");
      }
    }
  }

  function stopStreaming() {
    if (!isStreaming) return;
    const partialText = streamingText.trim();
    if (partialText) {
      appendMessage({
        threadId: sessionId,
        role: "assistant",
        content: partialText,
      });
    }
    activeRequestIdRef.current = Date.now();
    streamAbortRef.current?.abort();
    streamAbortRef.current = null;
    setIsStreaming(false);
    setStreamingText("");
  }

  useEffect(() => {
    if (autoSentRef.current) return;
    if (!isButlerThread) return;
    if (messages.length !== 1 || messages[0]?.role !== "user") return;
    autoSentRef.current = true;
    void sendWithApi(messages[0].content, false);
  }, [isButlerThread, messages]);

  useEffect(() => {
    const viewport = messageViewportRef.current;
    if (!viewport) return;
    viewport.scrollTop = viewport.scrollHeight;
  }, [messages, streamingText]);

  if (!isButlerThread) {
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
    let forceSend = false;
    if (isStreaming) {
      stopStreaming();
      forceSend = true;
    }
    void sendWithApi(text, true, forceSend);
    setInput("");
  }

  function onInputKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key !== "Enter" || event.shiftKey) return;
    event.preventDefault();
    send();
  }

  return (
    <div className="relative mx-auto min-h-[calc(100vh-180px)] w-full max-w-5xl pb-28">
      <section className="min-h-[60vh] px-4 py-3">
        <div className="mb-5">
          <p className="text-xs text-slate-500">主控会话</p>
          <h2 className="text-xl font-semibold text-slate-900">{title}</h2>
        </div>
        <div
          ref={messageViewportRef}
          className="h-[calc(100vh-320px)] min-h-[360px] overflow-y-auto pr-1"
        >
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
            {isStreaming && streamingText ? (
              <div className="flex justify-start">
                <div className="max-w-[50%] w-fit whitespace-pre-wrap break-words rounded-2xl bg-slate-100 px-4 py-3 text-sm text-slate-900">
                  {streamingText}
                </div>
              </div>
            ) : null}
          </div>
        </div>
      </section>

      <section className="fixed bottom-6 left-1/2 z-20 w-[min(820px,calc(100%-2rem))] -translate-x-1/2 rounded-2xl border border-slate-200 bg-white/95 p-3 shadow-lg backdrop-blur">
        {streamError ? (
          <p className="mb-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
            {streamError}
          </p>
        ) : null}
        {!getApiBaseUrl() ? (
          <p className="mb-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-700">
            未配置 `NEXT_PUBLIC_API_BASE_URL`，无法调用后端流式接口。
          </p>
        ) : null}
        <div className="flex flex-col gap-3 sm:flex-row">
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={onInputKeyDown}
            placeholder="继续输入消息..."
            className="min-h-16 flex-1 rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm outline-none ring-indigo-200 transition focus:ring"
          />
          <button
            type="button"
            onClick={isStreaming ? stopStreaming : send}
            disabled={!getApiBaseUrl()}
            className={
              isStreaming
                ? "h-12 rounded-xl bg-amber-600 px-5 text-sm font-medium text-white hover:bg-amber-500"
                : "h-12 rounded-xl bg-slate-900 px-5 text-sm font-medium text-white hover:bg-slate-800"
            }
          >
            {isStreaming ? "停止生成" : "发送"}
          </button>
        </div>
      </section>
    </div>
  );
}
