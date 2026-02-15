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
} from "@/types/api";

const BASE = "/api";

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
    return request<PreferencesUpdate>("/users/preferences", {
      method: "PATCH",
      body: JSON.stringify(prefs),
    });
  },
  watchHistory() {
    return request<WatchHistoryItem[]>("/users/history");
  },
  addToWatchlist(tmdbId: number) {
    return request<void>("/users/watchlist", {
      method: "POST",
      body: JSON.stringify({ tmdb_id: tmdbId }),
    });
  },
  removeFromWatchlist(tmdbId: number) {
    return request<void>(`/users/watchlist/${tmdbId}`, {
      method: "DELETE",
    });
  },
};

// ─── Recommendations ───

export const recommend = {
  create(req: RecommendationRequest) {
    return request<RecommendationResponse>("/recommend/create", {
      method: "POST",
      body: JSON.stringify(req),
    });
  },
  refine(sessionId: string, req: NarrowRequest) {
    return request<RecommendationResponse>(
      `/recommend/${sessionId}/refine`,
      { method: "POST", body: JSON.stringify(req) },
    );
  },
  react(sessionId: string, req: ReactionRequest) {
    return request<void>(`/recommend/${sessionId}/react`, {
      method: "POST",
      body: JSON.stringify(req),
    });
  },
  select(sessionId: string, req: SelectionRequest) {
    return request<void>(`/recommend/${sessionId}/select`, {
      method: "POST",
      body: JSON.stringify(req),
    });
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
    return request<GroupResponse>("/groups/create", {
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
