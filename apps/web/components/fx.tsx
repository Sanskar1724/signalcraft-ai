"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";

export function toast(msg: string) {
  window.dispatchEvent(new CustomEvent("sc-toast", { detail: msg }));
}

export function Toaster() {
  const [items, setItems] = useState<{ id: number; msg: string }[]>([]);
  const id = useRef(0);
  useEffect(() => {
    const on = (e: Event) => {
      const cur = ++id.current;
      setItems((l) => [...l, { id: cur, msg: (e as CustomEvent).detail }]);
      setTimeout(() => setItems((l) => l.filter((x) => x.id !== cur)), 2600);
    };
    window.addEventListener("sc-toast", on);
    return () => window.removeEventListener("sc-toast", on);
  }, []);
  return (
    <div className="toasts" role="status" aria-live="polite">
      {items.map((t) => (
        <div key={t.id} className="toast">{t.msg}</div>
      ))}
    </div>
  );
}

export function Reveal({ children, delay = 0 }: { children: ReactNode; delay?: number }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      el.classList.add("in");
      return;
    }
    const io = new IntersectionObserver(
      ([e]) => {
        if (e.isIntersecting) {
          el.classList.add("in");
          io.disconnect();
        }
      },
      { threshold: 0.12 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return (
    <div ref={ref} className="rv" style={{ transitionDelay: `${delay}ms` }}>
      {children}
    </div>
  );
}
