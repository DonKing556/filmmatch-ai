"use client";

import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { ChipGroup } from "@/components/ui/chip";
import { Textarea } from "@/components/ui/input";
import { StepIndicator } from "@/components/ui/step-indicator";
import { AILoading } from "@/components/movie/ai-loading";
import { HeroPick } from "@/components/movie/hero-pick";
import { MovieCard } from "@/components/movie/movie-card";
import { MovieDetail } from "@/components/movie/movie-detail";
import { ScrollRow } from "@/components/ui/scroll-row";
import { BottomNav, DesktopNav } from "@/components/layout/navigation";
import { usePreferencesStore } from "@/stores/preferences";
import { useUIStore } from "@/stores/ui";
import { recommend, users } from "@/lib/api";
import { toast } from "sonner";

const GENRES = [
  "Action", "Adventure", "Animation", "Comedy", "Crime",
  "Documentary", "Drama", "Fantasy", "Horror", "Mystery",
  "Romance", "Sci-Fi", "Thriller", "War", "Western",
];

const MOODS = [
  "Feel-good", "Intense", "Mind-bending", "Emotional",
  "Relaxing", "Adventurous", "Dark", "Funny",
  "Romantic", "Suspenseful", "Nostalgic", "Inspirational",
];

const STEPS = ["Genres", "Mood", "Details", "Results"];

const pageVariants = {
  enter: { opacity: 0, x: 40 },
  center: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -40 },
};

export default function SoloPage() {
  const router = useRouter();
  const {
    profile,
    context,
    freeText,
    setGenres,
    setMood,
    setFreeText,
    setContext,
    reset,
  } = usePreferencesStore();

  const {
    currentStep,
    setStep,
    recommendation,
    setRecommendation,
    selectedMovie,
    detailOpen,
    openDetail,
    closeDetail,
  } = useUIStore();

  const stepIndex = STEPS.findIndex(
    (s) => s.toLowerCase() === currentStep,
  );

  async function handleSubmit() {
    setStep("loading");

    try {
      const result = await recommend.create({
        mode: "solo",
        users: [profile],
        context: context,
        message: freeText || undefined,
      });
      setRecommendation(result);
      setStep("results");
    } catch {
      toast.error("Something went wrong. Please try again.");
      setStep("details");
    }
  }

  function handleStartOver() {
    reset();
    setRecommendation(null);
    setStep("genres");
  }

  async function handleWatchlist(tmdbId: number) {
    try {
      await users.addToWatchlist(tmdbId);
      toast.success("Added to watchlist!");
    } catch {
      toast.error("Could not add to watchlist.");
    }
  }

  return (
    <>
      <DesktopNav />

      <div className="max-w-2xl mx-auto min-h-screen">
        {currentStep !== "loading" && currentStep !== "results" && (
          <div className="pt-4">
            <StepIndicator steps={STEPS.slice(0, 3)} current={stepIndex} />
          </div>
        )}

        <AnimatePresence mode="wait">
          {/* Step 1: Genres */}
          {currentStep === "genres" && (
            <motion.div
              key="genres"
              variants={pageVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.3 }}
              className="px-6 py-8 space-y-6"
            >
              <div>
                <h1 className="text-2xl font-bold">What are you in the mood for?</h1>
                <p className="text-text-secondary mt-1">
                  Pick one or more genres you&apos;re feeling tonight.
                </p>
              </div>

              <ChipGroup
                options={GENRES}
                selected={profile.likes_genres}
                onChange={setGenres}
                multiple
              />

              <div className="flex gap-3 pt-4">
                <Button
                  variant="secondary"
                  onClick={() => router.push("/")}
                >
                  Back
                </Button>
                <Button
                  variant="primary"
                  onClick={() => setStep("mood")}
                  disabled={profile.likes_genres.length === 0}
                  className="flex-1"
                >
                  Next
                </Button>
              </div>
            </motion.div>
          )}

          {/* Step 2: Mood */}
          {currentStep === "mood" && (
            <motion.div
              key="mood"
              variants={pageVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.3 }}
              className="px-6 py-8 space-y-6"
            >
              <div>
                <h1 className="text-2xl font-bold">Set the mood</h1>
                <p className="text-text-secondary mt-1">
                  How do you want to feel while watching?
                </p>
              </div>

              <ChipGroup
                options={MOODS}
                selected={profile.mood}
                onChange={setMood}
                multiple
              />

              <div className="flex gap-3 pt-4">
                <Button variant="secondary" onClick={() => setStep("genres")}>
                  Back
                </Button>
                <Button
                  variant="primary"
                  onClick={() => setStep("details")}
                  disabled={profile.mood.length === 0}
                  className="flex-1"
                >
                  Next
                </Button>
              </div>
            </motion.div>
          )}

          {/* Step 3: Details */}
          {currentStep === "details" && (
            <motion.div
              key="details"
              variants={pageVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.3 }}
              className="px-6 py-8 space-y-6"
            >
              <div>
                <h1 className="text-2xl font-bold">Any other preferences?</h1>
                <p className="text-text-secondary mt-1">
                  Fine-tune your recommendation or just hit &quot;Find My Movie&quot;.
                </p>
              </div>

              <Textarea
                label="Tell us more (optional)"
                placeholder='e.g., "Something like Interstellar but more upbeat" or "No horror, keep it under 2 hours"'
                value={freeText}
                onChange={(e) => setFreeText(e.target.value)}
                rows={3}
              />

              <div className="space-y-3">
                <label className="flex items-center gap-3 p-3 rounded-xl bg-bg-secondary border border-glass-border cursor-pointer">
                  <input
                    type="checkbox"
                    checked={context.want_something_new ?? false}
                    onChange={(e) =>
                      setContext({ want_something_new: e.target.checked })
                    }
                    className="w-4 h-4 accent-accent rounded"
                  />
                  <div>
                    <span className="text-sm font-medium">Surprise me</span>
                    <p className="text-xs text-text-tertiary">
                      Include hidden gems I might not know
                    </p>
                  </div>
                </label>
              </div>

              <div className="flex gap-3 pt-4">
                <Button variant="secondary" onClick={() => setStep("mood")}>
                  Back
                </Button>
                <Button
                  variant="primary"
                  onClick={handleSubmit}
                  className="flex-1"
                >
                  Find My Movie
                </Button>
              </div>
            </motion.div>
          )}

          {/* Loading */}
          {currentStep === "loading" && (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <AILoading />
            </motion.div>
          )}

          {/* Results */}
          {currentStep === "results" && recommendation && (
            <motion.div
              key="results"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-8"
            >
              <HeroPick
                movie={recommendation.best_pick}
                onDetails={() => openDetail(recommendation.best_pick)}
                onWatchlist={() =>
                  handleWatchlist(recommendation.best_pick.tmdb_id)
                }
              />

              {recommendation.additional_picks.length > 0 && (
                <ScrollRow title="More Picks For You">
                  {recommendation.additional_picks.map((movie, i) => (
                    <MovieCard
                      key={movie.tmdb_id}
                      movie={movie}
                      rank={i + 2}
                      onClick={() => openDetail(movie)}
                    />
                  ))}
                </ScrollRow>
              )}

              <div className="px-6 pb-8">
                <Button
                  variant="secondary"
                  onClick={handleStartOver}
                  className="w-full"
                >
                  Start Over
                </Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
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
