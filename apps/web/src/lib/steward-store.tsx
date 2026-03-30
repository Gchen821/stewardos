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
  RepositoryConfig,
  RuntimeTokenUsage,
  SkillRecord,
} from "@/lib/types";

type StewardStore = {
  agents: AgentRecord[];
  skills: SkillRecord[];
  repositoryConfig: RepositoryConfig;
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
    assistantReply?: string;
  }) => string;
  appendMessage: (input: {
    threadId: string;
    role: "user" | "assistant";
    content: string;
  }) => void;
  runtimeTokenUsage: RuntimeTokenUsage;
  recordRuntimeTokenUsage: (input: {
    model: string;
    promptTokens?: number;
    completionTokens?: number;
    totalTokens?: number;
  }) => void;
  resetRuntimeTokenUsage: () => void;
  updateRepositoryConfig: (next: Partial<RepositoryConfig>) => void;
  resetRepositoryConfig: () => void;
};

const STORAGE_KEY = "steward-web-state-v1";
const THREAD_MESSAGES_KEY_PREFIX = "steward-thread-messages-v1:";
const DEFAULT_REPOSITORY_CONFIG: RepositoryConfig = {
  rootPath: "/workspace/repositories",
  agentsDir: "agents",
  skillsDir: "skills",
  toolsDir: "tools",
  autoBootstrap: true,
};

const DEFAULT_RUNTIME_TOKEN_USAGE: RuntimeTokenUsage = {
  promptTokens: 0,
  completionTokens: 0,
  totalTokens: 0,
  updatedAt: null,
  byModel: {},
};

const StewardContext = createContext<StewardStore | null>(null);

function isBrowser() {
  return typeof window !== "undefined";
}

function threadMessagesStorageKey(threadId: string) {
  return `${THREAD_MESSAGES_KEY_PREFIX}${threadId}`;
}

function readThreadMessages(threadId: string): ChatMessage[] {
  if (!isBrowser()) return [];
  const raw = localStorage.getItem(threadMessagesStorageKey(threadId));
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw) as ChatMessage[];
    if (!Array.isArray(parsed)) return [];
    return parsed;
  } catch {
    return [];
  }
}

function writeThreadMessages(threadId: string, messages: ChatMessage[]) {
  if (!isBrowser()) return;
  localStorage.setItem(threadMessagesStorageKey(threadId), JSON.stringify(messages));
}

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
  const [repositoryConfig, setRepositoryConfig] = useState<RepositoryConfig>(
    DEFAULT_REPOSITORY_CONFIG,
  );
  const [chatThreads, setChatThreads] = useState<ChatThread[]>([]);
  const [chatMessagesByThread, setChatMessagesByThread] = useState<
    Record<string, ChatMessage[]>
  >({});
  const [runtimeTokenUsage, setRuntimeTokenUsage] = useState<RuntimeTokenUsage>(
    DEFAULT_RUNTIME_TOKEN_USAGE,
  );
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as {
        agents?: AgentRecord[];
        skills?: SkillRecord[];
        repositoryConfig?: RepositoryConfig;
        chatThreads?: ChatThread[];
        chatMessagesByThread?: Record<string, ChatMessage[]>;
        runtimeTokenUsage?: RuntimeTokenUsage;
      };
      if (parsed.agents) {
        setAgents(parsed.agents);
      }
      if (parsed.skills) {
        setSkills(parsed.skills);
      }
      if (parsed.repositoryConfig) {
        setRepositoryConfig({
          ...DEFAULT_REPOSITORY_CONFIG,
          ...parsed.repositoryConfig,
        });
      }
      if (parsed.chatThreads) {
        setChatThreads(parsed.chatThreads);
      }
      if (parsed.chatMessagesByThread) {
        for (const [threadId, messages] of Object.entries(parsed.chatMessagesByThread)) {
          if (Array.isArray(messages) && messages.length > 0) {
            writeThreadMessages(threadId, messages);
          }
        }
      }
      if (parsed.runtimeTokenUsage) {
        setRuntimeTokenUsage(parsed.runtimeTokenUsage);
      }
    }
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    localStorage.setItem(
      STORAGE_KEY,
        JSON.stringify({
          agents,
          skills,
          repositoryConfig,
          chatThreads,
          runtimeTokenUsage,
        }),
    );
  }, [
    agents,
    skills,
    repositoryConfig,
    chatThreads,
    runtimeTokenUsage,
    hydrated,
  ]);

  const value = useMemo<StewardStore>(
    () => ({
      agents,
      skills,
      repositoryConfig,
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
      getThreadMessages: (threadId) => chatMessagesByThread[threadId] ?? readThreadMessages(threadId),
      createThread: ({ scope, agentId = null, firstUserMessage, assistantReply }) => {
        const now = nowIso();
        const threadId = `thread-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
        const userMessage: ChatMessage = {
          id: `m-${Date.now()}-u`,
          role: "user",
          content: firstUserMessage.trim(),
          createdAt: now,
        };
        const assistantText = (assistantReply ?? "").trim();
        const assistantMessage: ChatMessage | null = assistantText
          ? {
              id: `m-${Date.now()}-a`,
              role: "assistant",
              content: assistantText,
              createdAt: now,
            }
          : null;
        const thread: ChatThread = {
          id: threadId,
          scope,
          agentId: scope === "butler" ? null : agentId,
          title: buildTitle(firstUserMessage),
          createdAt: now,
          updatedAt: now,
          messageCount: assistantMessage ? 2 : 1,
          lastMessagePreview: (assistantMessage ? assistantText : firstUserMessage).slice(0, 80),
        };
        setChatThreads((prev) => [thread, ...prev]);
        const initialMessages = assistantMessage ? [userMessage, assistantMessage] : [userMessage];
        writeThreadMessages(threadId, initialMessages);
        setChatMessagesByThread((prev) => ({
          ...prev,
          [threadId]: initialMessages,
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
          const current = prev[threadId] ?? readThreadMessages(threadId);
          const nextMessages = [...current, message];
          writeThreadMessages(threadId, nextMessages);
          return {
            ...prev,
            [threadId]: nextMessages,
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
      runtimeTokenUsage,
      recordRuntimeTokenUsage: ({
        model,
        promptTokens = 0,
        completionTokens = 0,
        totalTokens,
      }) => {
        const normalizedTotal = totalTokens ?? promptTokens + completionTokens;
        setRuntimeTokenUsage((prev) => {
          const currentByModel = prev.byModel[model] ?? {
            promptTokens: 0,
            completionTokens: 0,
            totalTokens: 0,
          };
          const nextByModel = {
            ...prev.byModel,
            [model]: {
              promptTokens: currentByModel.promptTokens + promptTokens,
              completionTokens: currentByModel.completionTokens + completionTokens,
              totalTokens: currentByModel.totalTokens + normalizedTotal,
            },
          };
          return {
            promptTokens: prev.promptTokens + promptTokens,
            completionTokens: prev.completionTokens + completionTokens,
            totalTokens: prev.totalTokens + normalizedTotal,
            updatedAt: nowIso(),
            byModel: nextByModel,
          };
        });
      },
      resetRuntimeTokenUsage: () => {
        setRuntimeTokenUsage(DEFAULT_RUNTIME_TOKEN_USAGE);
      },
      updateRepositoryConfig: (next) => {
        setRepositoryConfig((prev) => ({
          ...prev,
          ...next,
        }));
      },
      resetRepositoryConfig: () => {
        setRepositoryConfig(DEFAULT_REPOSITORY_CONFIG);
      },
    }),
    [
      agents,
      skills,
      repositoryConfig,
      chatThreads,
      chatMessagesByThread,
      runtimeTokenUsage,
    ],
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
