"use client";

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { defaultAgents, defaultSkills } from "@/lib/default-data";
import type {
  AgentRecord,
  ChatMessage,
  ChatScope,
  ChatThread,
  SkillRecord,
} from "@/lib/types";

type StewardStore = {
  agents: AgentRecord[];
  skills: SkillRecord[];
  upsertAgent: (agent: AgentRecord) => void;
  deleteAgent: (id: string) => void;
  toggleAgentEnabled: (id: string, enabled: boolean) => void;
  toggleAgentPermission: (id: string, enabled: boolean) => void;
  upsertSkill: (skill: SkillRecord) => void;
  deleteSkill: (id: string) => void;
  toggleSkillEnabled: (id: string, enabled: boolean) => void;
  toggleSkillPermission: (id: string, enabled: boolean) => void;
  listThreads: (scope: ChatScope, agentId?: string | null) => ChatThread[];
  getThreadById: (threadId: string) => ChatThread | undefined;
  getThreadMessages: (threadId: string) => ChatMessage[];
  createThread: (input: {
    scope: ChatScope;
    agentId?: string | null;
    firstUserMessage: string;
    assistantReply: string;
  }) => string;
  appendMessage: (input: {
    threadId: string;
    role: "user" | "assistant";
    content: string;
  }) => void;
};

const STORAGE_KEY = "steward-web-state-v1";

const StewardContext = createContext<StewardStore | null>(null);

function nowText() {
  return new Date().toLocaleString("zh-CN", {
    hour12: false,
  });
}

function nowIso() {
  return new Date().toISOString();
}

function buildTitle(text: string) {
  const normalized = text.trim().replace(/\s+/g, " ");
  if (normalized.length <= 32) {
    return normalized;
  }
  return `${normalized.slice(0, 32)}...`;
}

export function StewardProvider({ children }: { children: ReactNode }) {
  const [agents, setAgents] = useState<AgentRecord[]>(defaultAgents);
  const [skills, setSkills] = useState<SkillRecord[]>(defaultSkills);
  const [chatThreads, setChatThreads] = useState<ChatThread[]>([]);
  const [chatMessagesByThread, setChatMessagesByThread] = useState<
    Record<string, ChatMessage[]>
  >({});
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as {
        agents?: AgentRecord[];
        skills?: SkillRecord[];
        chatThreads?: ChatThread[];
        chatMessagesByThread?: Record<string, ChatMessage[]>;
      };
      if (parsed.agents) {
        setAgents(parsed.agents);
      }
      if (parsed.skills) {
        setSkills(parsed.skills);
      }
      if (parsed.chatThreads) {
        setChatThreads(parsed.chatThreads);
      }
      if (parsed.chatMessagesByThread) {
        setChatMessagesByThread(parsed.chatMessagesByThread);
      }
    }
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ agents, skills, chatThreads, chatMessagesByThread }),
    );
  }, [agents, skills, chatThreads, chatMessagesByThread, hydrated]);

  const value = useMemo<StewardStore>(
    () => ({
      agents,
      skills,
      upsertAgent: (agent) => {
        setAgents((prev) => {
          const next = [...prev];
          const idx = next.findIndex((item) => item.id === agent.id);
          const withTime = { ...agent, updatedAt: nowText() };
          if (idx >= 0) {
            next[idx] = withTime;
          } else {
            next.unshift(withTime);
          }
          return next;
        });
      },
      deleteAgent: (id) => {
        setAgents((prev) => prev.filter((item) => item.id !== id));
      },
      toggleAgentEnabled: (id, enabled) => {
        setAgents((prev) =>
          prev.map((item) =>
            item.id === id ? { ...item, enabled, updatedAt: nowText() } : item,
          ),
        );
      },
      toggleAgentPermission: (id, enabled) => {
        setAgents((prev) =>
          prev.map((item) =>
            item.id === id
              ? { ...item, permissionEnabled: enabled, updatedAt: nowText() }
              : item,
          ),
        );
      },
      upsertSkill: (skill) => {
        setSkills((prev) => {
          const next = [...prev];
          const idx = next.findIndex((item) => item.id === skill.id);
          const withTime = { ...skill, updatedAt: nowText() };
          if (idx >= 0) {
            next[idx] = withTime;
          } else {
            next.unshift(withTime);
          }
          return next;
        });
      },
      deleteSkill: (id) => {
        setSkills((prev) => prev.filter((item) => item.id !== id));
      },
      toggleSkillEnabled: (id, enabled) => {
        setSkills((prev) =>
          prev.map((item) =>
            item.id === id ? { ...item, enabled, updatedAt: nowText() } : item,
          ),
        );
      },
      toggleSkillPermission: (id, enabled) => {
        setSkills((prev) =>
          prev.map((item) =>
            item.id === id
              ? { ...item, permissionEnabled: enabled, updatedAt: nowText() }
              : item,
          ),
        );
      },
      listThreads: (scope, agentId = null) =>
        chatThreads
          .filter((item) =>
            item.scope === scope
            && (scope === "butler" ? item.agentId === null : item.agentId === (agentId ?? null)),
          )
          .sort((a, b) => (a.updatedAt < b.updatedAt ? 1 : -1)),
      getThreadById: (threadId) => chatThreads.find((item) => item.id === threadId),
      getThreadMessages: (threadId) => chatMessagesByThread[threadId] ?? [],
      createThread: ({ scope, agentId = null, firstUserMessage, assistantReply }) => {
        const now = nowIso();
        const threadId = `thread-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
        const userMessage: ChatMessage = {
          id: `m-${Date.now()}-u`,
          role: "user",
          content: firstUserMessage.trim(),
          createdAt: now,
        };
        const assistantMessage: ChatMessage = {
          id: `m-${Date.now()}-a`,
          role: "assistant",
          content: assistantReply,
          createdAt: now,
        };
        const thread: ChatThread = {
          id: threadId,
          scope,
          agentId: scope === "butler" ? null : agentId,
          title: buildTitle(firstUserMessage),
          createdAt: now,
          updatedAt: now,
          messageCount: 2,
          lastMessagePreview: assistantReply.slice(0, 80),
        };
        setChatThreads((prev) => [thread, ...prev]);
        setChatMessagesByThread((prev) => ({
          ...prev,
          [threadId]: [userMessage, assistantMessage],
        }));
        return threadId;
      },
      appendMessage: ({ threadId, role, content }) => {
        const text = content.trim();
        if (!text) return;
        const now = nowIso();
        const message: ChatMessage = {
          id: `m-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
          role,
          content: text,
          createdAt: now,
        };
        setChatMessagesByThread((prev) => {
          const current = prev[threadId] ?? [];
          return {
            ...prev,
            [threadId]: [...current, message],
          };
        });
        setChatThreads((prev) =>
          prev.map((item) =>
            item.id === threadId
              ? {
                  ...item,
                  updatedAt: now,
                  messageCount: item.messageCount + 1,
                  lastMessagePreview: text.slice(0, 80),
                }
              : item,
          ),
        );
      },
    }),
    [agents, skills, chatThreads, chatMessagesByThread],
  );

  return (
    <StewardContext.Provider value={value}>{children}</StewardContext.Provider>
  );
}

export function useStewardStore() {
  const ctx = useContext(StewardContext);
  if (!ctx) {
    throw new Error("useStewardStore must be used inside StewardProvider");
  }
  return ctx;
}
