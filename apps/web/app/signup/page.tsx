"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Logo from "../../components/Logo";
import { api } from "../../lib/api";
import { setToken } from "../../lib/auth";

export default function SignupPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit() {
    setBusy(true);
    setError("");
    try {
      const r = await api.signup(name, email, password);
      setToken(r.token);
      router.replace("/onboarding");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="centerwrap">
      <p><Link href="/" style={{ color: "var(--muted)", textDecoration: "none" }}><Logo size={30} /></Link></p>
      <h1>Create your account</h1>
      <p className="sub">Then tell SignalCraft who you are — it takes two minutes.</p>
      <div className="card">
        <label className="field">Name
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Sankiyy" />
        </label>
        <label className="field" style={{ marginTop: 10 }}>Email
          <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
        </label>
        <label className="field" style={{ marginTop: 10 }}>Password (8+ characters)
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && submit()} />
        </label>
        <p><button className="btn" onClick={submit} disabled={busy || !name || !email || password.length < 8}>
          {busy ? "Creating…" : "Sign up"}
        </button></p>
        {error && <p className="error">{error}</p>}
        <p className="muted">Have an account? <Link href="/login" style={{ color: "var(--accent2)" }}>Log in</Link></p>
      </div>
    </div>
  );
}
