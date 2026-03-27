import type { AgentRecord, SkillRecord } from "@/lib/types";

export const defaultAgents: AgentRecord[] = [
  {
    id: "planner-agent",
    name: "行程规划 Agent",
    description: "负责拆解需求并生成多天行动计划与时间轴。",
    avatar: "/globe.svg",
    status: "online",
    enabled: true,
    permissionEnabled: true,
    updatedAt: "2026-03-27 10:10",
  },
  {
    id: "research-agent",
    name: "研究检索 Agent",
    description: "负责检索资料、提炼证据并给出引用建议。",
    avatar: "/file.svg",
    status: "online",
    enabled: true,
    permissionEnabled: true,
    updatedAt: "2026-03-27 10:20",
  },
  {
    id: "ops-agent",
    name: "运维执行 Agent",
    description: "负责执行低风险系统操作，默认需要策略确认。",
    avatar: "/window.svg",
    status: "offline",
    enabled: false,
    permissionEnabled: false,
    updatedAt: "2026-03-27 09:58",
  },
];

export const defaultSkills: SkillRecord[] = [
  {
    id: "skill-web-search",
    name: "Web Search",
    description: "联网检索公开信息并返回摘要。",
    category: "search",
    enabled: true,
    permissionEnabled: true,
    updatedAt: "2026-03-27 10:05",
  },
  {
    id: "skill-note",
    name: "Structured Note",
    description: "写入结构化笔记，供上下文工程阶段复用。",
    category: "memory",
    enabled: true,
    permissionEnabled: true,
    updatedAt: "2026-03-27 10:12",
  },
  {
    id: "skill-terminal",
    name: "Terminal",
    description: "执行命令行任务，默认高风险，需要审批。",
    category: "runtime",
    enabled: false,
    permissionEnabled: false,
    updatedAt: "2026-03-27 09:51",
  },
];
