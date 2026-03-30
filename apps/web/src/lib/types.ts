export type AgentStatus = "online" | "offline" | "draft";

export type AgentRecord = {
  id: string;
  name: string;
  description: string;
  avatar: string;
  status: AgentStatus;
  enabled: boolean;
  permissionEnabled: boolean;
  updatedAt: string;
};

export type SkillRecord = {
  id: string;
  name: string;
  description: string;
  category: string;
  enabled: boolean;
  permissionEnabled: boolean;
  updatedAt: string;
};

export type RepositoryConfig = {
  rootPath: string;
  agentsDir: string;
  skillsDir: string;
  toolsDir: string;
  autoBootstrap: boolean;
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: string;
};

export type ChatScope = "butler" | "agent";

export type ChatThread = {
  id: string;
  scope: ChatScope;
  agentId: string | null;
  title: string;
  createdAt: string;
  updatedAt: string;
  messageCount: number;
  lastMessagePreview: string;
};

export type RuntimeTokenUsage = {
  promptTokens: number;
  completionTokens: number;
  totalTokens: number;
  updatedAt: string | null;
  byModel: Record<
    string,
    {
      promptTokens: number;
      completionTokens: number;
      totalTokens: number;
    }
  >;
};
