"use client";

import { useEffect, useState } from "react";
import { api, apiBase } from "../lib/api";

export function GoogleIcon() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" aria-hidden>
      <path fill="#4285F4" d="M23.5 12.3c0-.9-.1-1.5-.3-2.2H12v4.3h6.5c-.1 1.1-.8 2.7-2.4 3.8l-.1.1 3.5 2.7.2.1c2.2-2 3.8-5 3.8-8.8z" />
      <path fill="#34A853" d="M12 24c3.2 0 6-1.1 7.9-2.9l-3.8-2.9c-1 .7-2.4 1.2-4.1 1.2-3.2 0-5.9-2.1-6.8-5l-.1.1-3.6 2.8v.1C3.5 21.3 7.5 24 12 24z" />
      <path fill="#FBBC05" d="M5.2 14.4c-.2-.7-.4-1.5-.4-2.4s.1-1.7.4-2.4l-.1-.1-3.6-2.8-.1.1C.5 8.6 0 10.2 0 12s.5 3.4 1.4 4.9l3.8-2.5z" />
      <path fill="#EA4335" d="M12 4.7c1.8 0 3 .8 3.7 1.4l3.3-3.2C17.9 1.1 15.2 0 12 0 7.5 0 3.5 2.7 1.4 6.6l3.8 2.9c.9-2.7 3.6-4.8 6.8-4.8z" />
    </svg>
  );
}

/** Google sign-in with a REAL boundary (§27, §58): reports setup state,
 *  never fakes a login. Backend: GET /api/auth/google/status. */
export function GoogleButton({ mode }: { mode: string }) {
  const [state, setState] = useState<"checking" | "ready" | "unconfigured">("checking");
  const [note, setNote] = useState("");

  useEffect(() => {
    api.googleStatus()
      .then((s) => setState(s.configured ? "ready" : "unconfigured"))
      .catch(() => setState("unconfigured"));
  }, []);

  function click() {
    if (state === "ready") {
      window.location.href = `${apiBase}/api/auth/google/start`;
    } else {
      setNote("Google sign-in isn't configured on this server yet — use email, or ask the admin to set GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET. Nothing was faked.");
    }
  }

  return (
    <>
      <button className="gbtn" onClick={click} disabled={state === "checking"}>
        <GoogleIcon /> Continue with Google
      </button>
      {note && <p className="muted">{note}</p>}
      <p className="stamp" style={{ display: "none" }}>{mode}</p>
    </>
  );
}
