"use client";

import Image from "next/image";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { MatchScore } from "@/components/ui/match-score";
import { cn, posterUrl, backdropUrl, formatRuntime } from "@/lib/utils";
import type { MovieSummary } from "@/types/api";

interface MovieDetailProps {
  movie: MovieSummary | null;
  open: boolean;
  onClose: () => void;
}

export function MovieDetail({ movie, open, onClose }: MovieDetailProps) {
  if (!movie) return null;

  const backdrop = backdropUrl(movie.backdrop_url);

  return (
    <Modal open={open} onClose={onClose}>
      <div className="relative">
        {/* Backdrop */}
        {backdrop && (
          <div className="relative h-[200px] sm:h-[300px] overflow-hidden rounded-t-2xl">
            <Image
              src={backdrop}
              alt=""
              fill
              className="object-cover"
              role="presentation"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-bg-secondary via-bg-secondary/50 to-transparent" />
          </div>
        )}

        {/* Content */}
        <div className={cn("p-6 space-y-5", backdrop ? "-mt-20 relative" : "")}>
          <div className="flex gap-5">
            {/* Poster */}
            <div className="relative w-28 h-42 flex-shrink-0 rounded-xl overflow-hidden shadow-elevated">
              <Image
                src={posterUrl(movie.poster_url, "w342")}
                alt={`${movie.title} poster`}
                width={112}
                height={168}
                className="object-cover"
              />
            </div>

            {/* Info */}
            <div className="flex-1 min-w-0 space-y-2">
              <h2 className="text-2xl font-bold text-text-primary">
                {movie.title}
              </h2>
              <div className="flex items-center gap-3 text-sm text-text-secondary flex-wrap">
                {movie.year && <span>{movie.year}</span>}
                {movie.runtime && <span>{formatRuntime(movie.runtime)}</span>}
                {movie.vote_average > 0 && (
                  <span>{movie.vote_average.toFixed(1)} / 10</span>
                )}
              </div>

              {/* Genres */}
              <div className="flex flex-wrap gap-1.5">
                {movie.genres.map((genre) => (
                  <span
                    key={genre}
                    className="px-2.5 py-1 text-xs rounded-full bg-bg-tertiary border border-glass-border text-text-secondary"
                  >
                    {genre}
                  </span>
                ))}
              </div>

              {/* Match score */}
              {movie.match_score != null && (
                <div className="flex items-center gap-2">
                  <MatchScore score={movie.match_score} size="md" />
                  <span className="text-sm text-text-secondary">match</span>
                </div>
              )}
            </div>
          </div>

          {/* Rationale */}
          {movie.rationale && (
            <div className="p-4 rounded-xl bg-accent/5 border border-accent/10">
              <p className="text-sm font-medium text-accent mb-1">Why we picked this</p>
              <p className="text-sm text-text-secondary whitespace-pre-line">
                {movie.rationale}
              </p>
            </div>
          )}

          {/* Synopsis */}
          {movie.overview && (
            <div>
              <h3 className="text-sm font-semibold text-text-primary mb-2">Synopsis</h3>
              <p className="text-sm text-text-secondary leading-relaxed">
                {movie.overview}
              </p>
            </div>
          )}

          {/* Cast & Crew */}
          <div className="grid grid-cols-2 gap-4">
            {movie.directors.length > 0 && (
              <div>
                <h4 className="text-xs font-semibold text-text-tertiary uppercase tracking-wider mb-1">
                  Director
                </h4>
                <p className="text-sm text-text-primary">
                  {movie.directors.join(", ")}
                </p>
              </div>
            )}
            {movie.cast.length > 0 && (
              <div>
                <h4 className="text-xs font-semibold text-text-tertiary uppercase tracking-wider mb-1">
                  Cast
                </h4>
                <p className="text-sm text-text-primary">
                  {movie.cast.slice(0, 4).join(", ")}
                </p>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <Button variant="primary" size="md" className="flex-1">
              Add to Watchlist
            </Button>
            <Button variant="secondary" size="md">
              Not Interested
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  );
}
