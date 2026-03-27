export const API_ROUTES = {
  chatSend: "/api/v1/chat/send",
  conversations: "/api/v1/conversations",
  agents: "/api/v1/agents",
  skills: "/api/v1/skills",
  modelProviders: "/api/v1/model/providers",
  permissions: "/api/v1/permissions/me",
} as const;

export const apiPlanNote =
  "This UI currently uses local mock state. API wiring is reserved for the next implementation plan.";
