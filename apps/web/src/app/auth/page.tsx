"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { type FormEvent, useState } from "react";

import { useAuth } from "@/components/auth-provider";

type AuthMode = "login" | "register";

function getErrorMessage(error: unknown) {
  if (!(error instanceof Error)) {
    return "请求失败，请稍后重试";
  }

  try {
    const payload = JSON.parse(error.message) as { detail?: string };
    if (typeof payload.detail === "string") {
      return payload.detail;
    }
  } catch {
    return error.message;
  }

  return error.message;
}

export default function AuthPage() {
  const router = useRouter();
  const { login, register } = useAuth();
  const [mode, setMode] = useState<AuthMode>("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    if (mode === "register" && password !== confirmPassword) {
      setError("两次输入的密码不一致");
      return;
    }

    setSubmitting(true);
    try {
      if (mode === "login") {
        await login(username, password);
      } else {
        await register(username, password);
      }
      router.push("/settings");
    } catch (submitError) {
      setError(getErrorMessage(submitError));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-[linear-gradient(135deg,_#f7fee7_0%,_#ecfeff_42%,_#eff6ff_100%)] px-4 py-10">
      <div className="grid w-full max-w-5xl overflow-hidden rounded-[2rem] border border-emerald-100 bg-white shadow-[0_30px_90px_rgba(15,23,42,0.12)] lg:grid-cols-[1.1fr_0.9fr]">
        <section className="hidden bg-[radial-gradient(circle_at_top,_rgba(16,185,129,0.16),_transparent_45%),linear-gradient(180deg,_#022c22_0%,_#134e4a_100%)] p-10 text-white lg:block">
          <p className="text-sm uppercase tracking-[0.3em] text-emerald-200">StewardOS</p>
          <h1 className="mt-6 max-w-sm text-5xl font-semibold leading-tight">
            用一个账户进入你的控制台。
          </h1>
          <p className="mt-6 max-w-md text-sm leading-7 text-emerald-50/88">
            登录后即可进入主控对话、资产仓库和账户设置。注册成功后会自动登录，并在账户设置中显示当前用户名。
          </p>
          <div className="mt-10 rounded-3xl border border-white/15 bg-white/10 p-5 backdrop-blur">
            <p className="text-xs uppercase tracking-[0.2em] text-emerald-100/80">默认体验账号</p>
            <p className="mt-3 text-2xl font-semibold">admin</p>
            <p className="mt-1 text-sm text-emerald-50/80">密码：123456</p>
          </div>
        </section>

        <section className="p-6 sm:p-10">
          <div className="mx-auto max-w-md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-emerald-700">账户入口</p>
                <h2 className="mt-2 text-3xl font-semibold text-slate-950">
                  {mode === "login" ? "登录" : "注册"}
                </h2>
              </div>
              <Link href="/chat" className="text-sm text-slate-500 hover:text-slate-900">
                返回控制台
              </Link>
            </div>

            <div className="mt-8 inline-flex rounded-2xl bg-slate-100 p-1">
              <button
                type="button"
                onClick={() => setMode("login")}
                className={`rounded-xl px-4 py-2 text-sm font-medium ${
                  mode === "login" ? "bg-white text-slate-950 shadow-sm" : "text-slate-500"
                }`}
              >
                用户登录
              </button>
              <button
                type="button"
                onClick={() => setMode("register")}
                className={`rounded-xl px-4 py-2 text-sm font-medium ${
                  mode === "register" ? "bg-white text-slate-950 shadow-sm" : "text-slate-500"
                }`}
              >
                创建账户
              </button>
            </div>

            <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
              <label className="block space-y-2">
                <span className="text-sm font-medium text-slate-700">用户名</span>
                <input
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  placeholder="输入用户名"
                  required
                  className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none"
                />
              </label>

              <label className="block space-y-2">
                <span className="text-sm font-medium text-slate-700">密码</span>
                <input
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="输入密码"
                  required
                  className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none"
                />
              </label>

              {mode === "register" ? (
                <label className="block space-y-2">
                  <span className="text-sm font-medium text-slate-700">确认密码</span>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(event) => setConfirmPassword(event.target.value)}
                    placeholder="再次输入密码"
                    required
                    className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none"
                  />
                </label>
              ) : null}

              {error ? (
                <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
                  {error}
                </div>
              ) : null}

              <button
                type="submit"
                disabled={submitting}
                className="w-full rounded-2xl bg-slate-950 px-4 py-3 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-400"
              >
                {submitting ? "提交中..." : mode === "login" ? "登录进入控制台" : "注册并登录"}
              </button>
            </form>
          </div>
        </section>
      </div>
    </main>
  );
}
