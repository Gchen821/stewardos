"use client";

import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import {
  clearStoredToken,
  fetchMe,
  getStoredToken,
  login as loginRequest,
  register as registerRequest,
  type User,
} from "@/lib/api";

type AuthContextValue = {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<User>;
  register: (username: string, password: string) => Promise<User>;
  logout: () => void;
  refreshUser: () => Promise<User | null>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  async function refreshUser() {
    if (!getStoredToken()) {
      setUser(null);
      setLoading(false);
      return null;
    }

    try {
      const nextUser = await fetchMe();
      setUser(nextUser);
      return nextUser;
    } catch {
      clearStoredToken();
      setUser(null);
      return null;
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refreshUser();
  }, []);

  async function login(username: string, password: string) {
    const result = await loginRequest(username, password);
    setUser(result.user);
    return result.user;
  }

  async function register(username: string, password: string) {
    await registerRequest(username, password);
    const result = await loginRequest(username, password);
    setUser(result.user);
    return result.user;
  }

  function logout() {
    clearStoredToken();
    setUser(null);
  }

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      isAuthenticated: user !== null,
      login,
      register,
      logout,
      refreshUser,
    }),
    [loading, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
