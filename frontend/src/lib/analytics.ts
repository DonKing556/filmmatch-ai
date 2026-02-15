import posthog from "posthog-js";

const POSTHOG_KEY = process.env.NEXT_PUBLIC_POSTHOG_KEY;
const POSTHOG_HOST = process.env.NEXT_PUBLIC_POSTHOG_HOST ?? "https://us.i.posthog.com";

let initialized = false;

export function initAnalytics() {
  if (typeof window === "undefined" || initialized || !POSTHOG_KEY) return;

  posthog.init(POSTHOG_KEY, {
    api_host: POSTHOG_HOST,
    capture_pageview: true,
    capture_pageleave: true,
    persistence: "localStorage+cookie",
    autocapture: false,
  });

  initialized = true;
}

/** Track a custom event with optional properties. */
export function track(event: string, properties?: Record<string, unknown>) {
  if (!initialized) return;
  posthog.capture(event, properties);
}

/** Identify a logged-in user. */
export function identify(userId: string, traits?: Record<string, unknown>) {
  if (!initialized) return;
  posthog.identify(userId, traits);
}

/** Reset identity on logout. */
export function resetIdentity() {
  if (!initialized) return;
  posthog.reset();
}

// ────────────────────────────────────────────────
// Typed event helpers for key funnel events
// ────────────────────────────────────────────────

export const analytics = {
  onboardingStarted: () => track("onboarding_started"),
  onboardingCompleted: (step: number) =>
    track("onboarding_completed", { steps: step }),

  recommendationRequested: (mode: "solo" | "group", genreCount: number) =>
    track("recommendation_requested", { mode, genre_count: genreCount }),
  recommendationViewed: (sessionId: string, movieCount: number) =>
    track("recommendation_viewed", { session_id: sessionId, movie_count: movieCount }),
  recommendationSelected: (sessionId: string, tmdbId: number) =>
    track("recommendation_selected", { session_id: sessionId, tmdb_id: tmdbId }),

  movieDetailOpened: (tmdbId: number) =>
    track("movie_detail_opened", { tmdb_id: tmdbId }),
  movieReaction: (tmdbId: number, positive: boolean) =>
    track("movie_reaction", { tmdb_id: tmdbId, positive }),

  groupSessionCreated: () => track("group_session_created"),
  groupSessionJoined: (code: string) =>
    track("group_session_joined", { code }),

  feedbackSubmitted: (type: "rating" | "nps", value: number) =>
    track("feedback_submitted", { type, value }),

  watchlistAdded: (tmdbId: number) =>
    track("watchlist_added", { tmdb_id: tmdbId }),
  watchlistRemoved: (tmdbId: number) =>
    track("watchlist_removed", { tmdb_id: tmdbId }),
};
