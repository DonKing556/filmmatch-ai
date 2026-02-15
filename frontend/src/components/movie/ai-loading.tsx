"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const PHASES = [
  { text: "Searching movie databases...", duration: 2000 },
  { text: "Analyzing your preferences...", duration: 2500 },
  { text: "Finding your best matches...", duration: 2000 },
  { text: "Ranking recommendations...", duration: 1500 },
];

export function AILoading() {
  const [phase, setPhase] = useState(0);

  useEffect(() => {
    let timeout: NodeJS.Timeout;
    const advance = () => {
      setPhase((p) => {
        const next = p + 1;
        if (next < PHASES.length) {
          timeout = setTimeout(advance, PHASES[next]!.duration);
        }
        return Math.min(next, PHASES.length - 1);
      });
    };
    timeout = setTimeout(advance, PHASES[0]!.duration);
    return () => clearTimeout(timeout);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-8 px-6" role="status" aria-label="Loading recommendations">
      {/* Animated constellation */}
      <div className="relative w-48 h-48" aria-hidden="true">
        {Array.from({ length: 12 }).map((_, i) => {
          const angle = (i / 12) * Math.PI * 2;
          const radius = 60 + (i % 3) * 20;
          return (
            <motion.div
              key={i}
              className="absolute w-2 h-2 rounded-full bg-accent"
              initial={{
                x: 96 + Math.cos(angle) * 100 - 4,
                y: 96 + Math.sin(angle) * 100 - 4,
                opacity: 0,
                scale: 0,
              }}
              animate={{
                x: 96 + Math.cos(angle + phase * 0.5) * radius - 4,
                y: 96 + Math.sin(angle + phase * 0.5) * radius - 4,
                opacity: [0, 1, 0.6, 1],
                scale: phase >= 2 ? (i < 6 ? 1.5 : 0.5) : 1,
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                repeatType: "reverse",
                delay: i * 0.1,
              }}
            />
          );
        })}

        {/* Center pulse */}
        <motion.div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-4 h-4 rounded-full bg-accent-secondary"
          animate={{
            scale: [1, 1.5, 1],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{ duration: 2, repeat: Infinity }}
        />

        {/* Connecting lines */}
        <svg className="absolute inset-0 w-full h-full opacity-20">
          {Array.from({ length: 6 }).map((_, i) => {
            const a1 = (i / 12) * Math.PI * 2;
            const a2 = ((i + 6) / 12) * Math.PI * 2;
            return (
              <motion.line
                key={i}
                x1={96 + Math.cos(a1) * 60}
                y1={96 + Math.sin(a1) * 60}
                x2={96 + Math.cos(a2) * 60}
                y2={96 + Math.sin(a2) * 60}
                stroke="#8B5CF6"
                strokeWidth={1}
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 1.5, delay: i * 0.2 }}
              />
            );
          })}
        </svg>
      </div>

      {/* Phase text */}
      <AnimatePresence mode="wait">
        <motion.p
          key={phase}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="text-lg text-text-secondary text-center"
          aria-live="polite"
        >
          {PHASES[phase]?.text}
        </motion.p>
      </AnimatePresence>

      {/* Progress bar */}
      <div
        className="w-64 h-1 rounded-full bg-bg-tertiary overflow-hidden"
        role="progressbar"
        aria-valuenow={Math.round(((phase + 1) / PHASES.length) * 100)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="Loading progress"
      >
        <motion.div
          className="h-full bg-gradient-to-r from-accent to-accent-secondary rounded-full"
          initial={{ width: "0%" }}
          animate={{ width: `${((phase + 1) / PHASES.length) * 100}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>
    </div>
  );
}
