"use client";

import dynamic from "next/dynamic";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { ScrollRow } from "@/components/ui/scroll-row";
import { MovieCard } from "@/components/movie/movie-card";
import { MovieCardSkeleton } from "@/components/ui/skeleton";
import { Footer } from "@/components/layout/footer";
import { BottomNav, DesktopNav } from "@/components/layout/navigation";
import { useUIStore } from "@/stores/ui";
import { movies } from "@/lib/api";
import type { TrendingMovie, MovieSummary } from "@/types/api";

const MovieDetail = dynamic(
  () =>
    import("@/components/movie/movie-detail").then((m) => ({
      default: m.MovieDetail,
    })),
  { ssr: false },
);

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
              {trending.map((movie, i) => (
                <MovieCard
                  key={movie.tmdb_id}
                  movie={trendingToSummary(movie)}
                  onClick={() => openDetail(trendingToSummary(movie))}
                  priority={i < 4}
                />
              ))}
            </ScrollRow>
          )
        )}
      </section>

      {/* Feature Showcase: Solo Mode */}
      <section className="py-20 px-6 overflow-hidden">
        <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-12 items-center">
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
            className="space-y-5"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-accent/10 border border-accent/20">
              <span className="w-2 h-2 rounded-full bg-accent" />
              <span className="text-xs font-semibold text-accent uppercase tracking-wider">Solo Mode</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold">
              Your personal film concierge
            </h2>
            <p className="text-text-secondary text-lg">
              Tell us your mood, pick your genres, and get AI-ranked picks with
              match scores. Swipe to narrow down until you find the one.
            </p>
            <ul className="space-y-3">
              {["3-step preference wizard", "AI match scoring (0-10)", "Swipe to narrow down", "Natural language input"].map((item) => (
                <li key={item} className="flex items-center gap-3 text-text-secondary">
                  <div className="w-5 h-5 rounded-full bg-accent/10 flex items-center justify-center flex-shrink-0">
                    <svg className="w-3 h-3 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  {item}
                </li>
              ))}
            </ul>
            <Button variant="primary" onClick={() => router.push("/solo")}>
              Try Solo Mode
            </Button>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="relative"
          >
            <div className="relative rounded-2xl bg-gradient-to-br from-accent/10 to-accent-secondary/10 border border-glass-border p-8 aspect-square flex items-center justify-center">
              <div className="space-y-4 w-full max-w-xs">
                {["Action", "Sci-Fi", "Thriller"].map((genre, i) => (
                  <motion.div
                    key={genre}
                    initial={{ opacity: 0, scale: 0.8 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.4 + i * 0.15 }}
                    className="px-4 py-2 rounded-full bg-accent/20 border border-accent text-accent text-sm font-medium text-center"
                  >
                    {genre}
                  </motion.div>
                ))}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.9 }}
                  className="mt-6 p-4 rounded-xl bg-bg-secondary border border-glass-border"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-14 rounded-lg bg-accent/20" />
                    <div className="flex-1 space-y-1.5">
                      <div className="h-3 w-24 bg-bg-tertiary rounded" />
                      <div className="h-2 w-16 bg-bg-tertiary rounded" />
                    </div>
                    <div className="text-lg font-bold text-success">9.2</div>
                  </div>
                </motion.div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Feature Showcase: Group Mode */}
      <section className="py-20 px-6 bg-bg-secondary/50">
        <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-12 items-center">
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="order-2 md:order-1 relative"
          >
            <div className="relative rounded-2xl bg-gradient-to-br from-accent-secondary/10 to-accent/10 border border-glass-border p-8 aspect-square flex items-center justify-center">
              <div className="space-y-3 w-full max-w-xs">
                {["Alex", "Jordan", "Sam"].map((name, i) => (
                  <motion.div
                    key={name}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.4 + i * 0.15 }}
                    className="flex items-center gap-3 p-3 rounded-xl bg-bg-secondary border border-glass-border"
                  >
                    <div className="w-8 h-8 rounded-full bg-accent-secondary/20 flex items-center justify-center text-xs font-bold text-accent-secondary">
                      {name[0]}
                    </div>
                    <span className="text-sm font-medium flex-1">{name}</span>
                    <div className="w-5 h-5 rounded-full bg-success/20 flex items-center justify-center">
                      <svg className="w-3 h-3 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                  </motion.div>
                ))}
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.9 }}
                  className="text-center pt-2"
                >
                  <span className="text-sm text-accent-secondary font-semibold">
                    87% Group Match
                  </span>
                </motion.div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
            className="order-1 md:order-2 space-y-5"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-accent-secondary/10 border border-accent-secondary/20">
              <span className="w-2 h-2 rounded-full bg-accent-secondary" />
              <span className="text-xs font-semibold text-accent-secondary uppercase tracking-wider">Group Mode</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold">
              Movie night, solved
            </h2>
            <p className="text-text-secondary text-lg">
              No more arguing over what to watch. Everyone submits their
              preferences, and the AI finds what works for the whole group.
            </p>
            <ul className="space-y-3">
              {["Share a code to invite friends", "Each person picks genres & mood", "AI finds the group overlap", "Vote on the top picks"].map((item) => (
                <li key={item} className="flex items-center gap-3 text-text-secondary">
                  <div className="w-5 h-5 rounded-full bg-accent-secondary/10 flex items-center justify-center flex-shrink-0">
                    <svg className="w-3 h-3 text-accent-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  {item}
                </li>
              ))}
            </ul>
            <Button variant="secondary" onClick={() => router.push("/group")}>
              Start a Group
            </Button>
          </motion.div>
        </div>
      </section>

      {/* Feature Showcase: AI Engine */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center space-y-12">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
            className="space-y-4"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-glass-border">
              <span className="w-2 h-2 rounded-full bg-gradient-to-r from-accent to-accent-secondary" />
              <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Powered by Claude AI</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold">
              Smarter than a search bar
            </h2>
            <p className="text-text-secondary text-lg max-w-2xl mx-auto">
              We search real movie databases, then let AI rank and explain
              why each pick matches your taste. No hallucinated titles,
              no random guesses.
            </p>
          </motion.div>

          <div className="grid sm:grid-cols-3 gap-6">
            {[
              {
                icon: (
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                ),
                title: "500K+ Movies",
                desc: "Powered by TMDB with real-time data",
              },
              {
                icon: (
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                ),
                title: "AI Reasoning",
                desc: "Every pick comes with a personalized explanation",
              },
              {
                icon: (
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                ),
                title: "0% Hallucination",
                desc: "Every recommendation is a verified, real film",
              },
            ].map((item, i) => (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15 }}
                className="p-6 rounded-2xl bg-bg-secondary border border-glass-border space-y-3"
              >
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent/10 to-accent-secondary/10 flex items-center justify-center text-accent">
                  {item.icon}
                </div>
                <h3 className="text-lg font-semibold">{item.title}</h3>
                <p className="text-sm text-text-secondary">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-16 px-6 bg-bg-secondary/30">
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

      {/* CTA */}
      <section className="py-20 px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-2xl mx-auto text-center space-y-6"
        >
          <h2 className="text-3xl md:text-4xl font-bold">
            Ready to find your next favorite film?
          </h2>
          <p className="text-text-secondary text-lg">
            It takes less than 30 seconds. No account required.
          </p>
          <Button
            size="lg"
            variant="primary"
            onClick={() => router.push("/solo")}
            className="text-base px-10"
          >
            Get Started
          </Button>
        </motion.div>
      </section>

      <Footer />

      <MovieDetail
        movie={selectedMovie}
        open={detailOpen}
        onClose={closeDetail}
      />

      <BottomNav />
    </>
  );
}
