"use client";

import Image from "next/image";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { MatchScore } from "@/components/ui/match-score";
import { cn, posterUrl, backdropUrl, formatRuntime } from "@/lib/utils";
import { users } from "@/lib/api";
import { toast } from "sonner";
import type { MovieSummary } from "@/types/api";

const STREAMING_SERVICES: Record<string, { label: string; color: string }> = {
  netflix: { label: "Netflix", color: "#E50914" },
  prime: { label: "Prime Video", color: "#00A8E1" },
  disney: { label: "Disney+", color: "#113CCF" },
  hulu: { label: "Hulu", color: "#1CE783" },
  hbo: { label: "Max", color: "#002BE7" },
  apple: { label: "Apple TV+", color: "#555555" },
  peacock: { label: "Peacock", color: "#000000" },
  paramount: { label: "Paramount+", color: "#0064FF" },
};

interface MovieDetailProps {
  movie: MovieSummary | null;
  open: boolean;
  onClose: () => void;
  streamingServices?: string[];
}

export function MovieDetail({
  movie,
  open,
  onClose,
  streamingServices,
}: MovieDetailProps) {
  if (!movie) return null;

  const backdrop = backdropUrl(movie.backdrop_url);

  async function handleWatchlist() {
    if (!movie) return;
    try {
      await users.addToWatchlist(movie.tmdb_id);
      toast.success("Added to watchlist!");
    } catch {
      toast.error("Could not add to watchlist.");
    }
  }

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

          {/* Where to Watch */}
          {streamingServices && streamingServices.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-text-primary mb-3">
                Where to Watch
              </h3>
              <div className="flex flex-wrap gap-2">
                {streamingServices.map((serviceId) => {
                  const service = STREAMING_SERVICES[serviceId];
                  if (!service) return null;
                  return (
                    <div
                      key={serviceId}
                      className="flex items-center gap-2 px-3 py-2 rounded-lg bg-bg-tertiary border border-glass-border"
                    >
                      <div
                        className="w-6 h-6 rounded flex items-center justify-center text-white text-[10px] font-bold"
                        style={{ backgroundColor: service.color }}
                      >
                        {service.label[0]}
                      </div>
                      <span className="text-xs font-medium text-text-secondary">
                        {service.label}
                      </span>
                    </div>
                  );
                })}
              </div>
              <p className="text-[10px] text-text-tertiary mt-2">
                Availability may vary by region.
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
            <Button variant="primary" size="md" className="flex-1" onClick={handleWatchlist}>
              Add to Watchlist
            </Button>
            <Button variant="secondary" size="md" onClick={onClose}>
              Close
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  );
}
