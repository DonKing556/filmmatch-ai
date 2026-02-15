"use client";

import Image from "next/image";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { MatchScore } from "@/components/ui/match-score";
import { backdropUrl, formatRuntime } from "@/lib/utils";
import type { MovieSummary } from "@/types/api";

interface HeroPickProps {
  movie: MovieSummary;
  onDetails: () => void;
  onWatchlist: () => void;
}

export function HeroPick({ movie, onDetails, onWatchlist }: HeroPickProps) {
  const backdrop = backdropUrl(movie.backdrop_url);

  return (
    <div className="relative h-[70vh] min-h-[500px] w-full overflow-hidden">
      {/* Backdrop image */}
      {backdrop && (
        <Image
          src={backdrop}
          alt=""
          fill
          className="object-cover"
          priority
          role="presentation"
        />
      )}

      {/* Gradient overlays */}
      <div className="absolute inset-0 bg-gradient-to-t from-bg-primary via-bg-primary/60 to-bg-primary/20" />
      <div className="absolute inset-0 bg-gradient-to-r from-bg-primary/80 to-transparent" />

      {/* Content */}
      <div className="absolute bottom-0 left-0 right-0 p-6 md:p-12 space-y-4">
        {/* Best Pick badge */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-accent/20 border border-accent/30"
        >
          <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
          <span className="text-sm font-semibold text-accent">Best Pick</span>
        </motion.div>

        {/* Title */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-4xl md:text-6xl font-bold text-white max-w-2xl"
        >
          {movie.title}
        </motion.h1>

        {/* Meta */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex items-center gap-4 text-text-secondary"
        >
          {movie.match_score != null && (
            <MatchScore score={movie.match_score} size="lg" />
          )}
          <div className="flex items-center gap-3 text-sm">
            {movie.year && <span>{movie.year}</span>}
            {movie.runtime && (
              <>
                <span className="w-1 h-1 rounded-full bg-text-tertiary" />
                <span>{formatRuntime(movie.runtime)}</span>
              </>
            )}
            {movie.genres.length > 0 && (
              <>
                <span className="w-1 h-1 rounded-full bg-text-tertiary" />
                <span>{movie.genres.slice(0, 3).join(", ")}</span>
              </>
            )}
          </div>
        </motion.div>

        {/* Rationale */}
        {movie.rationale && (
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-base text-text-secondary max-w-xl whitespace-pre-line"
          >
            {movie.rationale}
          </motion.p>
        )}

        {/* Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="flex gap-3 pt-2"
        >
          <Button size="lg" variant="primary" onClick={onDetails}>
            View Details
          </Button>
          <Button size="lg" variant="secondary" onClick={onWatchlist}>
            Add to Watchlist
          </Button>
        </motion.div>
      </div>
    </div>
  );
}
