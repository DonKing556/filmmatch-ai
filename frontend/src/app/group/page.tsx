"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ChipGroup } from "@/components/ui/chip";
import { AILoading } from "@/components/movie/ai-loading";
import { HeroPick } from "@/components/movie/hero-pick";
import { MovieCard } from "@/components/movie/movie-card";
import { MovieDetail } from "@/components/movie/movie-detail";
import { ScrollRow } from "@/components/ui/scroll-row";
import { ShareCode } from "@/components/group/share-code";
import { VoteRound } from "@/components/group/vote-round";
import { BottomNav, DesktopNav } from "@/components/layout/navigation";
import { useUIStore } from "@/stores/ui";
import { recommend, users } from "@/lib/api";
import { toast } from "sonner";
import { analytics } from "@/lib/analytics";
import type { RecommendationResponse, UserProfile } from "@/types/api";

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

type GroupStep =
  | "setup"
  | "share"
  | "members"
  | "waiting"
  | "loading"
  | "results"
  | "voting";

interface MemberEntry {
  name: string;
  likes_genres: string[];
  dealbreakers: string[];
  mood: string[];
}

const emptyMember = (): MemberEntry => ({
  name: "",
  likes_genres: [],
  dealbreakers: [],
  mood: [],
});

export default function GroupPage() {
  const router = useRouter();
  const { selectedMovie, detailOpen, openDetail, closeDetail } = useUIStore();

  const [step, setStep] = useState<GroupStep>("setup");
  const [members, setMembers] = useState<MemberEntry[]>([
    emptyMember(),
    emptyMember(),
  ]);
  const [activeMember, setActiveMember] = useState(0);
  const [recommendation, setRecommendation] =
    useState<RecommendationResponse | null>(null);
  const [groupCode] = useState(() =>
    Math.random().toString(36).substring(2, 8).toUpperCase(),
  );
  const [groupId] = useState(() => crypto.randomUUID());

  function updateMember(index: number, patch: Partial<MemberEntry>) {
    setMembers((prev) =>
      prev.map((m, i) => (i === index ? { ...m, ...patch } : m)),
    );
  }

  function addMember() {
    if (members.length < 6) {
      setMembers((prev) => [...prev, emptyMember()]);
    }
  }

  function removeMember(index: number) {
    if (members.length > 2) {
      setMembers((prev) => prev.filter((_, i) => i !== index));
      if (activeMember >= members.length - 1) {
        setActiveMember(Math.max(0, members.length - 2));
      }
    }
  }

  const allMembersReady = members.every(
    (m) => m.name.trim() && m.likes_genres.length > 0 && m.mood.length > 0,
  );

  async function handleSubmit() {
    setStep("loading");
    analytics.recommendationRequested("group", members.reduce((s, m) => s + m.likes_genres.length, 0));
    try {
      const userProfiles: UserProfile[] = members.map((m) => ({
        name: m.name,
        likes_genres: m.likes_genres,
        dislikes_genres: [],
        dealbreakers: m.dealbreakers,
        favorite_actors: [],
        favorite_directors: [],
        mood: m.mood,
      }));

      const result = await recommend.create({
        mode: "group",
        users: userProfiles,
      });
      setRecommendation(result);
      analytics.recommendationViewed(result.session_id, 1 + result.additional_picks.length);
      setStep("results");
    } catch {
      toast.error("Something went wrong. Please try again.");
      setStep("members");
    }
  }

  async function handleWatchlist(tmdbId: number) {
    try {
      await users.addToWatchlist(tmdbId);
      toast.success("Added to watchlist!");
    } catch {
      toast.error("Could not add to watchlist.");
    }
  }

  function handleVotesComplete(votes: Record<number, boolean>) {
    const positiveIds = Object.entries(votes)
      .filter(([, v]) => v)
      .map(([id]) => Number(id));

    if (recommendation && positiveIds.length > 0) {
      const winner =
        [recommendation.best_pick, ...recommendation.additional_picks].find(
          (m) => m.tmdb_id === positiveIds[0],
        ) ?? recommendation.best_pick;
      toast.success(`Group picked: ${winner.title}!`);
    }
    setStep("results");
  }

  return (
    <>
      <DesktopNav />

      <div className="max-w-2xl mx-auto min-h-screen">
        <AnimatePresence mode="wait">
          {/* Step 1: Setup members */}
          {step === "setup" && (
            <motion.div
              key="setup"
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -40 }}
              className="px-6 py-8 space-y-6"
            >
              <div>
                <h1 className="text-2xl font-bold">Group Watch</h1>
                <p className="text-text-secondary mt-1">
                  Add everyone who&apos;s watching, then set each person&apos;s
                  preferences.
                </p>
              </div>

              <div className="space-y-3">
                {members.map((member, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-3 p-3 rounded-xl bg-bg-secondary border border-glass-border"
                  >
                    <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center text-sm font-bold text-accent">
                      {i + 1}
                    </div>
                    <Input
                      value={member.name}
                      onChange={(e) =>
                        updateMember(i, { name: e.target.value })
                      }
                      placeholder={`Person ${i + 1}'s name`}
                      className="flex-1"
                    />
                    {members.length > 2 && (
                      <button
                        onClick={() => removeMember(i)}
                        className="text-text-tertiary hover:text-error transition-colors p-1"
                      >
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    )}
                  </div>
                ))}
              </div>

              {members.length < 6 && (
                <button
                  onClick={addMember}
                  className="w-full p-3 rounded-xl border border-dashed border-glass-border text-text-secondary hover:text-text-primary hover:border-accent/30 transition-colors text-sm"
                >
                  + Add another person
                </button>
              )}

              <div className="flex gap-3 pt-4">
                <Button variant="secondary" onClick={() => router.push("/")}>
                  Back
                </Button>
                <Button
                  variant="primary"
                  onClick={() => setStep("share")}
                  disabled={members.some((m) => !m.name.trim())}
                  className="flex-1"
                >
                  Continue
                </Button>
              </div>
            </motion.div>
          )}

          {/* Step 2: Share code */}
          {step === "share" && (
            <motion.div
              key="share"
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -40 }}
              className="px-6 py-8 space-y-6"
            >
              <div className="text-center">
                <h1 className="text-2xl font-bold">Invite your crew</h1>
                <p className="text-text-secondary mt-1">
                  Share this code so others can join the session.
                </p>
              </div>

              <ShareCode joinCode={groupCode} groupId={groupId} />

              <Button
                variant="primary"
                onClick={() => {
                  setActiveMember(0);
                  setStep("members");
                }}
                className="w-full"
              >
                Set Preferences
              </Button>
            </motion.div>
          )}

          {/* Step 3: Member preferences */}
          {step === "members" && (
            <motion.div
              key="members"
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -40 }}
              className="px-6 py-8 space-y-6"
            >
              {/* Member tabs */}
              <div className="flex gap-2 overflow-x-auto pb-2">
                {members.map((m, i) => {
                  const ready =
                    m.likes_genres.length > 0 && m.mood.length > 0;
                  return (
                    <button
                      key={i}
                      onClick={() => setActiveMember(i)}
                      className={`px-4 py-2 rounded-full text-sm font-medium transition-colors whitespace-nowrap ${
                        i === activeMember
                          ? "bg-accent text-white"
                          : ready
                            ? "bg-success/10 text-success border border-success/20"
                            : "bg-bg-tertiary text-text-secondary"
                      }`}
                    >
                      {m.name || `Person ${i + 1}`}
                      {ready && i !== activeMember && " \u2713"}
                    </button>
                  );
                })}
              </div>

              <div>
                <h2 className="text-xl font-bold">
                  {members[activeMember]?.name || "Person"}&apos;s Preferences
                </h2>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-text-secondary mb-3">
                  Genres
                </h3>
                <ChipGroup
                  options={GENRES}
                  selected={members[activeMember]?.likes_genres ?? []}
                  onChange={(genres) =>
                    updateMember(activeMember, { likes_genres: genres })
                  }
                  multiple
                />
              </div>

              <div>
                <h3 className="text-sm font-semibold text-text-secondary mb-3">
                  Mood
                </h3>
                <ChipGroup
                  options={MOODS}
                  selected={members[activeMember]?.mood ?? []}
                  onChange={(moods) =>
                    updateMember(activeMember, { mood: moods })
                  }
                  multiple
                />
              </div>

              <div className="flex gap-3 pt-4">
                {activeMember > 0 ? (
                  <Button
                    variant="secondary"
                    onClick={() => setActiveMember(activeMember - 1)}
                  >
                    Previous
                  </Button>
                ) : (
                  <Button
                    variant="secondary"
                    onClick={() => setStep("share")}
                  >
                    Back
                  </Button>
                )}

                {activeMember < members.length - 1 ? (
                  <Button
                    variant="primary"
                    onClick={() => setActiveMember(activeMember + 1)}
                    className="flex-1"
                    disabled={
                      (members[activeMember]?.likes_genres.length ?? 0) === 0 ||
                      (members[activeMember]?.mood.length ?? 0) === 0
                    }
                  >
                    Next Person
                  </Button>
                ) : (
                  <Button
                    variant="primary"
                    onClick={handleSubmit}
                    className="flex-1"
                    disabled={!allMembersReady}
                  >
                    Find Our Movie
                  </Button>
                )}
              </div>
            </motion.div>
          )}

          {/* Loading */}
          {step === "loading" && (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <AILoading />
            </motion.div>
          )}

          {/* Voting */}
          {step === "voting" && recommendation && (
            <motion.div
              key="voting"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <VoteRound
                movies={[
                  recommendation.best_pick,
                  ...recommendation.additional_picks,
                ]}
                onVotesComplete={handleVotesComplete}
              />
            </motion.div>
          )}

          {/* Results */}
          {step === "results" && recommendation && (
            <motion.div
              key="results"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-8"
            >
              {recommendation.overlap_summary && (
                <div className="mx-6 mt-6 p-4 rounded-xl bg-accent/5 border border-accent/10">
                  <p className="text-sm font-medium text-accent mb-1">
                    Group Overlap
                  </p>
                  <p className="text-sm text-text-secondary">
                    {recommendation.overlap_summary}
                  </p>
                </div>
              )}

              <HeroPick
                movie={recommendation.best_pick}
                onDetails={() => openDetail(recommendation.best_pick)}
                onWatchlist={() =>
                  handleWatchlist(recommendation.best_pick.tmdb_id)
                }
              />

              {recommendation.additional_picks.length > 0 && (
                <ScrollRow title="More Picks For The Group">
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

              {/* Vote CTA */}
              <div className="px-6">
                <Button
                  variant="secondary"
                  onClick={() => setStep("voting")}
                  className="w-full"
                >
                  Vote on picks
                </Button>
              </div>

              <div className="px-6 pb-8">
                <Button
                  variant="ghost"
                  onClick={() => {
                    setRecommendation(null);
                    setStep("setup");
                  }}
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
