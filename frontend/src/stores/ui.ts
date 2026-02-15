import { create } from "zustand";
import type { MovieSummary, RecommendationResponse } from "@/types/api";

type FlowStep = "genres" | "mood" | "details" | "loading" | "results";

interface UIState {
  // Solo flow navigation
  currentStep: FlowStep;
  setStep: (step: FlowStep) => void;

  // Results
  recommendation: RecommendationResponse | null;
  setRecommendation: (rec: RecommendationResponse | null) => void;

  // Movie detail modal
  selectedMovie: MovieSummary | null;
  detailOpen: boolean;
  openDetail: (movie: MovieSummary) => void;
  closeDetail: () => void;

  // Tab navigation
  activeTab: "home" | "solo" | "group" | "watchlist";
  setActiveTab: (tab: UIState["activeTab"]) => void;
}

export const useUIStore = create<UIState>((set) => ({
  currentStep: "genres",
  setStep: (step) => set({ currentStep: step }),

  recommendation: null,
  setRecommendation: (rec) => set({ recommendation: rec }),

  selectedMovie: null,
  detailOpen: false,
  openDetail: (movie) => set({ selectedMovie: movie, detailOpen: true }),
  closeDetail: () => set({ detailOpen: false }),

  activeTab: "home",
  setActiveTab: (tab) => set({ activeTab: tab }),
}));
