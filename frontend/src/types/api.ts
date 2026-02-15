// ─── Recommendation ───

export interface YearRange {
  min?: number | null;
  max?: number | null;
}

export interface Constraints {
  max_runtime_min?: number | null;
  subtitles_ok?: boolean | null;
  streaming_services?: string[] | null;
  family_friendly?: boolean | null;
}

export interface UserProfile {
  name: string;
  likes_genres: string[];
  dislikes_genres: string[];
  favorite_actors: string[];
  favorite_directors: string[];
  year_range?: YearRange | null;
  mood: string[];
  constraints?: Constraints | null;
}

export interface Context {
  occasion?: string | null;
  energy?: string | null;
  want_something_new?: boolean;
  familiarity?: string | null;
}

export interface RecommendationRequest {
  mode: "solo" | "group";
  users: UserProfile[];
  context?: Context | null;
  message?: string | null;
}

export interface NarrowRequest {
  feedback: string;
  keep_tmdb_ids?: number[];
  reject_tmdb_ids?: number[];
}

export interface ReactionRequest {
  tmdb_id: number;
  positive: boolean;
  reason?: string | null;
}

export interface SelectionRequest {
  tmdb_id: number;
}

export interface MovieSummary {
  tmdb_id: number;
  title: string;
  year: string | null;
  genres: string[];
  vote_average: number;
  runtime: number | null;
  poster_url: string | null;
  backdrop_url: string | null;
  overview: string;
  directors: string[];
  cast: string[];
  match_score: number | null;
  rationale: string;
}

export interface RecommendationResponse {
  session_id: string;
  best_pick: MovieSummary;
  additional_picks: MovieSummary[];
  narrow_question: string | null;
  overlap_summary: string | null;
  model_used: string;
}

// ─── Auth ───

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserResponse {
  id: string;
  email: string;
  display_name: string | null;
  created_at: string;
}

// ─── User ───

export interface PreferencesUpdate {
  preferred_genres?: number[] | null;
  disliked_genres?: number[] | null;
  favorite_actors?: number[] | null;
  favorite_directors?: number[] | null;
  preferred_decades?: number[] | null;
  streaming_services?: string[] | null;
  content_rating_max?: string | null;
  language_preferences?: string[] | null;
}

export interface WatchHistoryItem {
  tmdb_id: number;
  title: string | null;
  poster_url: string | null;
  status: string;
  rating: number | null;
  created_at: string;
}

// ─── Group ───

export interface GroupCreate {
  name?: string | null;
}

export interface GroupMemberPreferences {
  likes_genres: string[];
  dislikes_genres: string[];
  mood: string[];
  constraints?: Record<string, unknown> | null;
}

export interface GroupResponse {
  id: string;
  name: string | null;
  join_code: string;
  member_count: number;
  is_active: boolean;
  created_at: string;
}

// ─── Movies ───

export interface TrendingMovie {
  tmdb_id: number;
  title: string;
  year: string | null;
  poster_url: string | null;
  backdrop_url: string | null;
  vote_average: number;
  genres: string[];
  overview: string;
}
