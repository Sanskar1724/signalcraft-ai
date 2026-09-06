"use client";

const KEY = "sc_token";

export function getToken(): string | null {
  try {
    return localStorage.getItem(KEY);
  } catch {
    return null;
  }
}

export function setToken(t: string) {
  localStorage.setItem(KEY, t);
}

export function clearToken() {
  try {
    localStorage.removeItem(KEY);
  } catch {
    /* noop */
  }
}

export async function authHeaders(): Promise<Record<string, string>> {
  const t = getToken();
  return t ? { Authorization: `Bearer ${t}` } : {};
}
