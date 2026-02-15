"use client";

import { useState } from "react";
import Image from "next/image";
import {
  motion,
  useMotionValue,
  useTransform,
  type PanInfo,
} from "framer-motion";
import { posterUrl, formatRuntime } from "@/lib/utils";
import { MatchScore } from "@/components/ui/match-score";
import type { MovieSummary } from "@/types/api";

interface SwipeCardProps {
  movie: MovieSummary;
  onSwipe: (direction: "left" | "right") => void;
  isTop: boolean;
}

const SWIPE_THRESHOLD = 120;

export function SwipeCard({ movie, onSwipe, isTop }: SwipeCardProps) {
  const x = useMotionValue(0);
  const rotate = useTransform(x, [-300, 0, 300], [-18, 0, 18]);
  const keepOpacity = useTransform(x, [0, SWIPE_THRESHOLD], [0, 1]);
  const rejectOpacity = useTransform(x, [-SWIPE_THRESHOLD, 0], [1, 0]);

  const [exitDirection, setExitDirection] = useState<"left" | "right" | null>(
    null,
  );

  function handleDragEnd(_: unknown, info: PanInfo) {
    const offset = info.offset.x;
    const velocity = info.velocity.x;

    if (Math.abs(offset) > SWIPE_THRESHOLD || Math.abs(velocity) > 500) {
      const direction = offset > 0 ? "right" : "left";
      setExitDirection(direction);
      onSwipe(direction);
    }
  }

  return (
    <motion.div
      className="absolute inset-0"
      style={{ x, rotate, zIndex: isTop ? 10 : 0 }}
      drag={isTop ? "x" : false}
      dragConstraints={{ left: 0, right: 0 }}
      dragElastic={0.9}
      onDragEnd={handleDragEnd}
      initial={{ scale: isTop ? 1 : 0.95, opacity: isTop ? 1 : 0.5 }}
      animate={{
        scale: isTop ? 1 : 0.95,
        opacity: isTop ? 1 : 0.5,
      }}
      exit={{
        x: exitDirection === "right" ? 400 : -400,
        opacity: 0,
        transition: { duration: 0.3 },
      }}
    >
      <div className="relative w-full h-full rounded-2xl overflow-hidden shadow-elevated bg-bg-secondary border border-glass-border">
        {/* Poster */}
        <div className="relative h-[55%]">
          <Image
            src={posterUrl(movie.poster_url)}
            alt={`${movie.title} poster`}
            fill
            className="object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-bg-secondary via-transparent to-transparent" />

          {/* Keep/Reject overlays */}
          <motion.div
            className="absolute inset-0 bg-success/20 flex items-center justify-center"
            style={{ opacity: keepOpacity }}
          >
            <div className="px-6 py-3 border-4 border-success rounded-xl rotate-[-15deg]">
              <span className="text-4xl font-black text-success">KEEP</span>
            </div>
          </motion.div>

          <motion.div
            className="absolute inset-0 bg-error/20 flex items-center justify-center"
            style={{ opacity: rejectOpacity }}
          >
            <div className="px-6 py-3 border-4 border-error rounded-xl rotate-[15deg]">
              <span className="text-4xl font-black text-error">NOPE</span>
            </div>
          </motion.div>
        </div>

        {/* Content */}
        <div className="p-5 space-y-3">
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1 min-w-0">
              <h3 className="text-xl font-bold text-text-primary truncate">
                {movie.title}
              </h3>
              <div className="flex items-center gap-2 mt-1 text-sm text-text-secondary">
                {movie.year && <span>{movie.year}</span>}
                {movie.runtime && (
                  <>
                    <span className="w-1 h-1 rounded-full bg-text-tertiary" />
                    <span>{formatRuntime(movie.runtime)}</span>
                  </>
                )}
              </div>
            </div>
            {movie.match_score != null && (
              <MatchScore score={movie.match_score} size="md" />
            )}
          </div>

          {/* Genres */}
          <div className="flex flex-wrap gap-1.5">
            {movie.genres.slice(0, 4).map((genre) => (
              <span
                key={genre}
                className="px-2.5 py-1 text-xs rounded-full bg-bg-tertiary border border-glass-border text-text-secondary"
              >
                {genre}
              </span>
            ))}
          </div>

          {/* Rationale */}
          {movie.rationale && (
            <p className="text-sm text-text-secondary line-clamp-2">
              {movie.rationale}
            </p>
          )}
        </div>
      </div>
    </motion.div>
  );
}
