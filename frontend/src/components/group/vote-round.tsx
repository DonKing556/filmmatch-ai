"use client";

import { useState } from "react";
import Image from "next/image";
import { motion } from "framer-motion";
import { posterUrl } from "@/lib/utils";
import { MatchScore } from "@/components/ui/match-score";
import { Button } from "@/components/ui/button";
import type { MovieSummary } from "@/types/api";

interface VoteRoundProps {
  movies: MovieSummary[];
  onVotesComplete: (votes: Record<number, boolean>) => void;
}

export function VoteRound({ movies, onVotesComplete }: VoteRoundProps) {
  const [votes, setVotes] = useState<Record<number, boolean>>({});
  const allVoted = movies.every((m) => votes[m.tmdb_id] !== undefined);

  function toggleVote(tmdbId: number, positive: boolean) {
    setVotes((prev) => ({
      ...prev,
      [tmdbId]: prev[tmdbId] === positive ? undefined! : positive,
    }));
  }

  return (
    <div className="px-6 py-8 space-y-6">
      <div className="text-center">
        <h2 className="text-xl font-bold">Vote on the picks</h2>
        <p className="text-sm text-text-secondary mt-1">
          Thumbs up or down on each recommendation
        </p>
      </div>

      <div className="space-y-3">
        {movies.map((movie, i) => {
          const vote = votes[movie.tmdb_id];
          return (
            <motion.div
              key={movie.tmdb_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="flex items-center gap-4 p-3 rounded-xl bg-bg-secondary border border-glass-border"
            >
              {/* Poster */}
              <div className="relative w-14 h-20 flex-shrink-0 rounded-lg overflow-hidden">
                <Image
                  src={posterUrl(movie.poster_url, "w185")}
                  alt={movie.title}
                  fill
                  className="object-cover"
                />
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-semibold text-text-primary truncate">
                  {movie.title}
                </h3>
                <div className="flex items-center gap-2 mt-0.5">
                  {movie.year && (
                    <span className="text-xs text-text-tertiary">
                      {movie.year}
                    </span>
                  )}
                  {movie.match_score != null && (
                    <MatchScore score={movie.match_score} size="sm" animate={false} />
                  )}
                </div>
              </div>

              {/* Vote buttons */}
              <div className="flex gap-2">
                <motion.button
                  whileTap={{ scale: 0.9 }}
                  onClick={() => toggleVote(movie.tmdb_id, false)}
                  className={`w-10 h-10 rounded-full flex items-center justify-center transition-colors ${
                    vote === false
                      ? "bg-error/20 text-error"
                      : "bg-bg-tertiary text-text-tertiary hover:text-text-secondary"
                  }`}
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76.94m-7 10v5a2 2 0 002 2h.096c.5 0 .905-.405.905-.904 0-.715.211-1.413.608-2.008L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5" />
                  </svg>
                </motion.button>
                <motion.button
                  whileTap={{ scale: 0.9 }}
                  onClick={() => toggleVote(movie.tmdb_id, true)}
                  className={`w-10 h-10 rounded-full flex items-center justify-center transition-colors ${
                    vote === true
                      ? "bg-success/20 text-success"
                      : "bg-bg-tertiary text-text-tertiary hover:text-text-secondary"
                  }`}
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                  </svg>
                </motion.button>
              </div>
            </motion.div>
          );
        })}
      </div>

      <Button
        variant="primary"
        onClick={() => onVotesComplete(votes)}
        disabled={!allVoted}
        className="w-full"
      >
        Submit Votes
      </Button>
    </div>
  );
}
