"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { MatchScore } from "@/components/ui/match-score";
import { posterUrl } from "@/lib/utils";
import { toast } from "sonner";
import type { MovieSummary } from "@/types/api";

interface DecisionReceiptProps {
  movie: MovieSummary;
  members: string[];
  mode: "solo" | "group";
  moviesConsidered: number;
  onClose: () => void;
}

export function DecisionReceipt({
  movie,
  members,
  mode,
  moviesConsidered,
  onClose,
}: DecisionReceiptProps) {
  const shareText =
    mode === "group"
      ? `${members.slice(0, 3).join(" & ")}${members.length > 3 ? ` + ${members.length - 3} more` : ""} picked "${movie.title}" for movie night with FilmMatch AI!`
      : `I'm watching "${movie.title}" tonight, found with FilmMatch AI!`;

  async function handleShare() {
    if (navigator.share) {
      try {
        await navigator.share({
          title: `FilmMatch: ${movie.title}`,
          text: shareText,
        });
      } catch {
        // User cancelled
      }
    } else {
      try {
        await navigator.clipboard.writeText(shareText);
        toast.success("Copied to clipboard!");
      } catch {
        toast.error("Could not copy text.");
      }
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: "spring", stiffness: 200, damping: 25 }}
      className="mx-auto max-w-sm"
    >
      {/* Receipt card */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#1a1a2e] via-[#16162a] to-[#0f0f1a] border border-glass-border shadow-elevated">
        {/* Decorative gradient strip */}
        <div className="h-1.5 bg-gradient-to-r from-accent via-[#06B6D4] to-accent" />

        <div className="p-6 space-y-5">
          {/* Header */}
          <div className="text-center">
            <p className="text-[10px] font-bold uppercase tracking-[0.3em] text-accent/70">
              FilmMatch AI
            </p>
            <p className="text-[10px] text-text-tertiary mt-0.5">
              Decision Receipt
            </p>
          </div>

          {/* Movie poster + info */}
          <div className="flex gap-4 items-start">
            <div className="relative w-20 h-30 flex-shrink-0 rounded-xl overflow-hidden shadow-lg">
              <Image
                src={posterUrl(movie.poster_url, "w342")}
                alt={movie.title}
                width={80}
                height={120}
                className="object-cover"
              />
            </div>
            <div className="flex-1 min-w-0 space-y-1.5">
              <h3 className="text-lg font-bold text-text-primary leading-tight">
                {movie.title}
              </h3>
              <div className="flex items-center gap-2 text-xs text-text-secondary">
                {movie.year && <span>{movie.year}</span>}
                {movie.genres.length > 0 && (
                  <span>{movie.genres.slice(0, 2).join(", ")}</span>
                )}
              </div>
              {movie.match_score != null && (
                <MatchScore score={movie.match_score} size="sm" />
              )}
            </div>
          </div>

          {/* Dashed divider */}
          <div className="border-t border-dashed border-glass-border" />

          {/* Stats */}
          <div className="grid grid-cols-2 gap-3 text-center">
            <div className="p-2.5 rounded-xl bg-bg-tertiary/50">
              <p className="text-xl font-bold text-accent">
                {moviesConsidered}
              </p>
              <p className="text-[10px] text-text-tertiary">
                Movies Considered
              </p>
            </div>
            <div className="p-2.5 rounded-xl bg-bg-tertiary/50">
              <p className="text-xl font-bold text-accent">
                {members.length}
              </p>
              <p className="text-[10px] text-text-tertiary">
                {mode === "group" ? "Group Members" : "Viewer"}
              </p>
            </div>
          </div>

          {/* Members */}
          {mode === "group" && members.length > 0 && (
            <div className="text-center">
              <p className="text-xs text-text-tertiary">
                Picked by{" "}
                <span className="text-text-secondary font-medium">
                  {members.join(", ")}
                </span>
              </p>
            </div>
          )}

          {/* Rationale snippet */}
          {movie.rationale && (
            <div className="p-3 rounded-xl bg-accent/5 border border-accent/10">
              <p className="text-[10px] font-semibold text-accent mb-1">
                Why this one
              </p>
              <p className="text-xs text-text-secondary leading-relaxed line-clamp-3">
                {movie.rationale}
              </p>
            </div>
          )}

          {/* Dashed divider */}
          <div className="border-t border-dashed border-glass-border" />

          {/* Footer */}
          <p className="text-center text-[9px] text-text-tertiary">
            filmmatch.ai
          </p>
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex gap-3 mt-4">
        <Button variant="primary" onClick={handleShare} className="flex-1">
          Share
        </Button>
        <Button variant="secondary" onClick={onClose}>
          Done
        </Button>
      </div>
    </motion.div>
  );
}
