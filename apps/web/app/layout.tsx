import type { ReactNode } from "react";
import "./globals.css";

export const metadata = {
  title: "SignalCraft AI — Your personal AI content strategist",
  description: "Personal AI content intelligence: research, trends, opportunities, drafts, analytics and learning.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
