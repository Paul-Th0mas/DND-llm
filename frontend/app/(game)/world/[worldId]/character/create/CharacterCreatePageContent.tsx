"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import Typography from "@mui/material/Typography";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { ProtectedRoute } from "@/shared/components/ProtectedRoute";
import { CreateCharacterWizard } from "@/domains/character/components/CreateCharacterWizard";
import { getWorldById } from "@/domains/world/services/world.service";
import { ApiError } from "@/lib/api/client";
import type { WorldDetail } from "@/domains/world/types";

/** Props for CharacterCreatePageContent. */
export interface CharacterCreatePageContentProps {
  /** The UUID of the world this character will belong to. */
  readonly worldId: string;
}

/**
 * Client component for the world-scoped character creation page.
 * Fetches the world to resolve the theme, then renders the CreateCharacterWizard.
 * Characters belong to worlds — this page enforces that architectural rule.
 * Restricted to authenticated users (player and dm roles) via ProtectedRoute.
 * Route: /world/{worldId}/character/create
 */
export function CharacterCreatePageContent({
  worldId,
}: CharacterCreatePageContentProps): React.ReactElement {
  const router = useRouter();
  const [world, setWorld] = useState<WorldDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Read token on the client side only — localStorage is not available in SSR.
  const token =
    typeof window !== "undefined"
      ? (localStorage.getItem("access_token") ?? "")
      : "";

  useEffect(() => {
    if (!worldId) return;

    let cancelled = false;
    setIsLoading(true);
    setError(null);

    async function fetchWorld(): Promise<void> {
      try {
        const worldData = await getWorldById(worldId);
        if (cancelled) return;

        // A missing theme means the world data is incomplete — do not mount wizard.
        if (!worldData.theme) {
          setError("World not found.");
          return;
        }

        setWorld(worldData);
      } catch (err) {
        if (!cancelled) {
          if (err instanceof ApiError && err.status === 404) {
            setError("World not found.");
          } else {
            setError("Could not load world details.");
          }
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    void fetchWorld();

    return () => {
      cancelled = true;
    };
  }, [worldId]);

  return (
    <ProtectedRoute>
      <Box sx={{ minHeight: "100vh", bgcolor: "background.default" }}>
        {/* Page header */}
        <Box
          component="header"
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 1,
            px: { xs: 3, sm: 6 },
            py: 2,
            borderBottom: "1px solid",
            borderColor: "divider",
            bgcolor: "background.paper",
          }}
        >
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => router.push(`/world/${worldId}`)}
            sx={{ textTransform: "none", color: "text.secondary" }}
          >
            Back to World
          </Button>
          <Typography variant="h6" fontWeight={700} sx={{ ml: 1 }}>
            Create Character
          </Typography>
        </Box>

        {/* Content */}
        <Box sx={{ px: { xs: 3, sm: 6 }, py: 4 }}>
          {isLoading && (
            <Box sx={{ display: "flex", justifyContent: "center", py: 10 }}>
              <CircularProgress />
            </Box>
          )}

          {!isLoading && error !== null && (
            <Alert severity="error">{error}</Alert>
          )}

          {!isLoading && error === null && world !== null && (
            <CreateCharacterWizard
              worldId={worldId}
              worldTheme={world.theme}
              token={token}
            />
          )}
        </Box>
      </Box>
    </ProtectedRoute>
  );
}
