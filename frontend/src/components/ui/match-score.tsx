"use client";

import { useEffect, useState } from "react";
import { motion, useSpring, useTransform } from "framer-motion";
import { cn } from "@/lib/utils";

interface MatchScoreProps {
  score: number;
  size?: "sm" | "md" | "lg";
  animate?: boolean;
}

export function MatchScore({ score, size = "md", animate = true }: MatchScoreProps) {
  const springValue = useSpring(0, { stiffness: 100, damping: 20 });
  const displayValue = useTransform(springValue, (v) => Math.round(v));
  const [display, setDisplay] = useState(animate ? 0 : score);

  useEffect(() => {
    if (animate) {
      springValue.set(score);
      const unsubscribe = displayValue.on("change", (v) => setDisplay(v));
      return unsubscribe;
    }
  }, [score, animate, springValue, displayValue]);

  const percentage = (score / 10) * 100;

  const color =
    score >= 8 ? "text-success" : score >= 5 ? "text-warning" : "text-error";
  const ringColor =
    score >= 8
      ? "stroke-success"
      : score >= 5
        ? "stroke-warning"
        : "stroke-error";

  const sizeMap = {
    sm: { box: "w-10 h-10", text: "text-xs", stroke: 3, r: 16 },
    md: { box: "w-14 h-14", text: "text-sm", stroke: 3, r: 22 },
    lg: { box: "w-20 h-20", text: "text-lg", stroke: 4, r: 32 },
  };

  const s = sizeMap[size];
  const circumference = 2 * Math.PI * s.r;
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <div
      className={cn("relative inline-flex items-center justify-center", s.box)}
      role="meter"
      aria-valuenow={score}
      aria-valuemin={0}
      aria-valuemax={10}
      aria-label={`Match score: ${score} out of 10`}
    >
      <svg className="absolute inset-0 -rotate-90" viewBox="0 0 80 80" aria-hidden="true">
        <circle
          cx="40" cy="40" r={s.r}
          fill="none"
          strokeWidth={s.stroke}
          className="stroke-bg-tertiary"
        />
        <motion.circle
          cx="40" cy="40" r={s.r}
          fill="none"
          strokeWidth={s.stroke}
          strokeLinecap="round"
          className={ringColor}
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        />
      </svg>
      <span className={cn("font-bold", s.text, color)}>
        {display}
      </span>
    </div>
  );
}
