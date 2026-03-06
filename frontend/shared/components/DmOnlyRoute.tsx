"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import Typography from "@mui/material/Typography";
import { useAuthStore, selectUser, selectIsLoading } from "@/shared/store/auth.store";

/** Props for DmOnlyRoute. */
interface DmOnlyRouteProps {
  readonly children: React.ReactNode;
}

/**
 * Guards a route behind DM role authentication.
 * - While the auth store is hydrating, shows a loading spinner.
 * - If no user is present, redirects to /login.
 * - If the user is a player (not a DM), shows a clear "DM only" message
 *   instead of a blank page or raw 403 error.
 * - If the user is a DM, renders children.
 */
export function DmOnlyRoute({ children }: DmOnlyRouteProps): React.ReactElement {
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
      <Box className="flex min-h-screen items-center justify-center" aria-label="Loading">
        <CircularProgress color="primary" />
      </Box>
    );
  }

  if (user === null) {
    return (
      <Box className="flex min-h-screen items-center justify-center" aria-label="Redirecting">
        <CircularProgress color="primary" />
      </Box>
    );
  }

  if (user.role !== "dm") {
    return (
      <Box
        sx={{
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 1,
          px: 4,
          textAlign: "center",
        }}
      >
        <Typography variant="h5" fontWeight={700}>
          DM Only
        </Typography>
        <Typography variant="body1" color="text.secondary">
          This area is restricted to the Dungeon Master. Ask your DM to share world and campaign
          details with you in the game room.
        </Typography>
      </Box>
    );
  }

  return <>{children}</>;
}
