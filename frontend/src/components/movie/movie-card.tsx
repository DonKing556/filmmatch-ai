"use client";

import { useState } from "react";
import Image from "next/image";
import { motion } from "framer-motion";
import { cn, posterUrl, formatRuntime } from "@/lib/utils";
import { MatchScore } from "@/components/ui/match-score";
import type { MovieSummary } from "@/types/api";

interface MovieCardProps {
  movie: MovieSummary;
  onClick?: () => void;
  rank?: number;
  className?: string;
}

export function MovieCard({ movie, onClick, rank, className }: MovieCardProps) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <motion.article
      layout
      className={cn(
        "relative flex-shrink-0 cursor-pointer group",
        "w-[160px] sm:w-[180px] md:w-[200px]",
        className
      )}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      onClick={onClick}
      whileHover={{ scale: 1.05, zIndex: 10 }}
      transition={{ duration: 0.2 }}
    >
      {/* Poster */}
      <div className="relative aspect-[2/3] rounded-xl overflow-hidden shadow-card">
        <Image
          src={posterUrl(movie.poster_url, "w342")}
          alt={`${movie.title} poster`}
          fill
          sizes="(max-width: 640px) 160px, (max-width: 768px) 180px, 200px"
          className="object-cover transition-transform duration-300 group-hover:scale-105"
        />

        {/* Gradient overlay on hover */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: isHovered ? 1 : 0 }}
          className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"
        />

        {/* Rank badge */}
        {rank && (
          <div className="absolute top-2 left-2 w-7 h-7 rounded-lg bg-accent flex items-center justify-center text-xs font-bold text-white">
            {rank}
          </div>
        )}

        {/* Match score */}
        {movie.match_score != null && (
          <div className="absolute top-2 right-2">
            <MatchScore score={movie.match_score} size="sm" animate={false} />
          </div>
        )}

        {/* Hover details */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: isHovered ? 1 : 0, y: isHovered ? 0 : 10 }}
          className="absolute bottom-0 left-0 right-0 p-3 space-y-1"
        >
          <div className="flex items-center gap-2 text-xs text-text-secondary">
            {movie.year && <span>{movie.year}</span>}
            {movie.runtime && (
              <>
                <span className="w-1 h-1 rounded-full bg-text-tertiary" />
                <span>{formatRuntime(movie.runtime)}</span>
              </>
            )}
          </div>
          {movie.genres.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {movie.genres.slice(0, 2).map((genre) => (
                <span
                  key={genre}
                  className="px-1.5 py-0.5 text-[10px] rounded-md bg-white/10 text-text-secondary"
                >
                  {genre}
                </span>
              ))}
            </div>
          )}
        </motion.div>
      </div>

      {/* Title */}
      <div className="mt-2 px-0.5">
        <h3 className="text-sm font-medium text-text-primary truncate">
          {movie.title}
        </h3>
        {movie.vote_average > 0 && (
          <p className="text-xs text-text-tertiary mt-0.5">
            {movie.vote_average.toFixed(1)} / 10
          </p>
        )}
      </div>
    </motion.article>
  );
}
