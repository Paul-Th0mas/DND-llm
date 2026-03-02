import { apiPost } from "@/lib/api/client";
import { AuthError } from "@/domains/auth/types";
import type { UserProfile, AuthTokenResponse } from "@/domains/auth/types";

/**
 * Fetches the currently authenticated user's profile via the BFF proxy.
 * Calls /api/users/me (Next.js route handler) which proxies to the backend.
 * @param token - The JWT access token from localStorage.
 * @returns A promise resolving to the authenticated user's profile.
 * @throws AuthError on 401, 404, or any non-2xx response.
 */
export async function fetchCurrentUser(token: string): Promise<UserProfile> {
  const response = await fetch("/api/users/me", {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new AuthError(
      `Failed to fetch current user: ${response.status}`,
      response.status
    );
  }

  return response.json() as Promise<UserProfile>;
}

/**
 * Authenticates a user with email and password.
 * Calls POST /api/v1/auth/login on the backend.
 * @param email - The user's email address.
 * @param password - The user's plain-text password.
 * @returns A promise resolving to the auth token response.
 * @throws Error if the request fails (wrong credentials, network error, etc.).
 */
export async function loginWithEmail(
  email: string,
  password: string
): Promise<AuthTokenResponse> {
  return apiPost<AuthTokenResponse>("/api/v1/auth/login", { email, password });
}

/**
 * Registers a new user account with email, password, and role.
 * Calls POST /api/v1/auth/register on the backend.
 * @param name - The display name for the new account.
 * @param email - The user's email address.
 * @param password - The user's chosen password.
 * @param role - Whether the user is a Dungeon Master or a player.
 * @returns A promise resolving to the auth token response.
 * @throws Error if the request fails (duplicate email, validation error, etc.).
 */
export async function registerUser(
  name: string,
  email: string,
  password: string,
  role: "dm" | "player"
): Promise<AuthTokenResponse> {
  return apiPost<AuthTokenResponse>("/api/v1/auth/register", {
    name,
    email,
    password,
    role,
  });
}
