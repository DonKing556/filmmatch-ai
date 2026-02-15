"use client";

import { useState, useCallback } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { SwipeCard } from "@/components/movie/swipe-card";
import { Button } from "@/components/ui/button";
import { MatchScore } from "@/components/ui/match-score";
import { posterUrl } from "@/lib/utils";
import Image from "next/image";
import type { MovieSummary } from "@/types/api";

interface NarrowDownProps {
  movies: MovieSummary[];
  onComplete: (kept: MovieSummary[], rejected: MovieSummary[]) => void;
  onRefine: (
    kept: number[],
    rejected: number[],
  ) => Promise<MovieSummary | null>;
}

export function NarrowDown({ movies, onComplete, onRefine }: NarrowDownProps) {
  const [deck, setDeck] = useState<MovieSummary[]>([...movies]);
  const [kept, setKept] = useState<MovieSummary[]>([]);
  const [rejected, setRejected] = useState<MovieSummary[]>([]);
  const [finalPick, setFinalPick] = useState<MovieSummary | null>(null);
  const [isRefining, setIsRefining] = useState(false);

  const currentCard = deck[0];
  const nextCard = deck[1];

  const handleSwipe = useCallback(
    (direction: "left" | "right") => {
      const movie = deck[0];
      if (!movie) return;

      if (direction === "right") {
        setKept((prev) => [...prev, movie]);
      } else {
        setRejected((prev) => [...prev, movie]);
      }

      setDeck((prev) => prev.slice(1));
    },
    [deck],
  );

  const handleButtonSwipe = useCallback(
    (direction: "left" | "right") => {
      handleSwipe(direction);
    },
    [handleSwipe],
  );

  async function handleFinish() {
    setIsRefining(true);
    const keptIds = kept.map((m) => m.tmdb_id);
    const rejectedIds = rejected.map((m) => m.tmdb_id);
    const result = await onRefine(keptIds, rejectedIds);
    if (result) {
      setFinalPick(result);
    } else {
      onComplete(kept, rejected);
    }
    setIsRefining(false);
  }

  // All cards swiped - show summary or get final pick
  if (deck.length === 0 && !finalPick) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] px-6 gap-6">
        <h2 className="text-xl font-bold text-center">
          {kept.length > 0 ? "Nice choices!" : "Let\u2019s try different options"}
        </h2>

        {kept.length > 0 && (
          <div className="flex gap-2 justify-center flex-wrap">
            {kept.map((m) => (
              <div
                key={m.tmdb_id}
                className="w-16 h-24 rounded-lg overflow-hidden border border-success/30"
              >
                <Image
                  src={posterUrl(m.poster_url, "w185")}
                  alt={m.title}
                  width={64}
                  height={96}
                  className="object-cover w-full h-full"
                />
              </div>
            ))}
          </div>
        )}

        <p className="text-text-secondary text-center">
          You kept {kept.length} and passed on {rejected.length}.
          {kept.length > 1 && " Let the AI find the best one for you."}
        </p>

        <Button
          variant="primary"
          size="lg"
          onClick={handleFinish}
          loading={isRefining}
          className="w-full max-w-xs"
        >
          {kept.length > 1 ? "Find My Perfect Pick" : "Done"}
        </Button>
      </div>
    );
  }

  // Final reveal
  if (finalPick) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] px-6 gap-6">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: "spring", stiffness: 200, damping: 20 }}
          className="text-center space-y-4"
        >
          <p className="text-sm font-semibold text-accent uppercase tracking-wider">
            Your Perfect Pick
          </p>

          <div className="relative w-48 h-72 mx-auto rounded-2xl overflow-hidden shadow-elevated">
            <Image
              src={posterUrl(finalPick.poster_url)}
              alt={finalPick.title}
              fill
              className="object-cover"
            />
          </div>

          <h2 className="text-2xl font-bold">{finalPick.title}</h2>

          {finalPick.match_score != null && (
            <div className="flex justify-center">
              <MatchScore score={finalPick.match_score} size="lg" />
            </div>
          )}

          {finalPick.rationale && (
            <p className="text-sm text-text-secondary max-w-sm mx-auto">
              {finalPick.rationale}
            </p>
          )}

          <Button
            variant="primary"
            size="lg"
            onClick={() => onComplete(kept, rejected)}
            className="mt-4"
          >
            View Full Details
          </Button>
        </motion.div>
      </div>
    );
  }

  // Swipe deck
  return (
    <div className="flex flex-col items-center px-6 py-8 gap-6">
      <div className="text-center">
        <h2 className="text-xl font-bold">Narrow it down</h2>
        <p className="text-sm text-text-secondary mt-1">
          Swipe right to keep, left to pass ({deck.length} remaining)
        </p>
      </div>

      {/* Card stack */}
      <div className="relative w-full max-w-sm aspect-[3/4]">
        <AnimatePresence>
          {nextCard && (
            <SwipeCard
              key={nextCard.tmdb_id}
              movie={nextCard}
              onSwipe={() => {}}
              isTop={false}
            />
          )}
          {currentCard && (
            <SwipeCard
              key={currentCard.tmdb_id}
              movie={currentCard}
              onSwipe={handleSwipe}
              isTop
            />
          )}
        </AnimatePresence>
      </div>

      {/* Action buttons */}
      <div className="flex items-center gap-6">
        <motion.button
          whileTap={{ scale: 0.9 }}
          onClick={() => handleButtonSwipe("left")}
          aria-label={`Pass on ${currentCard?.title ?? "this movie"}`}
          className="w-14 h-14 rounded-full bg-error/10 border border-error/20 flex items-center justify-center text-error"
        >
          <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </motion.button>

        <motion.button
          whileTap={{ scale: 0.9 }}
          onClick={() => handleButtonSwipe("right")}
          aria-label={`Keep ${currentCard?.title ?? "this movie"}`}
          className="w-14 h-14 rounded-full bg-success/10 border border-success/20 flex items-center justify-center text-success"
        >
          <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
        </motion.button>
      </div>

      {/* Progress */}
      <p className="sr-only" aria-live="polite">
        {deck.length} movies remaining, {kept.length} kept, {rejected.length} passed
      </p>
      <div className="flex gap-1" aria-hidden="true">
        {movies.map((m) => {
          const isKept = kept.some((k) => k.tmdb_id === m.tmdb_id);
          const isRejected = rejected.some((r) => r.tmdb_id === m.tmdb_id);
          return (
            <div
              key={m.tmdb_id}
              className={`w-2 h-2 rounded-full transition-colors ${
                isKept
                  ? "bg-success"
                  : isRejected
                    ? "bg-error"
                    : "bg-bg-tertiary"
              }`}
            />
          );
        })}
      </div>
    </div>
  );
}
