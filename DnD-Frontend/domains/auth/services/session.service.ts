"use client";

import { useAuthStore } from "@/shared/store/auth.store";
import { fetchCurrentUser } from "@/domains/auth/services/auth.service";

// localStorage and cookie key used to persist the JWT access token.
const TOKEN_KEY = "access_token" as const;

/**
 * Persists the access token to localStorage and sets a client-readable cookie
 * so that Next.js middleware can enforce route protection server-side.
 * @param token - The JWT to persist.
 */
function persistToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
  document.cookie = `${TOKEN_KEY}=${token}; path=/; SameSite=Lax`;
}

/**
 * Hydrates the auth session after a successful login or registration.
 *
 * Steps performed:
 * 1. Persists the token to localStorage and cookie.
 * 2. Writes the token into the Zustand auth store.
 * 3. Fetches the user profile from the backend and writes it into the store.
 *
 * The caller is responsible for navigating after this resolves.
 *
 * @param token - The JWT access token returned by the auth endpoint.
 * @throws If the user profile fetch fails (invalid token, network error).
 */
export async function hydrateSession(token: string): Promise<void> {
  persistToken(token);

  const { setToken, setUser } = useAuthStore.getState();
  setToken(token);

  const user = await fetchCurrentUser(token);
  setUser(user);
}
