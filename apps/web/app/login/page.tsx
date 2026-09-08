"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Logo from "../../components/Logo";
import { GoogleButton } from "../../components/GoogleButton";
import SignalField from "../../components/SignalField";
import { api } from "../../lib/api";
import { setToken } from "../../lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [show, setShow] = useState(false);
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
    <div className="authsplit">
      <div className="authstory">
        <SignalField />
        <div style={{ position: "relative" }}>
          <p><Logo size={36} /></p>
          <h2 className="landh">AI intelligence<br />for your content.</h2>
          <p className="muted">Research what matters. Create what resonates. Learn what works.</p>
          <div className="signalstrip" style={{ justifyContent: "flex-start" }}>
            <span className="pill">Trends for you</span>
            <span className="pill">Brief-led drafts</span>
            <span className="pill">Learning loop</span>
          </div>
        </div>
      </div>
      <div className="authform">
        <div>
          <h1>Welcome back</h1>
          <p className="sub">Log in to your content intelligence.</p>
          <label className="field">Email
            <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" autoComplete="email" />
          </label>
          <label className="field" style={{ marginTop: 10 }}>Password
            <div className="row" style={{ flexWrap: "nowrap" }}>
              <input type={show ? "text" : "password"} value={password}
                style={{ flex: 1 }} onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                onKeyDown={(e) => e.key === "Enter" && submit()} />
              <button type="button" className="btn ghost small" onClick={() => setShow(!show)}
                aria-label={show ? "Hide password" : "Show password"}>
                {show ? "Hide" : "Show"}
              </button>
            </div>
          </label>
          <p><button className="btn" style={{ width: "100%" }} onClick={submit} disabled={busy || !email || !password}>
            {busy ? "Logging in…" : "Continue"}
          </button></p>
          {error && <p className="error">{error}</p>}
          <p className="muted">Forgot your password? Email reset isn&apos;t enabled on this server — use Google sign-in or ask the admin to reset it.</p>
          <div className="or">or</div>
          <GoogleButton mode="login" />
          <p className="muted">Don&apos;t have an account? <Link href="/signup" style={{ color: "var(--accent)" }}>Sign up</Link></p>
        </div>
      </div>
    </div>
  );
}
