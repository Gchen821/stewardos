"use client";

import { type ReactNode, type UIEvent, useEffect, useMemo, useRef, useState } from "react";

import { type Agent, type Skill, type Tool } from "@/lib/api";
import { fetchAgents, fetchConversations, fetchSkills, fetchTools, sendChat, type Conversation } from "@/lib/api";

type ButlerMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

const CARD_PAGE_SIZE = 6;

function CardSection({
  title,
  emptyText,
  children,
  onScroll,
}: {
  title: string;
  emptyText: string;
  children: ReactNode;
  onScroll?: (event: UIEvent<HTMLDivElement>) => void;
}) {
  return (
    <section className="flex min-h-0 flex-1 flex-col rounded-2xl border border-slate-200 bg-white p-4">
      <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
      <div className="mt-3 min-h-0 flex-1 overflow-y-auto pr-1" onScroll={onScroll}>
        {children ?? <p className="text-sm text-slate-500">{emptyText}</p>}
      </div>
    </section>
  );
}

export default function ButlerChatPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [tools, setTools] = useState<Tool[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [content, setContent] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [showPlusMenu, setShowPlusMenu] = useState(false);
  const [showAgentPicker, setShowAgentPicker] = useState(false);
  const [showSkillPicker, setShowSkillPicker] = useState(false);
  const [showToolPicker, setShowToolPicker] = useState(false);
  const [boundAgentIds, setBoundAgentIds] = useState<number[]>([]);
  const [boundSkillIds, setBoundSkillIds] = useState<number[]>([]);
  const [boundToolIds, setBoundToolIds] = useState<number[]>([]);
  const [visibleAgentCount, setVisibleAgentCount] = useState(CARD_PAGE_SIZE);
  const [visibleHistoryCount, setVisibleHistoryCount] = useState(CARD_PAGE_SIZE);
  const [messages, setMessages] = useState<ButlerMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "我是主管家入口。这里会按 planner -> 执行已注册资产 -> reflection 的流程推进任务。",
    },
  ]);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const messageViewportRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    async function load() {
      const [agentRows, skillRows, toolRows, conversationRows] = await Promise.all([
        fetchAgents(),
        fetchSkills(),
        fetchTools(),
        fetchConversations(),
      ]);
      setAgents(agentRows.filter((item) => item.enabled && !item.is_deleted));
      setSkills(skillRows.filter((item) => item.enabled && !item.is_deleted));
      setTools(toolRows.filter((item) => item.enabled && !item.is_deleted));
      setConversations(conversationRows.filter((item) => item.target_type === "butler"));
    }
    void load();
  }, []);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    resizeTextarea(textarea);
  }, [content]);

  useEffect(() => {
    const viewport = messageViewportRef.current;
    if (!viewport) return;
    viewport.scrollTop = viewport.scrollHeight;
  }, [messages]);

  const boundAgents = useMemo(
    () => agents.filter((item) => boundAgentIds.includes(item.id)),
    [agents, boundAgentIds],
  );
  const boundSkills = useMemo(
    () => skills.filter((item) => boundSkillIds.includes(item.id)),
    [skills, boundSkillIds],
  );
  const boundTools = useMemo(
    () => tools.filter((item) => boundToolIds.includes(item.id)),
    [tools, boundToolIds],
  );
  const visibleBoundAgents = boundAgents.slice(0, visibleAgentCount);
  const visibleConversations = conversations.slice(0, visibleHistoryCount);

  function toggleNumber(list: number[], value: number, setter: (value: number[]) => void) {
    setter(list.includes(value) ? list.filter((item) => item !== value) : [...list, value]);
  }

  function resizeTextarea(textarea: HTMLTextAreaElement) {
    const computedStyle = window.getComputedStyle(textarea);
    const minHeight = Number.parseFloat(computedStyle.minHeight) || 48;
    const maxHeight = Number.parseFloat(computedStyle.maxHeight) || 224;

    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(Math.max(textarea.scrollHeight, minHeight), maxHeight)}px`;
  }

  function loadMoreOnScroll(
    event: UIEvent<HTMLDivElement>,
    visibleCount: number,
    totalCount: number,
    setter: (value: number) => void,
  ) {
    const target = event.currentTarget;
    const nearBottom = target.scrollTop + target.clientHeight >= target.scrollHeight - 24;
    if (nearBottom && visibleCount < totalCount) {
      setter(Math.min(visibleCount + CARD_PAGE_SIZE, totalCount));
    }
  }

  async function send() {
    const text = content.trim();
    if (!text || isSending) return;
    const nextUser: ButlerMessage = { id: `u-${Date.now()}`, role: "user", content: text };
    setMessages((prev) => [...prev, nextUser]);
    setContent("");
    setShowPlusMenu(false);
    setShowAgentPicker(false);
    setShowSkillPicker(false);
    setShowToolPicker(false);
    setIsSending(true);

    try {
      const result = await sendChat({
        conversation_id: conversationId,
        target_type: "butler",
        target_id: 0,
        content: text,
        bound_agent_ids: boundAgentIds,
        bound_skill_ids: boundSkillIds,
        bound_tool_ids: boundToolIds,
      });
      setConversationId(result.conversation_id);
      setMessages((prev) => [
        ...prev,
        {
          id: `a-${Date.now()}`,
          role: "assistant",
          content: result.reply,
        },
      ]);
      const conversationRows = await fetchConversations();
      setConversations(conversationRows.filter((item) => item.target_type === "butler"));
    } catch (error) {
      const message = error instanceof Error ? error.message : "主管家执行失败";
      setMessages((prev) => [
        ...prev,
        {
          id: `a-${Date.now()}`,
          role: "assistant",
          content: `主管家执行失败：${message}`,
        },
      ]);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] min-h-[720px] flex-col gap-6 lg:grid lg:grid-cols-[340px_minmax(0,1fr)]">
      <aside className="flex min-h-0 flex-col gap-4">
        <header className="space-y-2">
          <p className="inline-flex rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-800">管家对话</p>
          <h2 className="text-3xl font-semibold tracking-tight text-slate-950">总控入口</h2>
          <p className="text-sm text-slate-600">左侧查看绑定内容和最近会话，右侧完成聊天操作。</p>
        </header>

        <div className="flex min-h-0 flex-1 flex-col gap-4">
          <CardSection
            title="绑定的 Agent"
            emptyText="暂未绑定 Agent"
            onScroll={(event) => loadMoreOnScroll(event, visibleAgentCount, boundAgents.length, setVisibleAgentCount)}
          >
            {visibleBoundAgents.length ? (
              <div className="space-y-2">
                {visibleBoundAgents.map((item) => (
                  <div key={item.id} className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-3 text-sm">
                    <p className="truncate font-medium text-slate-900">{item.name}</p>
                    <p className="mt-1 truncate text-xs text-slate-500">{item.code}</p>
                    <p className="mt-1 line-clamp-2 text-xs text-slate-600">{item.description || "暂无描述"}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500">暂未绑定 Agent</p>
            )}
          </CardSection>

          <CardSection title="绑定的 Skills / Tools" emptyText="暂无绑定内容">
            <div className="space-y-3">
              <div>
                <p className="text-xs uppercase tracking-wide text-slate-500">Skills</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {boundSkills.length ? (
                    boundSkills.map((item) => (
                      <span key={item.id} className="max-w-full truncate rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-700">
                        {item.name}
                      </span>
                    ))
                  ) : (
                    <p className="text-sm text-slate-500">无</p>
                  )}
                </div>
              </div>
              <div>
                <p className="text-xs uppercase tracking-wide text-slate-500">Tools</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {boundTools.length ? (
                    boundTools.map((item) => (
                      <span key={item.id} className="max-w-full truncate rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-700">
                        {item.name}
                      </span>
                    ))
                  ) : (
                    <p className="text-sm text-slate-500">无</p>
                  )}
                </div>
              </div>
            </div>
          </CardSection>

          <CardSection
            title="历史聊天记录"
            emptyText="暂无历史聊天记录"
            onScroll={(event) => loadMoreOnScroll(event, visibleHistoryCount, conversations.length, setVisibleHistoryCount)}
          >
            {visibleConversations.length ? (
              <div className="space-y-2">
                {visibleConversations.map((item) => (
                  <div key={item.id} className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm">
                    <p className="truncate font-medium text-slate-900">{item.title}</p>
                    <p className="mt-1 truncate text-xs text-slate-500">
                      目标 ID: {item.target_id} · 更新时间 {new Date(item.updated_at).toLocaleString("zh-CN")}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500">暂无历史聊天记录</p>
            )}
          </CardSection>
        </div>
      </aside>

      <section className="flex min-h-0 flex-col rounded-3xl border border-slate-200 bg-gradient-to-b from-slate-50 to-white p-5 shadow-sm">
        <div ref={messageViewportRef} className="min-h-0 flex-1 space-y-3 overflow-y-auto pr-1">
          {messages.map((item) => (
            <div key={item.id} className={item.role === "assistant" ? "flex justify-start" : "flex justify-end"}>
              <div
                className={
                  item.role === "assistant"
                    ? "max-w-[80%] whitespace-pre-wrap rounded-2xl bg-slate-100 px-4 py-3 text-sm text-slate-900"
                    : "max-w-[80%] whitespace-pre-wrap rounded-2xl bg-slate-900 px-4 py-3 text-sm text-white"
                }
              >
                {item.content}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 shrink-0 rounded-2xl border border-slate-200 bg-white/95 p-3 shadow-sm">
          <textarea
            ref={textareaRef}
            value={content}
            onChange={(event) => {
              setContent(event.target.value);
              resizeTextarea(event.target);
            }}
            placeholder="向管家输入任务..."
            className="min-h-[44px] max-h-56 w-full resize-none overflow-y-auto rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm leading-5 outline-none ring-indigo-200 transition focus:ring"
          />

          <div className="mt-3 flex items-center justify-between gap-3">
            <div className="relative">
              <button
                type="button"
                onClick={() => setShowPlusMenu((prev) => !prev)}
                className="flex h-10 w-10 items-center justify-center rounded-full border border-slate-300 bg-white text-xl text-slate-700 hover:bg-slate-100"
              >
                +
              </button>
              {showPlusMenu ? (
                <div className="absolute bottom-12 left-0 z-20 w-44 rounded-xl border border-slate-200 bg-white p-2 shadow-lg">
                  <button
                    type="button"
                    onClick={() => {
                      setShowAgentPicker(true);
                      setShowSkillPicker(false);
                      setShowToolPicker(false);
                      setShowPlusMenu(false);
                    }}
                    className="w-full rounded-lg px-3 py-2 text-left text-sm text-slate-700 hover:bg-slate-100"
                  >
                    添加 Agent
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowSkillPicker(true);
                      setShowAgentPicker(false);
                      setShowToolPicker(false);
                      setShowPlusMenu(false);
                    }}
                    className="w-full rounded-lg px-3 py-2 text-left text-sm text-slate-700 hover:bg-slate-100"
                  >
                    添加 Skills
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowToolPicker(true);
                      setShowAgentPicker(false);
                      setShowSkillPicker(false);
                      setShowPlusMenu(false);
                    }}
                    className="w-full rounded-lg px-3 py-2 text-left text-sm text-slate-700 hover:bg-slate-100"
                  >
                    添加 Tools
                  </button>
                </div>
              ) : null}
            </div>

            <button
              type="button"
              onClick={send}
              disabled={isSending}
              className="h-12 rounded-xl bg-slate-900 px-5 text-sm font-medium text-white hover:bg-slate-800"
            >
              {isSending ? "执行中..." : "发送"}
            </button>
          </div>

          {showAgentPicker ? (
            <div className="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-3">
              <p className="mb-2 text-sm font-medium text-slate-800">绑定 Agent</p>
              <div className="grid max-h-52 gap-2 overflow-y-auto md:grid-cols-2">
                {agents.map((item) => (
                  <label key={item.id} className="flex items-center gap-2 rounded-lg bg-white px-3 py-2 text-sm">
                    <input type="checkbox" checked={boundAgentIds.includes(item.id)} onChange={() => toggleNumber(boundAgentIds, item.id, setBoundAgentIds)} />
                    <span className="truncate">{item.name} ({item.code})</span>
                  </label>
                ))}
              </div>
            </div>
          ) : null}

          {showSkillPicker ? (
            <div className="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-3">
              <p className="mb-2 text-sm font-medium text-slate-800">绑定 Skills</p>
              <div className="grid max-h-52 gap-2 overflow-y-auto md:grid-cols-2">
                {skills.map((item) => (
                  <label key={item.id} className="flex items-center gap-2 rounded-lg bg-white px-3 py-2 text-sm">
                    <input type="checkbox" checked={boundSkillIds.includes(item.id)} onChange={() => toggleNumber(boundSkillIds, item.id, setBoundSkillIds)} />
                    <span className="truncate">{item.name} ({item.code})</span>
                  </label>
                ))}
              </div>
            </div>
          ) : null}

          {showToolPicker ? (
            <div className="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-3">
              <p className="mb-2 text-sm font-medium text-slate-800">绑定 Tools</p>
              <div className="grid max-h-52 gap-2 overflow-y-auto md:grid-cols-2">
                {tools.map((item) => (
                  <label key={item.id} className="flex items-center gap-2 rounded-lg bg-white px-3 py-2 text-sm">
                    <input type="checkbox" checked={boundToolIds.includes(item.id)} onChange={() => toggleNumber(boundToolIds, item.id, setBoundToolIds)} />
                    <span className="truncate">{item.name} ({item.code})</span>
                  </label>
                ))}
              </div>
            </div>
          ) : null}
        </div>
      </section>
    </div>
  );
}
