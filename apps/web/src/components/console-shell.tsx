"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";

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
  const butlerEntryActive = pathname === "/chat";
  const historyViewportRef = useRef<HTMLDivElement | null>(null);
  const wheelDeltaRef = useRef(0);
  const bottomHitRef = useRef(0);
  const [historyVisibleCount, setHistoryVisibleCount] = useState(24);
  const [loadHintVisible, setLoadHintVisible] = useState(false);
  const visibleHistory = useMemo(
    () => conversationHistory.slice(0, historyVisibleCount),
    [conversationHistory, historyVisibleCount],
  );
  const hasMoreHistory = visibleHistory.length < conversationHistory.length;

  useEffect(() => {
    setHistoryVisibleCount((prev) => {
      if (conversationHistory.length <= prev) return prev;
      return Math.max(24, prev);
    });
  }, [conversationHistory.length]);

  function loadMoreHistory() {
    setHistoryVisibleCount((prev) => Math.min(prev + 20, conversationHistory.length));
    bottomHitRef.current = 0;
    setLoadHintVisible(false);
  }

  function onHistoryWheel(event: React.WheelEvent<HTMLDivElement>) {
    wheelDeltaRef.current = event.deltaY;
  }

  function onHistoryScroll(event: React.UIEvent<HTMLDivElement>) {
    if (!hasMoreHistory) return;
    const el = event.currentTarget;
    const nearBottom = el.scrollTop + el.clientHeight >= el.scrollHeight - 16;
    const scrollingDown = wheelDeltaRef.current > 0;
    if (!nearBottom || !scrollingDown) return;
    bottomHitRef.current += 1;
    if (bottomHitRef.current >= 2) {
      loadMoreHistory();
      return;
    }
    setLoadHintVisible(true);
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_12%_10%,_#d1fae5_0%,_#eff6ff_36%,_#f8fafc_68%)] text-slate-900">
      <div className="flex min-h-screen w-full">
        <aside className="hidden w-80 shrink-0 border-r border-teal-100 bg-white/95 lg:flex lg:flex-col">
          <div className="border-b border-teal-100 px-5 py-5">
            <p className="text-xs uppercase tracking-[0.2em] text-teal-700">StewardOS</p>
            <h1 className="mt-2 text-2xl font-semibold text-slate-950">控制台</h1>
          </div>

          <div className="border-b border-teal-100 px-4 py-4">
            <p className="px-2 text-xs uppercase tracking-[0.16em] text-slate-500">主控对话</p>
            <Link
              href="/chat"
              className={clsx(
                "mt-2 block rounded-xl px-3 py-2 text-sm font-medium transition",
                butlerEntryActive
                  ? "bg-teal-700 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-teal-50",
              )}
            >
              管家对话
            </Link>
            <div className="mt-4">
              <p className="px-2 text-[11px] text-slate-400">历史会话</p>
              <div
                ref={historyViewportRef}
                className="mt-1 max-h-64 space-y-1 overflow-y-auto pr-1"
                onWheel={onHistoryWheel}
                onScroll={onHistoryScroll}
              >
                {conversationHistory.length > 0 ? (
                  visibleHistory.map((history) => (
                    <Link
                      key={history.id}
                      href={`/chat/session/${history.id}`}
                      className={clsx(
                        "block w-full rounded-lg px-3 py-2 text-left text-xs transition",
                        pathname === `/chat/session/${history.id}`
                          ? "border border-teal-300 bg-teal-50 font-medium text-teal-800"
                          : pathname.startsWith("/chat")
                            ? "text-slate-700 hover:bg-teal-50"
                            : "text-slate-500",
                      )}
                    >
                      {history.title}
                    </Link>
                  ))
                ) : (
                  <p className="rounded-lg px-3 py-2 text-xs text-slate-400">暂无历史记录</p>
                )}
                {hasMoreHistory ? (
                  <div className="px-1 pb-1 pt-1">
                    {loadHintVisible ? (
                      <p className="px-2 py-1 text-[11px] text-slate-400">
                        继续下滑一次可加载更多
                      </p>
                    ) : null}
                    <button
                      type="button"
                      onClick={loadMoreHistory}
                      className="w-full rounded-lg border border-slate-200 bg-white px-2 py-1.5 text-[11px] text-slate-600 hover:border-teal-200 hover:bg-teal-50"
                    >
                      加载更多历史
                    </button>
                  </div>
                ) : null}
              </div>
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
                        ? "bg-teal-700 text-white"
                        : "text-slate-700 hover:bg-teal-50",
                    )}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </div>

          <div className="mt-auto border-t border-teal-100 p-4">
            <details className="group">
              <summary className="flex cursor-pointer list-none items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-3 py-3 hover:border-teal-200 hover:bg-teal-50">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-teal-100 font-semibold text-teal-700">
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
                          ? "bg-teal-700 text-white"
                          : "text-slate-700 hover:bg-teal-50",
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
                      ? "bg-teal-700 text-white"
                      : "bg-slate-100 text-slate-700",
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
          <div className="w-full min-h-[calc(100vh-1rem)] rounded-3xl border border-teal-100 bg-white/90 p-4 shadow-xl shadow-teal-100/40 backdrop-blur sm:min-h-[calc(100vh-2rem)] sm:p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
