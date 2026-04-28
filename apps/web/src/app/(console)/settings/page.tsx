"use client";

import Link from "next/link";
import { type FormEvent, useEffect, useState } from "react";

import { useAuth } from "@/components/auth-provider";
import {
  browseRepositoryDirectories,
  fetchRepositorySettings,
  type RepositoryDirectoryBrowse,
  updateRepositorySettings,
  type RepositorySettings,
} from "@/lib/api";

export default function SettingsPage() {
  const { user, loading, logout } = useAuth();
  const [repositorySettings, setRepositorySettings] = useState<RepositorySettings | null>(null);
  const [repositoryRootPath, setRepositoryRootPath] = useState("");
  const [saving, setSaving] = useState(false);
  const [pickerOpen, setPickerOpen] = useState(false);
  const [directoryBrowser, setDirectoryBrowser] = useState<RepositoryDirectoryBrowse | null>(null);
  const [loadingDirectories, setLoadingDirectories] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRepositorySettings()
      .then((result) => {
        setRepositorySettings(result);
        setRepositoryRootPath(result.repository_root_path);
      })
      .catch(() => setRepositorySettings(null));
  }, []);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setMessage(null);
    setError(null);

    try {
      const result = await updateRepositorySettings({
        repository_root_path: repositoryRootPath,
      });
      setRepositorySettings(result);
      setMessage("本地资产保存路径已写入 .env 并热加载");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "保存失败");
    } finally {
      setSaving(false);
    }
  }

  async function loadDirectories(path?: string) {
    setLoadingDirectories(true);
    setError(null);
    try {
      const result = await browseRepositoryDirectories(path);
      setDirectoryBrowser(result);
    } catch (browseError) {
      setError(browseError instanceof Error ? browseError.message : "目录加载失败");
    } finally {
      setLoadingDirectories(false);
    }
  }

  async function openDirectoryPicker() {
    setPickerOpen(true);
    await loadDirectories(repositoryRootPath || undefined);
  }

  function applyDirectoryPath(path: string) {
    setRepositoryRootPath(path);
    setPickerOpen(false);
  }

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <p className="inline-flex rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">账户设置</p>
        <h2 className="text-3xl font-semibold tracking-tight text-slate-950">当前登录用户</h2>
      </header>
      <div className="rounded-2xl border border-slate-200 bg-white p-5">
        {loading ? (
          <p className="text-sm text-slate-600">正在加载当前账户...</p>
        ) : user ? (
          <div className="space-y-2 text-sm text-slate-700">
            <p>用户名：{user.username}</p>
            <p>状态：{user.status}</p>
            <button
              type="button"
              onClick={logout}
              className="mt-4 rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:border-rose-200 hover:text-rose-700"
            >
              退出登录
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            <p className="text-sm text-slate-600">当前未登录，请先进入登录页或注册新账户。</p>
            <Link
              href="/auth"
              className="inline-flex rounded-xl bg-slate-900 px-4 py-2 text-sm font-medium text-white"
            >
              前往用户登录
            </Link>
          </div>
        )}
      </div>

      <form onSubmit={onSubmit} className="space-y-5 rounded-3xl border border-slate-200 bg-white p-6">
        <header className="space-y-1">
          <h3 className="text-xl font-semibold text-slate-950">本地资产保存路径</h3>
          <p className="text-sm text-slate-600">用于保存当前用户的全部资产与配置。系统会在根目录下按 `users/&lt;user_id&gt;/...` 自动组织 Agent、Skills、Tools。</p>
        </header>

        <label className="block space-y-2">
          <span className="text-sm font-medium text-slate-700">资产根目录</span>
          <div className="flex gap-3">
            <input
              value={repositoryRootPath}
              onChange={(event) => setRepositoryRootPath(event.target.value)}
              className="min-w-0 flex-1 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none"
              placeholder="./repositories"
            />
            <button
              type="button"
              onClick={openDirectoryPicker}
              className="shrink-0 rounded-2xl border border-slate-200 px-4 py-3 text-sm font-medium text-slate-700 hover:border-slate-300 hover:bg-slate-50"
            >
              选择文件夹
            </button>
          </div>
        </label>

        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
          <p>当前解析后的根目录：{repositorySettings?.resolved_repository_root ?? "-"}</p>
          <p className="mt-1">示例结构：`users/&lt;id&gt;/agents/*`、`users/&lt;id&gt;/skills/*`、`users/&lt;id&gt;/tools/*`、`users/&lt;id&gt;/config/*`</p>
        </div>

        {message ? <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{message}</div> : null}
        {error ? <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div> : null}

        <button
          type="submit"
          disabled={saving}
          className="rounded-2xl bg-slate-950 px-5 py-3 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {saving ? "保存中..." : "保存路径设置"}
        </button>
      </form>

      {pickerOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/35 p-4">
          <div className="flex max-h-[80vh] w-full max-w-3xl flex-col overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-2xl">
            <header className="space-y-2 border-b border-slate-200 px-6 py-5">
              <h3 className="text-xl font-semibold text-slate-950">选择资产根目录</h3>
              <p className="text-sm text-slate-600">选择后会把当前目录写入资产根路径，用于保存当前用户的仓库和配置。</p>
            </header>

            <div className="space-y-4 px-6 py-5">
              <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                当前目录：{(directoryBrowser?.current_path ?? repositoryRootPath) || "-"}
              </div>

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => void loadDirectories(directoryBrowser?.parent_path ?? undefined)}
                  disabled={loadingDirectories || !directoryBrowser?.parent_path}
                  className="rounded-2xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  返回上级
                </button>
                <button
                  type="button"
                  onClick={() => directoryBrowser && applyDirectoryPath(directoryBrowser.current_path)}
                  disabled={!directoryBrowser}
                  className="rounded-2xl bg-slate-950 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-400"
                >
                  选择当前文件夹
                </button>
                <button
                  type="button"
                  onClick={() => setPickerOpen(false)}
                  className="rounded-2xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700"
                >
                  取消
                </button>
              </div>

              <div className="max-h-[44vh] overflow-y-auto rounded-2xl border border-slate-200">
                {loadingDirectories ? (
                  <div className="px-4 py-6 text-sm text-slate-600">正在加载目录...</div>
                ) : directoryBrowser?.directories.length ? (
                  <div className="divide-y divide-slate-200">
                    {directoryBrowser.directories.map((directory) => (
                      <button
                        key={directory.path}
                        type="button"
                        onClick={() => void loadDirectories(directory.path)}
                        className="flex w-full items-center justify-between px-4 py-3 text-left hover:bg-slate-50"
                      >
                        <span className="text-sm font-medium text-slate-800">{directory.name}</span>
                        <span className="text-xs text-slate-500">{directory.path}</span>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="px-4 py-6 text-sm text-slate-600">当前目录下没有可进入的子文件夹。</div>
                )}
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
