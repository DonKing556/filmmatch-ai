"use client";

import { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { BottomNav, DesktopNav } from "@/components/layout/navigation";

function JoinContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [code, setCode] = useState(searchParams.get("code") ?? "");
  const [isJoining, setIsJoining] = useState(false);

  async function handleJoin() {
    if (!code.trim()) return;
    setIsJoining(true);
    // In a real implementation, this would call the API
    // For now, redirect to the group page
    router.push("/group");
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="px-6 py-12 space-y-8"
    >
      <div className="text-center">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-accent/10 flex items-center justify-center">
          <svg className="w-8 h-8 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold">Join a Group Session</h1>
        <p className="text-text-secondary mt-2">
          Enter the code shared by your friend to join their movie night.
        </p>
      </div>

      <div className="max-w-xs mx-auto space-y-4">
        <Input
          value={code}
          onChange={(e) => setCode(e.target.value.toUpperCase())}
          placeholder="Enter 6-digit code"
          className="text-center text-xl tracking-[0.2em] font-mono"
        />

        <Button
          variant="primary"
          onClick={handleJoin}
          disabled={code.trim().length < 4}
          loading={isJoining}
          className="w-full"
        >
          Join Session
        </Button>

        <Button
          variant="ghost"
          onClick={() => router.push("/group")}
          className="w-full"
        >
          Create Your Own
        </Button>
      </div>
    </motion.div>
  );
}

export default function JoinPage() {
  return (
    <>
      <DesktopNav />
      <div className="max-w-2xl mx-auto min-h-screen flex items-center justify-center">
        <Suspense fallback={<div className="text-text-secondary">Loading...</div>}>
          <JoinContent />
        </Suspense>
      </div>
      <BottomNav />
    </>
  );
}
