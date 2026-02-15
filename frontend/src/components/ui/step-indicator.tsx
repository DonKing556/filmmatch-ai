"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface StepIndicatorProps {
  steps: string[];
  current: number;
}

export function StepIndicator({ steps, current }: StepIndicatorProps) {
  return (
    <div className="flex items-center gap-2 px-6 py-4">
      {steps.map((label, i) => {
        const isDone = i < current;
        const isActive = i === current;

        return (
          <div key={label} className="flex items-center gap-2 flex-1 last:flex-initial">
            <div className="flex items-center gap-2">
              <div
                className={cn(
                  "relative w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold transition-colors",
                  isDone && "bg-accent text-white",
                  isActive && "bg-accent/20 text-accent border border-accent",
                  !isDone && !isActive && "bg-bg-tertiary text-text-tertiary",
                )}
              >
                {isDone ? (
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  i + 1
                )}
                {isActive && (
                  <motion.div
                    className="absolute inset-0 rounded-full border-2 border-accent"
                    animate={{ scale: [1, 1.2, 1], opacity: [1, 0, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                )}
              </div>
              <span
                className={cn(
                  "text-xs font-medium hidden sm:block",
                  isActive ? "text-text-primary" : "text-text-tertiary",
                )}
              >
                {label}
              </span>
            </div>

            {/* Connector line */}
            {i < steps.length - 1 && (
              <div className="flex-1 h-px bg-bg-tertiary mx-1">
                <motion.div
                  className="h-full bg-accent"
                  initial={{ width: "0%" }}
                  animate={{ width: isDone ? "100%" : "0%" }}
                  transition={{ duration: 0.3 }}
                />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
