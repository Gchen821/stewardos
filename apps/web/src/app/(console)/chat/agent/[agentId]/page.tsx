import Link from "next/link";

export default function AgentChatPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold text-slate-900">Agent 会话入口已收敛</h2>
      <p className="text-sm text-slate-600">当前前端统一使用 `/chat` 创建和管理会话，不再维护独立的 Agent 子聊天页面。</p>
      <Link href="/chat" className="text-sm font-medium text-teal-700">返回对话页</Link>
    </div>
  );
}
