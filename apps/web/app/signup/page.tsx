"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Logo from "../../components/Logo";
import { GoogleButton } from "../../components/GoogleButton";
import SignalField from "../../components/SignalField";
import { api } from "../../lib/api";
import { setToken } from "../../lib/auth";

export default function SignupPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [show, setShow] = useState(false);
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
    <div className="authsplit">
      <div className="authstory">
        <SignalField />
        <div style={{ position: "relative" }}>
          <p><Logo size={36} /></p>
          <h2 className="landh">Build your<br />content intelligence.</h2>
          <p className="muted">Tell SignalCraft who you are. It researches, strategizes, creates and learns with you.</p>
          <div className="loop">
            <span>You</span><i>→</i><span>Profile</span><i>→</i><span>Trends</span><i>→</i><span>Content</span><i>→</i><span>Learning</span>
          </div>
        </div>
      </div>
      <div className="authform">
        <div>
          <h1>Build your content intelligence</h1>
          <p className="sub">Two minutes of setup, then your first briefing.</p>
          <label className="field">Name
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Sankiyy" autoComplete="name" />
          </label>
          <label className="field" style={{ marginTop: 10 }}>Email
            <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" autoComplete="email" />
          </label>
          <label className="field" style={{ marginTop: 10 }}>Password (8+ characters)
            <div className="row" style={{ flexWrap: "nowrap" }}>
              <input type={show ? "text" : "password"} value={password}
                style={{ flex: 1 }} onChange={(e) => setPassword(e.target.value)}
                autoComplete="new-password"
                onKeyDown={(e) => e.key === "Enter" && submit()} />
              <button type="button" className="btn ghost small" onClick={() => setShow(!show)}
                aria-label={show ? "Hide password" : "Show password"}>
                {show ? "Hide" : "Show"}
              </button>
            </div>
          </label>
          <p><button className="btn" style={{ width: "100%" }} onClick={submit} disabled={busy || !name || !email || password.length < 8}>
            {busy ? "Creating…" : "Sign up"}
          </button></p>
          {error && <p className="error">{error}</p>}
          <div className="or">or</div>
          <GoogleButton mode="signup" />
          <p className="muted">Have an account? <Link href="/login" style={{ color: "var(--accent)" }}>Sign in</Link></p>
        </div>
      </div>
    </div>
  );
}
