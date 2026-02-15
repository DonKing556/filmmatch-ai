import { create } from "zustand";
import type { Context, UserProfile } from "@/types/api";

interface PreferencesState {
  // Solo flow
  profile: UserProfile;
  context: Context;
  freeText: string;

  // Actions
  setGenres: (genres: string[]) => void;
  setDislikedGenres: (genres: string[]) => void;
  setMood: (moods: string[]) => void;
  setFreeText: (text: string) => void;
  setContext: (ctx: Partial<Context>) => void;
  setProfileField: <K extends keyof UserProfile>(
    key: K,
    value: UserProfile[K],
  ) => void;
  reset: () => void;
}

const defaultProfile: UserProfile = {
  name: "",
  likes_genres: [],
  dislikes_genres: [],
  favorite_actors: [],
  favorite_directors: [],
  mood: [],
};

const defaultContext: Context = {
  want_something_new: false,
};

export const usePreferencesStore = create<PreferencesState>((set) => ({
  profile: { ...defaultProfile },
  context: { ...defaultContext },
  freeText: "",

  setGenres: (genres) =>
    set((s) => ({ profile: { ...s.profile, likes_genres: genres } })),
  setDislikedGenres: (genres) =>
    set((s) => ({ profile: { ...s.profile, dislikes_genres: genres } })),
  setMood: (moods) =>
    set((s) => ({ profile: { ...s.profile, mood: moods } })),
  setFreeText: (text) => set({ freeText: text }),
  setContext: (ctx) =>
    set((s) => ({ context: { ...s.context, ...ctx } })),
  setProfileField: (key, value) =>
    set((s) => ({ profile: { ...s.profile, [key]: value } })),
  reset: () =>
    set({
      profile: { ...defaultProfile },
      context: { ...defaultContext },
      freeText: "",
    }),
}));
