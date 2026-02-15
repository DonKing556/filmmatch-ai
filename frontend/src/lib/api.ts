import type {
  RecommendationRequest,
  RecommendationResponse,
  NarrowRequest,
  ReactionRequest,
  SelectionRequest,
  TokenResponse,
  UserResponse,
  PreferencesUpdate,
  WatchHistoryItem,
  GroupResponse,
  GroupMemberPreferences,
  TrendingMovie,
  MovieSummary,
  TasteProfile,
} from "@/types/api";

const BASE = "/api/v1";

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token =
    typeof window !== "undefined"
      ? localStorage.getItem("fm_access_token")
      : null;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) ?? {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE}${path}`, { ...options, headers });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(res.status, body.detail ?? res.statusText);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

/** Retry a request up to `retries` times with exponential backoff. */
async function requestWithRetry<T>(
  path: string,
  options: RequestInit = {},
  retries = 2,
): Promise<T> {
  let lastError: Error | undefined;
  for (let i = 0; i <= retries; i++) {
    try {
      return await request<T>(path, options);
    } catch (err) {
      lastError = err as Error;
      // Don't retry client errors (4xx)
      if (err instanceof ApiError && err.status >= 400 && err.status < 500) {
        throw err;
      }
      if (i < retries) {
        await new Promise((r) => setTimeout(r, 1000 * (i + 1)));
      }
    }
  }
  throw lastError;
}

// ─── Auth ───

export const auth = {
  requestMagicLink(email: string) {
    return request<{ message: string }>("/auth/magic-link", {
      method: "POST",
      body: JSON.stringify({ email }),
    });
  },
  verifyMagicLink(token: string) {
    return request<TokenResponse>("/auth/verify", {
      method: "POST",
      body: JSON.stringify({ token }),
    });
  },
  refresh(refreshToken: string) {
    return request<TokenResponse>("/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  },
  logout() {
    return request<void>("/auth/logout", { method: "POST" });
  },
};

// ─── User ───

export const users = {
  me() {
    return request<UserResponse>("/users/me");
  },
  updatePreferences(prefs: PreferencesUpdate) {
    return request<PreferencesUpdate>("/users/me/preferences", {
      method: "PATCH",
      body: JSON.stringify(prefs),
    });
  },
  watchHistory() {
    return request<WatchHistoryItem[]>("/users/me/history");
  },
  addToWatchlist(tmdbId: number) {
    return request<void>("/users/me/watchlist", {
      method: "POST",
      body: JSON.stringify({ tmdb_id: tmdbId }),
    });
  },
  removeFromWatchlist(tmdbId: number) {
    return request<void>(`/users/me/watchlist/${tmdbId}`, {
      method: "DELETE",
    });
  },
  tasteProfile() {
    return request<TasteProfile>("/users/me/taste-profile");
  },
  rateMovie(tmdbId: number, rating: number) {
    return request<{ message: string }>(`/users/me/watchlist/${tmdbId}/rate`, {
      method: "PATCH",
      body: JSON.stringify({ rating, status: "watched" }),
    });
  },
  submitFeedback(type: string, value: number, comment?: string, sessionId?: string) {
    return request<{ message: string }>("/users/me/feedback", {
      method: "POST",
      body: JSON.stringify({ type, value, comment, session_id: sessionId }),
    });
  },
};

// ─── Recommendations ───

export const recommend = {
  create(req: RecommendationRequest) {
    return requestWithRetry<RecommendationResponse>("/recommendations", {
      method: "POST",
      body: JSON.stringify(req),
    });
  },
  refine(sessionId: string, req: NarrowRequest) {
    return requestWithRetry<RecommendationResponse>(
      `/recommendations/${sessionId}/refine`,
      { method: "POST", body: JSON.stringify(req) },
    );
  },
  react(sessionId: string, req: ReactionRequest) {
    return request<void>(`/recommendations/${sessionId}/react`, {
      method: "POST",
      body: JSON.stringify(req),
    });
  },
  select(sessionId: string, req: SelectionRequest) {
    return request<void>(`/recommendations/${sessionId}/select`, {
      method: "POST",
      body: JSON.stringify(req),
    });
  },
  receipt(sessionId: string) {
    return request<{
      session_id: string;
      mode: string;
      members: string[];
      movies_considered: number;
      movies_liked: number;
      movies_passed: number;
      final_pick_tmdb_id: number | null;
      complexity_tier: string;
      turn_count: number;
      shareable_text: string;
    }>(`/recommendations/${sessionId}/receipt`);
  },
};

// ─── Movies ───

export const movies = {
  trending() {
    return request<TrendingMovie[]>("/movies/trending");
  },
  details(tmdbId: number) {
    return request<MovieSummary>(`/movies/${tmdbId}`);
  },
};

// ─── Groups ───

export const groups = {
  create(name?: string) {
    return request<GroupResponse>("/groups", {
      method: "POST",
      body: JSON.stringify({ name }),
    });
  },
  join(joinCode: string) {
    return request<GroupResponse>("/groups/join", {
      method: "POST",
      body: JSON.stringify({ join_code: joinCode }),
    });
  },
  get(groupId: string) {
    return request<GroupResponse>(`/groups/${groupId}`);
  },
  submitPreferences(groupId: string, prefs: GroupMemberPreferences) {
    return request<void>(`/groups/${groupId}/preferences`, {
      method: "POST",
      body: JSON.stringify(prefs),
    });
  },
};

export { ApiError };
