"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "../../../../lib/api";
import { clearToken } from "../../../../lib/auth";
import { Card, Loading, useApi } from "../../../../components/ui";

export default function AccountPage() {
  const router = useRouter();
  const me = useApi(() => api.me());
  const [cur, setCur] = useState("");
  const [next, setNext] = useState("");
  const [msg, setMsg] = useState("");

  async function password() {
    setMsg("");
    try {
      await api.changePassword(cur, next);
      setMsg("Password changed — please log in again.");
      setTimeout(() => {
        clearToken();
        router.replace("/login");
      }, 1200);
    } catch (e) {
      setMsg(`Error: ${(e as Error).message}`);
    }
  }

  if (me.busy) return (<><h1>Account</h1><Loading /></>);
  if (me.error || !me.data) return (<><h1>Account</h1><div className="error">API unavailable: {me.error}</div></>);

  return (
    <>
      <h1>Settings</h1>
      <div className="row" style={{ marginBottom: 4 }}>
        <Link href="/app/settings/profile" className="btn ghost small">Profile</Link>
        <Link href="/app/settings/preferences" className="btn ghost small">Preferences</Link>
        <Link href="/app/settings/account" className="btn small">Account</Link>
      </div>
      <h2>Account</h2>
      <Card>
        <p><span className="muted">Name:</span> <b>{me.data.user.name}</b></p>
        <p><span className="muted">Email:</span> <b>{me.data.user.email || "—"}</b></p>
        <p><span className="muted">Onboarding:</span> <b>{me.data.onboarding_status}</b></p>
      </Card>
      <h2>Change password</h2>
      <Card>
        <label className="field">Current password
          <input type="password" value={cur} onChange={(e) => setCur(e.target.value)} /></label>
        <label className="field" style={{ marginTop: 10 }}>New password (8+ characters)
          <input type="password" value={next} onChange={(e) => setNext(e.target.value)} /></label>
        <p style={{ marginBottom: 0 }}>
          <button className="btn" onClick={password} disabled={!cur || next.length < 8}>Change password</button>
        </p>
        {msg && <p className="muted">{msg}</p>}
      </Card>
      <p>
        <button
          className="btn ghost"
          onClick={() => {
            api.logout().finally(() => {
              clearToken();
              router.replace("/login");
            });
          }}
        >
          Log out everywhere
        </button>
      </p>
    </>
  );
}
