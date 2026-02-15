"use client";

import { usePathname, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

const tabs = [
  {
    key: "home" as const,
    label: "Home",
    href: "/",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
      </svg>
    ),
  },
  {
    key: "solo" as const,
    label: "Solo",
    href: "/solo",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      </svg>
    ),
  },
  {
    key: "group" as const,
    label: "Group",
    href: "/group",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    ),
  },
  {
    key: "watchlist" as const,
    label: "Watchlist",
    href: "/watchlist",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
      </svg>
    ),
  },
];

export function BottomNav() {
  const pathname = usePathname();
  const router = useRouter();

  const activeKey = tabs.find((t) =>
    t.href === "/" ? pathname === "/" : pathname.startsWith(t.href),
  )?.key ?? "home";

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 md:hidden">
      <div className="bg-bg-secondary/80 backdrop-blur-xl border-t border-glass-border">
        <div className="flex items-center justify-around h-16 max-w-lg mx-auto">
          {tabs.map((tab) => {
            const isActive = tab.key === activeKey;
            return (
              <button
                key={tab.key}
                onClick={() => router.push(tab.href)}
                className={cn(
                  "relative flex flex-col items-center justify-center w-16 h-full gap-0.5 transition-colors",
                  isActive ? "text-accent" : "text-text-tertiary",
                )}
              >
                {isActive && (
                  <motion.div
                    layoutId="nav-indicator"
                    className="absolute -top-px left-3 right-3 h-0.5 bg-accent rounded-full"
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  />
                )}
                {tab.icon}
                <span className="text-[10px] font-medium">{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
}

export function DesktopNav() {
  const pathname = usePathname();
  const router = useRouter();

  const activeKey = tabs.find((t) =>
    t.href === "/" ? pathname === "/" : pathname.startsWith(t.href),
  )?.key ?? "home";

  return (
    <header className="hidden md:block sticky top-0 z-50 bg-bg-primary/80 backdrop-blur-xl border-b border-glass-border">
      <div className="flex items-center justify-between h-16 px-8 max-w-7xl mx-auto">
        <button
          onClick={() => router.push("/")}
          className="text-xl font-bold bg-gradient-to-r from-accent to-accent-secondary bg-clip-text text-transparent"
        >
          FilmMatch AI
        </button>

        <nav className="flex items-center gap-1">
          {tabs.map((tab) => {
            const isActive = tab.key === activeKey;
            return (
              <button
                key={tab.key}
                onClick={() => router.push(tab.href)}
                className={cn(
                  "relative px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                  isActive
                    ? "text-accent"
                    : "text-text-secondary hover:text-text-primary hover:bg-bg-hover",
                )}
              >
                {isActive && (
                  <motion.div
                    layoutId="desktop-nav-indicator"
                    className="absolute inset-0 bg-accent/10 rounded-lg"
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  />
                )}
                <span className="relative">{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
