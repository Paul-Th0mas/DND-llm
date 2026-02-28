"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import { useAuthStore, selectUser, selectIsLoading } from "@/shared/store/auth.store";

/**
 * Props for ProtectedRoute.
 */
interface ProtectedRouteProps {
  readonly children: React.ReactNode;
}

/**
 * Guards a route behind authentication.
 * While the auth store is hydrating, renders a centered loading spinner.
 * If hydration completes and no user is present, redirects to /login.
 * Otherwise renders children.
 */
export function ProtectedRoute({ children }: ProtectedRouteProps): React.ReactElement {
  const user = useAuthStore(selectUser);
  const isLoading = useAuthStore(selectIsLoading);
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && user === null) {
      router.replace("/login");
    }
  }, [isLoading, user, router]);

  if (isLoading) {
    return (
      <Box
        className="flex min-h-screen items-center justify-center"
        aria-label="Loading"
      >
        <CircularProgress color="primary" />
      </Box>
    );
  }

  if (user === null) {
    // Redirect is in progress via useEffect above — render nothing.
    return (
      <Box
        className="flex min-h-screen items-center justify-center"
        aria-label="Redirecting"
      >
        <CircularProgress color="primary" />
      </Box>
    );
  }

  return <>{children}</>;
}
