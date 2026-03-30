export const API_ROUTES = {
  chatSend: "/api/v1/chat/send",
  chatStream: "/api/v1/chat/stream",
  conversations: "/api/v1/conversations",
  agents: "/api/v1/agents",
  skills: "/api/v1/skills",
  modelsRuntime: "/api/v1/models/runtime",
  modelProviders: "/api/v1/model/providers",
  permissions: "/api/v1/permissions/me",
} as const;

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "").replace(/\/$/, "");

function buildApiUrl(path: string) {
  return `${API_BASE_URL}${path}`;
}

export function getApiBaseUrl() {
  return API_BASE_URL;
}

export type ChatStreamDoneEvent = {
  type: "done";
  selected_model?: string;
  metadata?: {
    agent?: {
      usage?: {
        prompt_tokens?: number;
        completion_tokens?: number;
        total_tokens?: number;
      };
      selected_model?: string;
    };
  };
};

type ChatStreamEvent =
  | { type: "start"; selected_model?: string; conversation_id?: string }
  | { type: "delta"; delta?: string }
  | ChatStreamDoneEvent
  | { type: "error"; message?: string };

type StreamButlerChatInput = {
  conversationId: string;
  content: string;
  signal?: AbortSignal;
  onStart?: (event: { selectedModel: string }) => void;
  onDelta?: (delta: string) => void;
  onDone?: (event: ChatStreamDoneEvent) => void;
  onError?: (message: string) => void;
};

function parseSsePayload(payload: string): ChatStreamEvent | null {
  try {
    return JSON.parse(payload) as ChatStreamEvent;
  } catch {
    return null;
  }
}

export async function streamButlerChat(input: StreamButlerChatInput) {
  const response = await fetch(buildApiUrl(API_ROUTES.chatStream), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      conversation_id: input.conversationId,
      target_type: "butler",
      target_id: null,
      content: input.content,
    }),
    signal: input.signal,
  });

  if (!response.ok || !response.body) {
    const message = `请求失败 (${response.status})`;
    input.onError?.(message);
    throw new Error(message);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  try {
    while (true) {
      if (input.signal?.aborted) {
        throw new DOMException("The operation was aborted.", "AbortError");
      }
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const chunks = buffer.split("\n\n");
      buffer = chunks.pop() ?? "";

      for (const chunk of chunks) {
        const lines = chunk.split("\n");
        for (const line of lines) {
          if (!line.startsWith("data:")) continue;
          const data = line.slice(5).trim();
          if (!data) continue;
          const event = parseSsePayload(data);
          if (!event) continue;

          if (event.type === "start") {
            input.onStart?.({ selectedModel: event.selected_model ?? "unknown" });
          } else if (event.type === "delta") {
            input.onDelta?.(event.delta ?? "");
          } else if (event.type === "done") {
            input.onDone?.(event);
          } else if (event.type === "error") {
            input.onError?.(event.message ?? "流式响应错误");
          }
        }
      }
    }
  } finally {
    try {
      await reader.cancel();
    } catch {
      // ignore reader cancel errors
    }
  }
}

export const apiPlanNote =
  "已支持对接后端流式会话。配置 NEXT_PUBLIC_API_BASE_URL 后可直接使用真实聊天与 token 统计。";

export type ModelRuntimeConfig = {
  current_model: string;
  fallback_model: string | null;
  has_fallback: boolean;
};

export async function fetchModelRuntimeConfig(): Promise<ModelRuntimeConfig> {
  const response = await fetch(buildApiUrl(API_ROUTES.modelsRuntime), {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });
  if (!response.ok) {
    throw new Error(`获取模型配置失败 (${response.status})`);
  }
  return response.json() as Promise<ModelRuntimeConfig>;
}
