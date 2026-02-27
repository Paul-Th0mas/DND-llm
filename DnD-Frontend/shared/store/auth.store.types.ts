import type { UserProfile } from "@/domains/auth/types";

/**
 * State shape for the auth store.
 * isLoading starts as true until the first hydration attempt completes.
 */
export interface AuthState {
  readonly user: UserProfile | null;
  readonly isLoading: boolean;
  /** JWT access token mirrored from localStorage for in-memory access. */
  readonly token: string | null;
}

/**
 * Actions available on the auth store.
 */
export interface AuthActions {
  setUser: (user: UserProfile | null) => void;
  setLoading: (isLoading: boolean) => void;
  setToken: (token: string | null) => void;
  clearAuth: () => void;
}
