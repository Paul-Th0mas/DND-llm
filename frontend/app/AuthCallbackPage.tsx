"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import { useAuthStore, selectUser, selectIsLoading } from "@/shared/store/auth.store";

/**
 * Client component rendered at the root "/" route.
 * Once AuthProvider has finished hydrating the auth state, this component
 * redirects the user to /dashboard (if authenticated) or /login (if not).
 * While hydration is in progress a centered spinner is shown.
 */
export function AuthCallbackPage(): React.ReactElement {
  const user = useAuthStore(selectUser);
  const isLoading = useAuthStore(selectIsLoading);
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (user) {
        router.replace("/dashboard");
      } else {
        router.replace("/login");
      }
    }
  }, [isLoading, user, router]);

  return (
    <Box
      className="flex min-h-screen items-center justify-center"
      aria-label="Initialising"
    >
      <CircularProgress color="primary" />
    </Box>
  );
}
