"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { ChipGroup } from "@/components/ui/chip";
import { StepIndicator } from "@/components/ui/step-indicator";
import { BottomNav, DesktopNav } from "@/components/layout/navigation";
import { usePreferencesStore } from "@/stores/preferences";

// ─── Mood/Vibe Data ───

const VIBES = [
  { id: "thrilling", label: "Thrilling", emoji: "\u26A1", gradient: "from-red-600/30 to-orange-500/30" },
  { id: "cozy", label: "Cozy", emoji: "\u2615", gradient: "from-amber-600/30 to-yellow-500/30" },
  { id: "mind-bending", label: "Mind-Bending", emoji: "\uD83E\uDDE0", gradient: "from-purple-600/30 to-pink-500/30" },
  { id: "feel-good", label: "Feel-Good", emoji: "\u2600\uFE0F", gradient: "from-yellow-500/30 to-green-400/30" },
  { id: "dark", label: "Dark", emoji: "\uD83C\uDF11", gradient: "from-gray-800/30 to-slate-700/30" },
  { id: "funny", label: "Funny", emoji: "\uD83D\uDE02", gradient: "from-cyan-500/30 to-blue-400/30" },
  { id: "romantic", label: "Romantic", emoji: "\u2764\uFE0F", gradient: "from-pink-600/30 to-rose-400/30" },
  { id: "epic", label: "Epic", emoji: "\uD83C\uDFAC", gradient: "from-indigo-600/30 to-violet-500/30" },
];

const GENRES = [
  "Action", "Adventure", "Animation", "Comedy", "Crime",
  "Documentary", "Drama", "Fantasy", "Horror", "Mystery",
  "Romance", "Sci-Fi", "Thriller", "War", "Western",
  "Musical", "Family", "History",
];

const STREAMING_SERVICES = [
  { id: "netflix", label: "Netflix", color: "#E50914" },
  { id: "prime", label: "Prime Video", color: "#00A8E1" },
  { id: "disney", label: "Disney+", color: "#113CCF" },
  { id: "hulu", label: "Hulu", color: "#1CE783" },
  { id: "hbo", label: "Max", color: "#002BE7" },
  { id: "apple", label: "Apple TV+", color: "#555555" },
  { id: "peacock", label: "Peacock", color: "#000000" },
  { id: "paramount", label: "Paramount+", color: "#0064FF" },
];

const STEPS = ["Vibes", "Genres", "Preferences", "Services"];

type OnboardingStep = 0 | 1 | 2 | 3;

export default function OnboardingPage() {
  const router = useRouter();
  const { setMood, setGenres, setContext } = usePreferencesStore();

  const [step, setStep] = useState<OnboardingStep>(0);
  const [selectedVibes, setSelectedVibes] = useState<string[]>([]);
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
  const [dealbreakers, setDealbreakers] = useState({
    subtitlesOk: true,
    longMoviesOk: true,
    familyFriendly: false,
    maxRuntime: null as number | null,
  });
  const [selectedServices, setSelectedServices] = useState<string[]>([]);

  function handleComplete() {
    setMood(selectedVibes);
    setGenres(selectedGenres);
    setContext({
      want_something_new: false,
    });
    localStorage.setItem("fm_onboarded", "true");
    router.push("/solo");
  }

  function canAdvance(): boolean {
    switch (step) {
      case 0: return selectedVibes.length >= 1;
      case 1: return selectedGenres.length >= 3;
      case 2: return true;
      case 3: return true;
    }
  }

  const pageVariants = {
    enter: { opacity: 0, x: 60 },
    center: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -60 },
  };

  return (
    <>
      <DesktopNav />

      <div className="max-w-2xl mx-auto min-h-screen">
        <div className="pt-4">
          <StepIndicator steps={STEPS} current={step} />
        </div>

        <AnimatePresence mode="wait">
          {/* Step 0: Mood/Vibe Selection */}
          {step === 0 && (
            <motion.div
              key="vibes"
              variants={pageVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.35 }}
              className="px-6 py-8 space-y-6"
            >
              <div>
                <h1 className="text-2xl font-bold">What vibes are you into?</h1>
                <p className="text-text-secondary mt-1">
                  Pick 1-3 vibes that match your usual movie mood.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                {VIBES.map((vibe) => {
                  const selected = selectedVibes.includes(vibe.id);
                  return (
                    <motion.button
                      key={vibe.id}
                      whileTap={{ scale: 0.96 }}
                      onClick={() => {
                        setSelectedVibes((prev) =>
                          prev.includes(vibe.id)
                            ? prev.filter((v) => v !== vibe.id)
                            : prev.length < 3
                              ? [...prev, vibe.id]
                              : prev,
                        );
                      }}
                      className={`relative p-5 rounded-2xl border transition-all duration-200 text-left ${
                        selected
                          ? "border-accent bg-accent/10 shadow-glow"
                          : "border-glass-border bg-bg-secondary hover:bg-bg-hover"
                      }`}
                    >
                      <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${vibe.gradient} opacity-50`} />
                      <div className="relative">
                        <span className="text-3xl">{vibe.emoji}</span>
                        <p className="mt-2 font-semibold text-text-primary">
                          {vibe.label}
                        </p>
                      </div>
                      {selected && (
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          className="absolute top-3 right-3 w-6 h-6 rounded-full bg-accent flex items-center justify-center"
                        >
                          <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                          </svg>
                        </motion.div>
                      )}
                    </motion.button>
                  );
                })}
              </div>

              <div className="flex gap-3 pt-4">
                <Button variant="ghost" onClick={() => router.push("/")}>
                  Skip
                </Button>
                <Button
                  variant="primary"
                  onClick={() => setStep(1)}
                  disabled={!canAdvance()}
                  className="flex-1"
                >
                  Next
                </Button>
              </div>
            </motion.div>
          )}

          {/* Step 1: Genre Preferences */}
          {step === 1 && (
            <motion.div
              key="genres"
              variants={pageVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.35 }}
              className="px-6 py-8 space-y-6"
            >
              <div>
                <h1 className="text-2xl font-bold">Pick your favorite genres</h1>
                <p className="text-text-secondary mt-1">
                  Choose at least 3 genres you enjoy.
                </p>
              </div>

              <ChipGroup
                options={GENRES}
                selected={selectedGenres}
                onChange={setSelectedGenres}
                multiple
              />

              <p className="text-sm text-text-tertiary">
                {selectedGenres.length} selected
                {selectedGenres.length < 3 && ` (${3 - selectedGenres.length} more needed)`}
              </p>

              <div className="flex gap-3 pt-4">
                <Button variant="secondary" onClick={() => setStep(0)}>
                  Back
                </Button>
                <Button
                  variant="primary"
                  onClick={() => setStep(2)}
                  disabled={!canAdvance()}
                  className="flex-1"
                >
                  Next
                </Button>
              </div>
            </motion.div>
          )}

          {/* Step 2: Dealbreakers */}
          {step === 2 && (
            <motion.div
              key="dealbreakers"
              variants={pageVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.35 }}
              className="px-6 py-8 space-y-6"
            >
              <div>
                <h1 className="text-2xl font-bold">Any dealbreakers?</h1>
                <p className="text-text-secondary mt-1">
                  Set your preferences so we never recommend something you&apos;d hate.
                </p>
              </div>

              <div className="space-y-3">
                <ToggleRow
                  label="Subtitles are fine"
                  description="Include foreign-language films"
                  checked={dealbreakers.subtitlesOk}
                  onChange={(v) => setDealbreakers((d) => ({ ...d, subtitlesOk: v }))}
                />
                <ToggleRow
                  label="Long movies OK"
                  description="Include films over 2.5 hours"
                  checked={dealbreakers.longMoviesOk}
                  onChange={(v) => setDealbreakers((d) => ({ ...d, longMoviesOk: v }))}
                />
                <ToggleRow
                  label="Keep it family-friendly"
                  description="Nothing above PG-13"
                  checked={dealbreakers.familyFriendly}
                  onChange={(v) => setDealbreakers((d) => ({ ...d, familyFriendly: v }))}
                />
              </div>

              <div className="flex gap-3 pt-4">
                <Button variant="secondary" onClick={() => setStep(1)}>
                  Back
                </Button>
                <Button
                  variant="primary"
                  onClick={() => setStep(3)}
                  className="flex-1"
                >
                  Next
                </Button>
              </div>
            </motion.div>
          )}

          {/* Step 3: Streaming Services */}
          {step === 3 && (
            <motion.div
              key="services"
              variants={pageVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.35 }}
              className="px-6 py-8 space-y-6"
            >
              <div>
                <h1 className="text-2xl font-bold">Where do you watch?</h1>
                <p className="text-text-secondary mt-1">
                  Select your streaming services so we can find what&apos;s available to you.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                {STREAMING_SERVICES.map((service) => {
                  const selected = selectedServices.includes(service.id);
                  return (
                    <motion.button
                      key={service.id}
                      whileTap={{ scale: 0.96 }}
                      onClick={() => {
                        setSelectedServices((prev) =>
                          prev.includes(service.id)
                            ? prev.filter((s) => s !== service.id)
                            : [...prev, service.id],
                        );
                      }}
                      className={`flex items-center gap-3 p-4 rounded-xl border transition-all duration-200 ${
                        selected
                          ? "border-accent bg-accent/10"
                          : "border-glass-border bg-bg-secondary hover:bg-bg-hover"
                      }`}
                    >
                      <div
                        className="w-10 h-10 rounded-lg flex items-center justify-center text-white text-xs font-bold"
                        style={{ backgroundColor: service.color }}
                      >
                        {service.label.charAt(0)}
                      </div>
                      <span className="text-sm font-medium text-text-primary">
                        {service.label}
                      </span>
                      {selected && (
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          className="ml-auto w-5 h-5 rounded-full bg-accent flex items-center justify-center"
                        >
                          <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                          </svg>
                        </motion.div>
                      )}
                    </motion.button>
                  );
                })}
              </div>

              <div className="flex gap-3 pt-4">
                <Button variant="secondary" onClick={() => setStep(2)}>
                  Back
                </Button>
                <Button
                  variant="primary"
                  onClick={handleComplete}
                  className="flex-1"
                >
                  Get Started
                </Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <BottomNav />
    </>
  );
}

// ─── Toggle Row Component ───

function ToggleRow({
  label,
  description,
  checked,
  onChange,
}: {
  label: string;
  description: string;
  checked: boolean;
  onChange: (value: boolean) => void;
}) {
  return (
    <label className="flex items-center justify-between p-4 rounded-xl bg-bg-secondary border border-glass-border cursor-pointer">
      <div>
        <p className="text-sm font-medium text-text-primary">{label}</p>
        <p className="text-xs text-text-tertiary">{description}</p>
      </div>
      <button
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={`relative w-11 h-6 rounded-full transition-colors duration-200 ${
          checked ? "bg-accent" : "bg-bg-tertiary"
        }`}
      >
        <motion.div
          className="absolute top-0.5 w-5 h-5 rounded-full bg-white shadow-sm"
          animate={{ left: checked ? "22px" : "2px" }}
          transition={{ type: "spring", stiffness: 500, damping: 30 }}
        />
      </button>
    </label>
  );
}
