"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

interface ShareCodeProps {
  joinCode: string;
  groupId?: string;
}

export function ShareCode({ joinCode }: ShareCodeProps) {
  const [copied, setCopied] = useState(false);

  const shareUrl =
    typeof window !== "undefined"
      ? `${window.location.origin}/group/join?code=${joinCode}`
      : "";

  async function copyCode() {
    try {
      await navigator.clipboard.writeText(joinCode);
      setCopied(true);
      toast.success("Code copied!");
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error("Could not copy code.");
    }
  }

  async function copyLink() {
    try {
      await navigator.clipboard.writeText(shareUrl);
      toast.success("Link copied!");
    } catch {
      toast.error("Could not copy link.");
    }
  }

  async function nativeShare() {
    if (navigator.share) {
      try {
        await navigator.share({
          title: "Join my FilmMatch session!",
          text: `Join my movie night with code: ${joinCode}`,
          url: shareUrl,
        });
      } catch {
        // User cancelled
      }
    } else {
      copyLink();
    }
  }

  return (
    <div className="space-y-6">
      {/* Code display */}
      <div className="text-center">
        <p className="text-sm text-text-secondary mb-3">Share this code</p>
        <motion.button
          whileTap={{ scale: 0.98 }}
          onClick={copyCode}
          className="inline-flex items-center gap-3 px-8 py-4 rounded-2xl bg-bg-secondary border-2 border-dashed border-accent/30 hover:border-accent/50 transition-colors"
        >
          <span className="text-3xl font-mono font-bold tracking-[0.3em] text-accent">
            {joinCode}
          </span>
          <svg
            className={`w-5 h-5 transition-colors ${copied ? "text-success" : "text-text-tertiary"}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            {copied ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            )}
          </svg>
        </motion.button>
      </div>

      {/* QR code placeholder */}
      <div className="flex justify-center">
        <div className="w-48 h-48 rounded-2xl bg-white p-4 flex items-center justify-center">
          <div className="w-full h-full bg-bg-secondary rounded-lg flex items-center justify-center">
            <div className="text-center">
              <svg className="w-12 h-12 mx-auto text-text-tertiary mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
              </svg>
              <p className="text-xs text-text-tertiary">QR Code</p>
            </div>
          </div>
        </div>
      </div>

      {/* Share buttons */}
      <div className="flex gap-3">
        <Button variant="primary" onClick={nativeShare} className="flex-1">
          Share Link
        </Button>
        <Button variant="secondary" onClick={copyLink}>
          Copy Link
        </Button>
      </div>
    </div>
  );
}
