"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { users } from "@/lib/api";
import { MovieDetail } from "@/components/movie/movie-detail";
import { BottomNav, DesktopNav } from "@/components/layout/navigation";
import { useUIStore } from "@/stores/ui";
import { posterUrl } from "@/lib/utils";
import { MovieCardSkeleton } from "@/components/ui/skeleton";
import Image from "next/image";

export default function WatchlistPage() {
  const { selectedMovie, detailOpen, openDetail, closeDetail } = useUIStore();

  const { data: history, isLoading } = useQuery({
    queryKey: ["watchHistory"],
    queryFn: users.watchHistory,
  });

  const watchlistItems = history?.filter((h) => h.status === "watchlist") ?? [];

  return (
    <>
      <DesktopNav />

      <div className="max-w-4xl mx-auto px-6 py-8 min-h-screen">
        <h1 className="text-2xl font-bold mb-6">My Watchlist</h1>

        {isLoading ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <MovieCardSkeleton key={i} />
            ))}
          </div>
        ) : watchlistItems.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-24 text-center">
            <div className="w-16 h-16 rounded-full bg-bg-tertiary flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-text-tertiary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
              </svg>
            </div>
            <h2 className="text-lg font-semibold text-text-secondary mb-1">
              No movies yet
            </h2>
            <p className="text-sm text-text-tertiary">
              Movies you save will appear here.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {watchlistItems.map((item, i) => (
              <motion.div
                key={item.tmdb_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className="cursor-pointer group"
                onClick={() =>
                  openDetail({
                    tmdb_id: item.tmdb_id,
                    title: item.title ?? "Unknown",
                    year: null,
                    genres: [],
                    vote_average: 0,
                    runtime: null,
                    poster_url: item.poster_url,
                    backdrop_url: null,
                    overview: "",
                    directors: [],
                    cast: [],
                    match_score: null,
                    rationale: "",
                  })
                }
              >
                <div className="relative aspect-[2/3] rounded-xl overflow-hidden shadow-card">
                  <Image
                    src={posterUrl(item.poster_url)}
                    alt={item.title ?? "Movie poster"}
                    fill
                    sizes="(max-width: 640px) 50vw, (max-width: 768px) 33vw, 25vw"
                    className="object-cover transition-transform duration-300 group-hover:scale-105"
                  />
                </div>
                {item.title && (
                  <p className="mt-2 text-sm font-medium text-text-primary truncate">
                    {item.title}
                  </p>
                )}
              </motion.div>
            ))}
          </div>
        )}
      </div>

      <MovieDetail
        movie={selectedMovie}
        open={detailOpen}
        onClose={closeDetail}
      />

      <BottomNav />
    </>
  );
}
