"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { type ReactNode, useEffect, useState } from "react";

import { useAuth } from "@/components/auth-provider";

const repositoryItems = [
  { href: "/agents", label: "Agents" },
  { href: "/skills", label: "Skills" },
  { href: "/tools", label: "Tools" },
];

const userItems = [
  { href: "/model-settings", label: "模型设置" },
  { href: "/settings", label: "账户设置" },
  { href: "/system-settings", label: "系统设置" },
];

function clsx(...values: Array<string | false>) {
  return values.filter(Boolean).join(" ");
}

export function ConsoleShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const { loading, user, logout } = useAuth();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const menuItems = [
    { href: "/chat", label: "主控对话" },
    { href: "/chat/subagents", label: "子agent对话" },
    ...repositoryItems,
    ...userItems,
    { href: "/auth", label: "用户登录" },
  ];
  const displayName = user?.username ?? (loading ? "加载中" : "未登录");
  const avatarLabel = displayName.slice(0, 1).toUpperCase() || "U";

  useEffect(() => {
    const storedValue = window.localStorage.getItem("stewardos-console-sidebar-collapsed");
    setSidebarCollapsed(storedValue === "true");
  }, []);

  function toggleSidebar() {
    setSidebarCollapsed((prev) => {
      const next = !prev;
      window.localStorage.setItem("stewardos-console-sidebar-collapsed", String(next));
      return next;
    });
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_12%_10%,_#d1fae5_0%,_#eff6ff_36%,_#f8fafc_68%)] text-slate-900">
      <div className="flex min-h-screen w-full">
        <aside
          className={clsx(
            "hidden shrink-0 border-r border-teal-100 bg-white/95 lg:flex lg:flex-col",
            sidebarCollapsed ? "w-24" : "w-80",
          )}
        >
          <div className={clsx("border-b border-teal-100", sidebarCollapsed ? "px-3 py-5" : "px-5 py-5")}>
            <div
              className={clsx(
                "flex",
                sidebarCollapsed ? "justify-center items-center" : "items-start justify-between gap-3",
              )}
            >
              {!sidebarCollapsed ? (
                <div className="flex min-w-0 flex-1 overflow-hidden transition-all duration-200">
                  <div className="w-44 min-h-14 transition-all duration-200">
                    <p className="text-xs uppercase tracking-[0.2em] text-teal-700">StewardOS</p>
                    <h1 className="mt-2 text-2xl font-semibold text-slate-950">控制台</h1>
                  </div>
                </div>
              ) : null}
              <button
                type="button"
                onClick={toggleSidebar}
                className={clsx(
                  "flex h-14 w-14 shrink-0 items-center justify-center rounded-xl border border-slate-200 bg-white px-0 py-0 text-xs font-medium text-slate-600 hover:border-teal-200 hover:bg-teal-50 hover:text-teal-700",
                )}
                title={sidebarCollapsed ? "展开侧栏" : "收起侧栏"}
                aria-label={sidebarCollapsed ? "展开侧栏" : "收起侧栏"}
              >
                {sidebarCollapsed ? ">" : "<"}
              </button>
            </div>
          </div>

          <div className={clsx("border-b border-teal-100", sidebarCollapsed ? "px-2 py-4" : "px-4 py-4")}>
            <div className={clsx("overflow-hidden transition-all duration-200", sidebarCollapsed ? "h-0 opacity-0" : "h-4 opacity-100")}>
              <p className="px-2 text-xs uppercase tracking-[0.16em] text-slate-500">主控对话</p>
            </div>
            <Link
              href="/chat"
              title="管家对话"
              className={clsx(
                "mt-2 flex items-center rounded-xl text-sm font-medium transition",
                sidebarCollapsed ? "justify-center px-2 py-3" : "gap-3 px-3 py-2",
                pathname === "/chat"
                  ? "bg-teal-700 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-teal-50",
              )}
            >
              <span className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-white/70 text-base text-current">
                ◎
              </span>
              {!sidebarCollapsed ? <span className="truncate">管家对话</span> : null}
            </Link>
            <Link
              href="/chat/subagents"
              title="子agent对话"
              className={clsx(
                "mt-2 flex items-center rounded-xl text-sm font-medium transition",
                sidebarCollapsed ? "justify-center px-2 py-3" : "gap-3 px-3 py-2",
                pathname.startsWith("/chat/subagents")
                  ? "border border-teal-200 bg-teal-50 text-teal-800"
                  : "bg-slate-50 text-slate-700 hover:bg-teal-50",
              )}
            >
              <span className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-white/70 text-base text-current">
                ◉
              </span>
              {!sidebarCollapsed ? <span className="truncate">子agent对话</span> : null}
            </Link>
          </div>

          <div className={clsx(sidebarCollapsed ? "px-2 py-4" : "px-4 py-4")}>
            <div className={clsx("overflow-hidden transition-all duration-200", sidebarCollapsed ? "h-0 opacity-0" : "h-4 opacity-100")}>
              <p className="px-2 text-xs uppercase tracking-[0.16em] text-slate-500">仓库设置</p>
            </div>
            <nav className="mt-2 flex flex-col gap-1">
              {repositoryItems.map((item) => {
                const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    title={item.label}
                    className={clsx(
                      "flex items-center rounded-xl text-sm font-medium transition",
                      sidebarCollapsed ? "justify-center px-2 py-3" : "gap-3 px-3 py-2",
                      active ? "bg-teal-700 text-white" : "text-slate-700 hover:bg-teal-50",
                    )}
                  >
                    <span className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-xs font-semibold text-current">
                      {item.label === "Agents" ? "A" : item.label === "Skills" ? "S" : "T"}
                    </span>
                    {!sidebarCollapsed ? <span className="truncate">{item.label}</span> : null}
                  </Link>
                );
              })}
            </nav>
          </div>

          <div className="mt-auto border-t border-teal-100 p-4">
            <details className="group">
              <summary
                title={displayName}
                className={clsx(
                  "flex cursor-pointer list-none rounded-xl border border-slate-200 bg-slate-50 px-3 py-3 hover:border-teal-200 hover:bg-teal-50",
                  sidebarCollapsed ? "justify-center" : "items-center gap-3",
                )}
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-teal-100 font-semibold text-teal-700">
                  {avatarLabel}
                </div>
                {!sidebarCollapsed ? (
                  <div>
                    <p className="text-sm font-semibold text-slate-900">{displayName}</p>
                    <p className="text-xs text-slate-500">{user ? "用户设置" : "点击登录或注册"}</p>
                  </div>
                ) : null}
              </summary>
              <div className={clsx("mt-2 space-y-1 rounded-xl border border-slate-200 bg-white p-2 text-sm", sidebarCollapsed && "hidden")}>
                {user ? (
                  <>
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
                    <button
                      type="button"
                      onClick={logout}
                      className="block w-full rounded-lg px-3 py-2 text-left text-slate-700 hover:bg-rose-50 hover:text-rose-700"
                    >
                      退出登录
                    </button>
                  </>
                ) : (
                  <Link
                    href="/auth"
                    className="block rounded-lg px-3 py-2 text-slate-700 hover:bg-teal-50"
                  >
                    用户登录
                  </Link>
                )}
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
                    active ? "bg-teal-700 text-white" : "bg-slate-100 text-slate-700",
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
          <div className="min-h-[calc(100vh-1rem)] rounded-3xl border border-teal-100 bg-white/90 p-4 shadow-xl shadow-teal-100/40 backdrop-blur sm:min-h-[calc(100vh-2rem)] sm:p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
