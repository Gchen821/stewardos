"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { type ReactNode } from "react";

import { useStewardStore } from "@/lib/steward-store";

const repositoryItems = [
  { href: "/agents", label: "Agent 仓库" },
  { href: "/skills", label: "Skills 仓库" },
  { href: "/tools", label: "Tools 仓库" },
];

const userItems = [
  { href: "/settings", label: "账户设置" },
  { href: "/model-settings", label: "模型设置" },
  { href: "/system-settings", label: "系统设置" },
];

function clsx(...values: Array<string | false>) {
  return values.filter(Boolean).join(" ");
}

export function ConsoleShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const { listThreads } = useStewardStore();
  const conversationHistory = listThreads("butler");
  const menuItems = [{ href: "/chat", label: "主控对话" }, ...repositoryItems, ...userItems];

  return (
    <div className="min-h-screen bg-[linear-gradient(120deg,_#f8fafc_0%,_#e2e8f0_55%,_#dbeafe_100%)] text-slate-900">
      <div className="flex min-h-screen w-full">
        <aside className="hidden w-80 shrink-0 border-r border-slate-200 bg-white lg:flex lg:flex-col">
          <div className="border-b border-slate-200 px-5 py-5">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">StewardOS</p>
            <h1 className="mt-2 text-2xl font-semibold text-slate-950">控制台</h1>
          </div>

          <div className="border-b border-slate-200 px-4 py-4">
            <p className="px-2 text-xs uppercase tracking-[0.16em] text-slate-500">主控对话</p>
            <Link
              href="/chat"
              className={clsx(
                "mt-2 block rounded-xl px-3 py-2 text-sm font-medium transition",
                pathname === "/chat" || pathname.startsWith("/chat/")
                  ? "bg-slate-900 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200",
              )}
            >
              进入主控对话
            </Link>
            <div className="mt-4 space-y-1">
              {conversationHistory.length > 0 ? (
                conversationHistory.map((history) => (
                  <Link
                    key={history.id}
                    href={`/chat/session/${history.id}`}
                    className={clsx(
                      "block w-full rounded-lg px-3 py-2 text-left text-xs transition",
                      pathname === `/chat/session/${history.id}`
                        ? "bg-slate-900 text-white"
                        : pathname.startsWith("/chat")
                          ? "text-slate-700 hover:bg-slate-100"
                          : "text-slate-500",
                    )}
                  >
                    {history.title}
                  </Link>
                ))
              ) : (
                <p className="rounded-lg px-3 py-2 text-xs text-slate-400">暂无历史记录</p>
              )}
            </div>
          </div>

          <div className="px-4 py-4">
            <p className="px-2 text-xs uppercase tracking-[0.16em] text-slate-500">仓库设置</p>
            <nav className="mt-2 flex flex-col gap-1">
              {repositoryItems.map((item) => {
                const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={clsx(
                      "rounded-xl px-3 py-2 text-sm font-medium transition",
                      active
                        ? "bg-slate-900 text-white"
                        : "text-slate-700 hover:bg-slate-100",
                    )}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </div>

          <div className="mt-auto border-t border-slate-200 p-4">
            <details className="group">
              <summary className="flex cursor-pointer list-none items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-3 py-3 hover:bg-slate-100">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-indigo-100 font-semibold text-indigo-700">
                  U
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-900">User Admin</p>
                  <p className="text-xs text-slate-500">账号与系统菜单</p>
                </div>
              </summary>
              <div className="mt-2 space-y-1 rounded-xl border border-slate-200 bg-white p-2 text-sm">
                {userItems.map((item) => {
                  const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={clsx(
                        "block rounded-lg px-3 py-2 transition",
                        active
                          ? "bg-slate-900 text-white"
                          : "text-slate-700 hover:bg-slate-100",
                      )}
                    >
                      {item.label}
                    </Link>
                  );
                })}
              </div>
            </details>
          </div>
        </aside>

        <main className="min-w-0 flex-1 px-2 py-2 sm:px-4 sm:py-4">
          <nav className="mb-4 flex gap-2 overflow-auto pb-2 lg:hidden">
            {menuItems.map((item) => {
              const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={clsx(
                    "whitespace-nowrap rounded-full px-3 py-1.5 text-xs font-medium",
                    active
                      ? "bg-slate-900 text-white"
                      : "bg-slate-100 text-slate-700",
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
          <div className="w-full min-h-[calc(100vh-1rem)] rounded-3xl border border-slate-200 bg-white/90 p-4 shadow-xl shadow-indigo-100/40 backdrop-blur sm:min-h-[calc(100vh-2rem)] sm:p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
