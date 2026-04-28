export const API_ROUTES = {
  health: "/api/v1/health",
  runtimeInfo: "/api/v1/runtime/info",
  runtimeLlmSettings: "/api/v1/runtime/llm-settings",
  runtimeRepositorySettings: "/api/v1/runtime/repository-settings",
  runtimeRepositoryDirectories: "/api/v1/runtime/repository-directories",
  login: "/api/v1/auth/login",
  me: "/api/v1/users/me",
  users: "/api/v1/users",
  agents: "/api/v1/agents",
  skills: "/api/v1/skills",
  tools: "/api/v1/tools",
  conversations: "/api/v1/conversations",
  chatSend: "/api/v1/chat/send",
} as const;

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "").replace(/\/$/, "");
const TOKEN_KEY = "stewardos-access-token";

function buildApiUrl(path: string) {
  return `${API_BASE_URL}${path}`;
}

function getHeaders() {
  const headers: HeadersInit = { "Content-Type": "application/json" };
  if (typeof window !== "undefined") {
    const token = window.localStorage.getItem(TOKEN_KEY);
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
  }
  return headers;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(buildApiUrl(path), {
    ...init,
    headers: {
      ...getHeaders(),
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export function getApiBaseUrl() {
  return API_BASE_URL;
}

export function getStoredToken() {
  if (typeof window === "undefined") {
    return null;
  }
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token: string) {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearStoredToken() {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.removeItem(TOKEN_KEY);
}

export type User = {
  id: string;
  username: string;
  status: string;
  created_at: string;
  updated_at: string;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

export type Agent = {
  id: number;
  owner_user_id: string;
  code: string;
  name: string;
  description: string;
  type: string;
  runtime_status: string;
  file_path: string;
  manifest_version: string;
  enabled: boolean;
  chat_selectable: boolean;
  is_builtin: boolean;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
};

export type Skill = {
  id: number;
  owner_user_id: string;
  code: string;
  name: string;
  description: string;
  category: string;
  file_path: string;
  manifest_version: string;
  enabled: boolean;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
};

export type Tool = {
  id: number;
  owner_user_id: string;
  code: string;
  name: string;
  description: string;
  category: string;
  file_path: string;
  manifest_version: string;
  risk_level: string;
  enabled: boolean;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
};

export type Conversation = {
  id: number;
  user_id: string;
  target_type: string;
  target_id: number;
  title: string;
  created_at: string;
  updated_at: string;
};

export type ChatMessage = {
  id: number;
  conversation_id: number;
  sender_role: string;
  sender_id: string | null;
  content: string;
  message_type: string;
  metadata_json: Record<string, unknown>;
  created_at: string;
};

export type RuntimeInfo = {
  mode: string;
  llm: {
    provider: string;
    model: string;
    fallback_model?: string | null;
    base_url?: string | null;
    timeout_seconds: number;
  };
  auth: {
    default_admin: string;
    default_password: string;
  };
};

export type LLMSettings = {
  provider: string;
  model: string;
  fallback_model?: string | null;
  base_url?: string | null;
  api_key?: string | null;
  timeout_seconds: number;
  api_key_env_name: string;
  api_key_configured: boolean;
  records: Record<
    string,
    {
      provider: string;
      model: string;
      fallback_model?: string | null;
      base_url?: string | null;
      api_key?: string | null;
      timeout_seconds: number;
      updated_at?: string | null;
    }
  >;
  runtime: RuntimeInfo["llm"];
};

export type RepositorySettings = {
  repository_root_path: string;
  resolved_repository_root: string;
  resolved_users_root: string;
  resolved_current_user_root: string;
  resolved_current_user_config_dir: string;
};

export type RepositoryDirectoryBrowse = {
  current_path: string;
  parent_path?: string | null;
  directories: Array<{
    name: string;
    path: string;
  }>;
};

export type ChatSendResponse = {
  conversation_id: number;
  reply: string;
  job_run_id: number;
  selected_model: string;
  metadata: Record<string, unknown>;
};

export async function login(username: string, password: string): Promise<LoginResponse> {
  const data = await request<LoginResponse>(API_ROUTES.login, {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  setStoredToken(data.access_token);
  return data;
}

export async function register(username: string, password: string): Promise<User> {
  return request<User>(API_ROUTES.users, {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

export async function fetchMe(): Promise<User> {
  return request<User>(API_ROUTES.me, { method: "GET" });
}

export async function fetchRuntimeInfo(): Promise<RuntimeInfo> {
  return request<RuntimeInfo>(API_ROUTES.runtimeInfo, { method: "GET" });
}

export async function fetchLLMSettings(): Promise<LLMSettings> {
  return request<LLMSettings>(API_ROUTES.runtimeLlmSettings, { method: "GET" });
}

export async function updateLLMSettings(payload: {
  provider: string;
  model: string;
  fallback_model?: string | null;
  base_url?: string | null;
  timeout_seconds: number;
  api_key?: string;
}): Promise<LLMSettings> {
  return request<LLMSettings>(API_ROUTES.runtimeLlmSettings, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function fetchRepositorySettings(): Promise<RepositorySettings> {
  return request<RepositorySettings>(API_ROUTES.runtimeRepositorySettings, { method: "GET" });
}

export async function updateRepositorySettings(payload: {
  repository_root_path: string;
}): Promise<RepositorySettings> {
  return request<RepositorySettings>(API_ROUTES.runtimeRepositorySettings, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function browseRepositoryDirectories(path?: string): Promise<RepositoryDirectoryBrowse> {
  const query = path ? `?path=${encodeURIComponent(path)}` : "";
  return request<RepositoryDirectoryBrowse>(`${API_ROUTES.runtimeRepositoryDirectories}${query}`, { method: "GET" });
}

export async function fetchAgents(): Promise<Agent[]> {
  return request<Agent[]>(API_ROUTES.agents, { method: "GET" });
}

export async function createAgent(payload: {
  code: string;
  name: string;
  description?: string;
  type?: string;
  runtime_status?: string;
  manifest_version?: string;
  chat_selectable?: boolean;
}): Promise<Agent> {
  return request<Agent>(API_ROUTES.agents, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateAgent(agentId: number, payload: Record<string, unknown>): Promise<Agent> {
  return request<Agent>(`${API_ROUTES.agents}/${agentId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function deleteAgent(agentId: number): Promise<void> {
  await request<{ message: string }>(`${API_ROUTES.agents}/${agentId}`, { method: "DELETE" });
}

export async function toggleAgent(agentId: number, enabled: boolean): Promise<void> {
  await request(`${API_ROUTES.agents}/${agentId}/${enabled ? "enable" : "disable"}`, {
    method: "POST",
  });
}

export async function fetchSkills(): Promise<Skill[]> {
  return request<Skill[]>(API_ROUTES.skills, { method: "GET" });
}

export async function createSkill(payload: {
  code: string;
  name: string;
  description?: string;
  category?: string;
  manifest_version?: string;
}): Promise<Skill> {
  return request<Skill>(API_ROUTES.skills, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateSkill(skillId: number, payload: Record<string, unknown>): Promise<Skill> {
  return request<Skill>(`${API_ROUTES.skills}/${skillId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function deleteSkill(skillId: number): Promise<void> {
  await request<{ message: string }>(`${API_ROUTES.skills}/${skillId}`, { method: "DELETE" });
}

export async function toggleSkill(skillId: number, enabled: boolean): Promise<void> {
  await request(`${API_ROUTES.skills}/${skillId}/${enabled ? "enable" : "disable"}`, {
    method: "POST",
  });
}

export async function fetchTools(): Promise<Tool[]> {
  return request<Tool[]>(API_ROUTES.tools, { method: "GET" });
}

export async function createTool(payload: {
  code: string;
  name: string;
  description?: string;
  category?: string;
  manifest_version?: string;
  risk_level?: string;
}): Promise<Tool> {
  return request<Tool>(API_ROUTES.tools, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateTool(toolId: number, payload: Record<string, unknown>): Promise<Tool> {
  return request<Tool>(`${API_ROUTES.tools}/${toolId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function deleteTool(toolId: number): Promise<void> {
  await request<{ message: string }>(`${API_ROUTES.tools}/${toolId}`, { method: "DELETE" });
}

export async function toggleTool(toolId: number, enabled: boolean): Promise<void> {
  await request(`${API_ROUTES.tools}/${toolId}/${enabled ? "enable" : "disable"}`, {
    method: "POST",
  });
}

export async function fetchConversations(): Promise<Conversation[]> {
  return request<Conversation[]>(API_ROUTES.conversations, { method: "GET" });
}

export async function createConversation(payload: {
  target_type: string;
  target_id: number;
  title: string;
}): Promise<Conversation> {
  return request<Conversation>(API_ROUTES.conversations, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function fetchMessages(conversationId: number): Promise<ChatMessage[]> {
  return request<ChatMessage[]>(`${API_ROUTES.conversations}/${conversationId}/messages`, {
    method: "GET",
  });
}

export async function sendChat(payload: {
  conversation_id?: number | null;
  target_type: string;
  target_id: number;
  content: string;
  bound_agent_ids?: number[];
  bound_skill_ids?: number[];
  bound_tool_ids?: number[];
}): Promise<ChatSendResponse> {
  return request<ChatSendResponse>(API_ROUTES.chatSend, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
