"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import Logo from "../components/Logo";

export function GitHubIcon({ size = 17 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="currentColor" aria-label="GitHub">
      <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z" />
    </svg>
  );
}

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header className={"landnav" + (scrolled ? " scrolled" : "")}>
      <Link href="/" className="landbrand"><Logo size={30} /><b>Signal<span>Craft</span></b></Link>
      <nav aria-label="Product">
        <a href="#product">Product</a>
        <a href="#how">How it works</a>
        <a href="#intelligence">Intelligence</a>
        <a href="#analytics">Analytics</a>
      </nav>
      <a className="gitlink" href="https://github.com/Sanskar1724" target="_blank" rel="noreferrer" aria-label="GitHub">
        <GitHubIcon />
      </a>
      <Link href="/login" className="btn ghost small">Sign In</Link>
      <Link href="/signup" className="btn small">Get Started</Link>
      <button className="iconbtn menubtn" aria-label="Menu" aria-expanded={open} onClick={() => setOpen(!open)}>
        ☰
      </button>
      {open && (
        <div className="mobilemenu">
          <a href="#product" onClick={() => setOpen(false)}>Product</a>
          <a href="#how" onClick={() => setOpen(false)}>How it works</a>
          <a href="#intelligence" onClick={() => setOpen(false)}>Intelligence</a>
          <a href="#analytics" onClick={() => setOpen(false)}>Analytics</a>
          <Link href="/login" onClick={() => setOpen(false)}>Sign In</Link>
          <Link href="/signup" onClick={() => setOpen(false)}>Get Started</Link>
        </div>
      )}
    </header>
  );
}
