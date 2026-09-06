"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Logo from "../../components/Logo";
import { api } from "../../lib/api";
import { setToken } from "../../lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit() {
    setBusy(true);
    setError("");
    try {
      const r = await api.login(email, password);
      setToken(r.token);
      router.replace(r.user.onboarding_status === "COMPLETED" ? "/app" : "/onboarding");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="centerwrap">
      <p><Link href="/" style={{ color: "var(--muted)", textDecoration: "none" }}><Logo size={30} /></Link></p>
      <h1>Welcome back</h1>
      <p className="sub">Log in to your content intelligence.</p>
      <div className="card">
        <label className="field">Email
          <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
        </label>
        <label className="field" style={{ marginTop: 10 }}>Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && submit()} />
        </label>
        <p><button className="btn" onClick={submit} disabled={busy || !email || !password}>
          {busy ? "Logging in…" : "Log in"}
        </button></p>
        {error && <p className="error">{error}</p>}
        <p className="muted">New here? <Link href="/signup" style={{ color: "var(--accent2)" }}>Create an account</Link></p>
      </div>
    </div>
  );
}
