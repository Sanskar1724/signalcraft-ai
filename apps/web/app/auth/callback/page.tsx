"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { api } from "../../../lib/api";
import { setToken } from "../../../lib/auth";

export default function AuthCallbackPage() {
  return (
    <Suspense>
      <CallbackInner />
    </Suspense>
  );
}

function CallbackInner() {
  const router = useRouter();
  const params = useSearchParams();
  const [error, setError] = useState("");

  useEffect(() => {
    const err = params.get("error");
    const token = params.get("token");
    if (err) {
      setError(`Google sign-in failed (${err}). Try email sign-in instead.`);
      return;
    }
    if (!token) {
      setError("Missing session token. Try signing in again.");
      return;
    }
    setToken(token);
    api.me()
      .then((me) => router.replace(me.onboarding_status === "COMPLETED" ? "/app" : "/onboarding"))
      .catch(() => setError("Session invalid. Try signing in again."));
  }, [params, router]);

  return (
    <div className="centerwrap">
      <h1>Signing you in…</h1>
      {error ? (
        <>
          <p className="error">{error}</p>
          <p><Link href="/login" className="btn">Back to login</Link></p>
        </>
      ) : (
        <p className="muted"><span className="spin" />Verifying with Google…</p>
      )}
    </div>
  );
}
