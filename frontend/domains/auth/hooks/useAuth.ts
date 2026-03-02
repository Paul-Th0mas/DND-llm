"use client";

import {
  useAuthStore,
  selectUser,
  selectIsLoading,
} from "@/shared/store/auth.store";
import type { UserProfile } from "@/domains/auth/types";

// localStorage and cookie key used to persist the JWT access token.
const TOKEN_KEY = "access_token" as const;

/**
 * Return type for the useAuth hook.
 */
export interface UseAuthReturn {
  readonly user: UserProfile | null;
  readonly isLoading: boolean;
  login: () => void;
  logout: () => void;
}

/**
 * Thin hook that exposes auth state and actions to client components.
 * login() triggers a full browser navigation to the backend OAuth endpoint.
 * logout() removes the token from localStorage and clears the Zustand store.
 * @returns Auth state and login/logout actions.
 */
export function useAuth(): UseAuthReturn {
  const user = useAuthStore(selectUser);
  const isLoading = useAuthStore(selectIsLoading);
  const clearAuth = useAuthStore((s) => s.clearAuth);

  function login(): void {
    // Full browser navigation is required — router.push cannot handle
    // cross-origin redirects initiated by the OAuth provider.
    window.location.href = `${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/google`;
  }

  function logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    // Clear the cookie so the middleware immediately treats the user as logged out.
    document.cookie = `${TOKEN_KEY}=; path=/; SameSite=Lax; max-age=0`;
    clearAuth();
  }

  return { user, isLoading, login, logout };
}
