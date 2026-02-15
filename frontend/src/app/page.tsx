"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { ScrollRow } from "@/components/ui/scroll-row";
import { MovieCard } from "@/components/movie/movie-card";
import { MovieDetail } from "@/components/movie/movie-detail";
import { MovieCardSkeleton } from "@/components/ui/skeleton";
import { BottomNav, DesktopNav } from "@/components/layout/navigation";
import { useUIStore } from "@/stores/ui";
import { movies } from "@/lib/api";
import type { TrendingMovie, MovieSummary } from "@/types/api";

function trendingToSummary(t: TrendingMovie): MovieSummary {
  return {
    ...t,
    runtime: null,
    directors: [],
    cast: [],
    match_score: null,
    rationale: "",
  };
}

export default function HomePage() {
  const router = useRouter();
  const { selectedMovie, detailOpen, openDetail, closeDetail } = useUIStore();

  const { data: trending, isLoading } = useQuery({
    queryKey: ["trending"],
    queryFn: movies.trending,
  });

  return (
    <>
      <DesktopNav />

      {/* Hero Section */}
      <section className="relative min-h-[80vh] flex items-center justify-center overflow-hidden px-6">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-b from-accent/5 via-transparent to-transparent" />
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-accent/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent-secondary/10 rounded-full blur-3xl" />

        <div className="relative text-center max-w-3xl mx-auto space-y-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          >
            <h1 className="text-5xl md:text-7xl font-bold leading-tight">
              <span className="bg-gradient-to-r from-accent to-accent-secondary bg-clip-text text-transparent">
                AI-Powered
              </span>
              <br />
              Movie Picks
            </h1>
          </motion.div>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
            className="text-lg md:text-xl text-text-secondary max-w-xl mx-auto"
          >
            Tell us your mood, genre preferences, and who you&apos;re watching
            with. Our AI finds the perfect film in seconds.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <Button
              size="lg"
              variant="primary"
              onClick={() => router.push("/solo")}
              className="text-base px-8"
            >
              Find My Movie
            </Button>
            <Button
              size="lg"
              variant="secondary"
              onClick={() => router.push("/group")}
              className="text-base px-8"
            >
              Group Watch
            </Button>
          </motion.div>
        </div>
      </section>

      {/* Trending Section */}
      <section className="py-12">
        {isLoading ? (
          <div className="px-6">
            <div className="h-7 w-40 bg-bg-tertiary rounded-lg mb-4 animate-pulse" />
            <div className="flex gap-3 overflow-hidden">
              {Array.from({ length: 6 }).map((_, i) => (
                <MovieCardSkeleton key={i} />
              ))}
            </div>
          </div>
        ) : (
          trending &&
          trending.length > 0 && (
            <ScrollRow title="Trending Now">
              {trending.map((movie) => (
                <MovieCard
                  key={movie.tmdb_id}
                  movie={trendingToSummary(movie)}
                  onClick={() => openDetail(trendingToSummary(movie))}
                />
              ))}
            </ScrollRow>
          )
        )}
      </section>

      {/* How it works */}
      <section className="py-16 px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl md:text-3xl font-bold text-center mb-12">
            How It Works
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: "1",
                title: "Tell Us Your Vibe",
                desc: "Pick genres, set your mood, and share any preferences.",
              },
              {
                step: "2",
                title: "AI Matches Films",
                desc: "Our engine searches thousands of movies and scores them for you.",
              },
              {
                step: "3",
                title: "Watch & Enjoy",
                desc: "Get your top pick with a match score and streaming info.",
              },
            ].map((item, i) => (
              <motion.div
                key={item.step}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15 }}
                className="text-center space-y-3"
              >
                <div className="w-12 h-12 mx-auto rounded-full bg-accent/10 border border-accent/20 flex items-center justify-center text-accent font-bold">
                  {item.step}
                </div>
                <h3 className="text-lg font-semibold">{item.title}</h3>
                <p className="text-sm text-text-secondary">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <MovieDetail
        movie={selectedMovie}
        open={detailOpen}
        onClose={closeDetail}
      />

      <BottomNav />
    </>
  );
}
