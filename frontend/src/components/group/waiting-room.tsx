"use client";

import { motion } from "framer-motion";

interface WaitingRoomProps {
  members: { name: string; ready: boolean }[];
  totalExpected: number;
}

export function WaitingRoom({ members, totalExpected }: WaitingRoomProps) {
  const readyCount = members.filter((m) => m.ready).length;
  const progress = totalExpected > 0 ? (readyCount / totalExpected) * 100 : 0;

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] px-6 gap-8">
      {/* Animated ring */}
      <div className="relative w-32 h-32">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="42"
            fill="none"
            stroke="var(--color-bg-tertiary)"
            strokeWidth="6"
          />
          <motion.circle
            cx="50"
            cy="50"
            r="42"
            fill="none"
            stroke="var(--color-accent)"
            strokeWidth="6"
            strokeLinecap="round"
            strokeDasharray={Math.PI * 84}
            initial={{ strokeDashoffset: Math.PI * 84 }}
            animate={{
              strokeDashoffset: Math.PI * 84 * (1 - progress / 100),
            }}
            transition={{ duration: 0.5 }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl font-bold text-accent">
            {readyCount}/{totalExpected}
          </span>
        </div>
      </div>

      <div className="text-center">
        <h2 className="text-xl font-bold">Waiting for everyone</h2>
        <p className="text-sm text-text-secondary mt-1">
          {readyCount === totalExpected
            ? "Everyone is ready! Starting..."
            : `${totalExpected - readyCount} more to go`}
        </p>
      </div>

      {/* Member list */}
      <div className="w-full max-w-sm space-y-2">
        {members.map((member, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.1 }}
            className="flex items-center justify-between p-3 rounded-xl bg-bg-secondary border border-glass-border"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center text-sm font-bold text-accent">
                {member.name.charAt(0).toUpperCase()}
              </div>
              <span className="text-sm font-medium text-text-primary">
                {member.name}
              </span>
            </div>
            {member.ready ? (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="w-6 h-6 rounded-full bg-success/20 flex items-center justify-center"
              >
                <svg className="w-3.5 h-3.5 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                </svg>
              </motion.div>
            ) : (
              <div className="w-6 h-6 rounded-full bg-bg-tertiary flex items-center justify-center">
                <motion.div
                  className="w-2 h-2 rounded-full bg-text-tertiary"
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                />
              </div>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
}
