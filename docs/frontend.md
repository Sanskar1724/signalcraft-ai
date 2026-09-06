# Frontend (§17-§20, §39-§40)

Next.js 14 + TypeScript in `apps/web`. Public routes (`/`, `/login`,
`/signup`, `/onboarding`) use a minimal layout; everything under `/app`
uses the authenticated shell (sidebar, mobile bottom nav, live API status,
user menu) with a client-side guard: no token → `/login`; onboarding
incomplete → `/onboarding`.

## Routes

| Route | Purpose |
|---|---|
| `/` | Premium landing (nav, hero, signal strip, problem, how-it-works, intelligence, generation, brain, learning, agent, preview, CTA, footer) |
| `/login`, `/signup` | Session auth (token in `localStorage`, Bearer on every call) |
| `/onboarding` | 7-step wizard, persisted per step, validated completion |
| `/app` | Personalized briefing (`Good {morning}, {name}`) |
| `/app/trends`, `/app/opportunities` | Filtered/sorted intelligence with reasons |
| `/app/create` | Opportunity + platform tabs, single or all-3 generation, copy |
| `/app/library` | Search/filter + detail drawer (body, versions, performance, metric logging) |
| `/app/analytics` | SVG trend chart, best/weak topics, formats, content |
| `/app/calendar` | Schedule form + timeline |
| `/app/insights` | Working / not working / try-next + learn-to-memory |
| `/app/agent` | Chat thread, traces, suggestion chips |
| `/app/settings/profile` | Identity, niche, audience, goals, style, topics, platforms |
| `/app/settings/preferences` | Content + AI-behavior controls |
| `/app/settings/account` | Email, status, password change, logout |

## Conventions

- `lib/api.ts` is the only fetch layer (typed, token-injecting, envelope-aware).
- `components/ui.tsx` (cards, stats, pills, modal, tabs, skeletons) and
  `components/charts.tsx` (Sparkline, bars, time-ago) are shared; no
  per-page style drift — all styling lives in `app/globals.css`.
- Pages show loading / error / empty states; drafts are never faked (§42).
- Verify: `npm run typecheck && npm run build` (10/10 static routes).
