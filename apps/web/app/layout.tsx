import { Inter } from "next/font/google";
import type { ReactNode } from "react";
import { Toaster } from "../components/fx";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], display: "swap" });

export const metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3001"),
  title: "SignalCraft AI — Your Personal AI Content Strategist",
  description:
    "SignalCraft understands your audience, tracks what is happening right now, finds your best content opportunities, and turns them into content that sounds like you.",
  openGraph: {
    title: "SignalCraft AI — Your Personal AI Content Strategist",
    description: "Research what matters. Create what resonates. Learn what works.",
    type: "website",
    images: ["/og-image.png"],
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className={inter.className}>
      <body>
        {children}
        <Toaster />
      </body>
    </html>
  );
}
