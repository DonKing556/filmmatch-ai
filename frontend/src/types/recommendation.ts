export interface YearRange {
  min?: number;
  max?: number;
}

export interface Constraints {
  max_runtime_min?: number;
  subtitles_ok?: boolean;
  streaming_services?: string[];
  family_friendly?: boolean;
}

export interface UserProfile {
  name: string;
  likes_genres: string[];
  dislikes_genres: string[];
  favorite_actors: string[];
  favorite_directors: string[];
  year_range?: YearRange;
  mood: string[];
  constraints?: Constraints;
}

export interface Context {
  occasion?: string;
  energy?: string;
  want_something_new: boolean;
  familiarity?: string;
}

export interface RecommendationRequest {
  mode: "solo" | "group";
  users: UserProfile[];
  context?: Context;
  message?: string;
}

export interface RecommendationResponse {
  recommendation: string;
}
