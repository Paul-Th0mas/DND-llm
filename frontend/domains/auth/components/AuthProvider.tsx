"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/shared/store/auth.store";
import { fetchCurrentUser } from "@/domains/auth/services/auth.service";

// localStorage and cookie key used to persist the JWT access token.
const TOKEN_KEY = "access_token" as const;

/**
 * Sets the access token cookie so that Next.js middleware can read it
 * for server-side route protection.
 * Not httpOnly — must be writable by client JS.
 * @param token - The JWT to store in the cookie.
 */
function setTokenCookie(token: string): void {
  document.cookie = `${TOKEN_KEY}=${token}; path=/; SameSite=Lax`;
}

/**
 * Expires the access token cookie, effectively clearing it.
 */
function clearTokenCookie(): void {
  document.cookie = `${TOKEN_KEY}=; path=/; SameSite=Lax; max-age=0`;
}

/**
 * Props for AuthProvider.
 */
interface AuthProviderProps {
  readonly children: React.ReactNode;
}

/**
 * Initializes authentication state on mount.
 * Responsibilities (in order):
 * 1. Reads ?token= from the URL (OAuth callback), saves it to localStorage, strips from URL.
 * 2. Reads the token from localStorage.
 * 3. If a token is present, calls /api/users/me to hydrate the user into the store.
 * 4. On failure, clears the token and marks the user as logged out.
 * 5. If no token, marks loading as false (user is null = logged out).
 * Renders children with no visual output of its own.
 */
export function AuthProvider({ children }: AuthProviderProps): React.ReactNode {
  const setUser = useAuthStore((s) => s.setUser);
  const setToken = useAuthStore((s) => s.setToken);
  const setLoading = useAuthStore((s) => s.setLoading);
  const clearAuth = useAuthStore((s) => s.clearAuth);
  const router = useRouter();

  useEffect(() => {
    async function initAuth(): Promise<void> {
      // Step 1: check if the URL contains a token from the OAuth callback.
      const params = new URLSearchParams(window.location.search);
      const urlToken = params.get("token");

      if (urlToken) {
        localStorage.setItem(TOKEN_KEY, urlToken);
        setTokenCookie(urlToken);
        // Strip the token from the URL to avoid exposing it in browser history.
        window.history.replaceState({}, "", window.location.pathname);
      }

      // Step 2: read the token from localStorage (may have just been set above).
      const token = localStorage.getItem(TOKEN_KEY);

      if (!token) {
        clearTokenCookie();
        setLoading(false);
        return;
      }

      // Ensure the cookie mirrors localStorage in case it was cleared externally.
      setTokenCookie(token);
      setToken(token);

      // Step 3: hydrate the user from the backend.
      try {
        const user = await fetchCurrentUser(token);
        setUser(user);
        router.replace("/dashboard");
      } catch {
        // Token is invalid or expired — treat as logged out.
        localStorage.removeItem(TOKEN_KEY);
        clearTokenCookie();
        clearAuth();
        router.replace("/login");
      } finally {
        setLoading(false);
      }
    }

    void initAuth();
    // Run only once on mount.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return children;
}
