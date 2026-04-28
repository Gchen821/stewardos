import Link from "next/link";

export default function AgentSessionPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold text-slate-900">独立 Agent Session 已下线</h2>
      <p className="text-sm text-slate-600">请统一从 `/chat` 进入单 Agent Runtime 会话。</p>
      <Link href="/chat" className="text-sm font-medium text-teal-700">返回对话页</Link>
    </div>
  );
}
