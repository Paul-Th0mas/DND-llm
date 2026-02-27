import { create } from "zustand";
import { devtools } from "zustand/middleware";
import type { AuthState, AuthActions } from "./auth.store.types";
import type { UserProfile } from "@/domains/auth/types";

// Combined store type merging state shape and actions.
type AuthStore = AuthState & AuthActions;

/**
 * Zustand store for authentication state.
 * Shared across domains because the JWT token is needed by the chat domain and others.
 * isLoading is true on init until the first hydration attempt completes.
 */
export const useAuthStore = create<AuthStore>()(
  devtools(
    (set) => ({
      // Initial state — isLoading true prevents flash of unauthenticated content.
      user: null,
      isLoading: true,
      token: null,

      setUser: (user: UserProfile | null) =>
        set({ user }, false, "auth/setUser"),

      setLoading: (isLoading: boolean) =>
        set({ isLoading }, false, "auth/setLoading"),

      setToken: (token: string | null) =>
        set({ token }, false, "auth/setToken"),

      clearAuth: () =>
        set({ user: null, isLoading: false, token: null }, false, "auth/clearAuth"),
    }),
    { name: "AuthStore" }
  )
);

/**
 * Selects the authenticated user from the auth store.
 * @param state - The current auth store state.
 * @returns The UserProfile or null if not authenticated.
 */
export const selectUser = (state: AuthStore): AuthState["user"] => state.user;

/**
 * Selects the loading flag from the auth store.
 * @param state - The current auth store state.
 * @returns True while the initial hydration is in progress.
 */
export const selectIsLoading = (state: AuthStore): AuthState["isLoading"] =>
  state.isLoading;

/**
 * Selects the JWT access token from the auth store.
 * @param state - The current auth store state.
 * @returns The token string or null if not authenticated.
 */
export const selectToken = (state: AuthStore): AuthState["token"] =>
  state.token;
