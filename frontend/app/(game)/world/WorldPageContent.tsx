"use client";

import { useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Typography from "@mui/material/Typography";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { AppCard } from "@/shared/components/AppCard";
import { ProtectedRoute } from "@/shared/components/ProtectedRoute";
import { getWorlds } from "@/domains/world/services/world.service";
import {
  useWorldStore,
  selectWorlds,
  selectWorldIsLoading,
} from "@/domains/world/store/world.store";
import type { WorldSummary, WorldTheme } from "@/domains/world/types";

/**
 * Converts a snake_case WorldTheme enum value to a human-readable title-case string.
 * For example, "MEDIEVAL_FANTASY" becomes "Medieval Fantasy".
 * @param theme - The raw WorldTheme enum value from the API.
 * @returns A formatted, human-readable string.
 */
function formatTheme(theme: WorldTheme): string {
  return theme
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
    .join(" ");
}

/**
 * Props for WorldCard.
 */
interface WorldCardProps {
  readonly world: WorldSummary;
  readonly index: number;
  readonly onCreateCharacter: (worldId: string) => void;
  readonly onViewWorld: (worldId: string) => void;
}

/**
 * Displays a single world summary card using AppCard.
 * Shows world name, theme chip, description, and action buttons.
 * Used in the world listing grid on the /world page.
 */
function WorldCard({
  world,
  index,
  onCreateCharacter,
  onViewWorld,
}: WorldCardProps): React.ReactElement {
  return (
    <AppCard
      title={world.name}
      chips={[
        <Chip
          key="theme"
          label={formatTheme(world.theme)}
          size="small"
          sx={{
            bgcolor: "#a07d60",
            color: "#F9F8F6",
            fontWeight: 600,
          }}
        />,
      ]}
      actions={
        <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
          <Button
            variant="contained"
            size="small"
            onClick={() => onCreateCharacter(world.world_id)}
            sx={{
              bgcolor: "#7d5e45",
              "&:hover": { bgcolor: "#5c4230" },
              textTransform: "none",
              fontWeight: 600,
            }}
          >
            Create a Character
          </Button>
          <Button
            variant="outlined"
            size="small"
            onClick={() => onViewWorld(world.world_id)}
            sx={{
              borderColor: "#7d5e45",
              color: "#7d5e45",
              textTransform: "none",
              fontWeight: 600,
              "&:hover": {
                borderColor: "#5c4230",
                color: "#5c4230",
                bgcolor: "transparent",
              },
            }}
          >
            View World
          </Button>
        </Box>
      }
      staggerIndex={index}
    >
      <Typography variant="body2" color="text.secondary">
        {world.description}
      </Typography>
    </AppCard>
  );
}

/**
 * Client component for the /world page.
 * Fetches and renders a grid of pre-seeded worlds, each with navigation
 * to the character creation wizard or the world detail page.
 * Accessible to all authenticated users (not DM-only).
 */
export function WorldPageContent(): React.ReactElement {
  const router = useRouter();
  const worlds = useWorldStore(selectWorlds);
  const isLoading = useWorldStore(selectWorldIsLoading);
  const setWorlds = useWorldStore((state) => state.setWorlds);
  const setLoading = useWorldStore((state) => state.setLoading);
  const setError = useWorldStore((state) => state.setError);
  const error = useWorldStore((state) => state.error);

  const fetchWorlds = useCallback(async (): Promise<void> => {
    // Skip the fetch if the store already has world data.
    if (worlds.length > 0) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await getWorlds();
      setWorlds(data);
    } catch {
      setError("Failed to load worlds. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [worlds.length, setLoading, setError, setWorlds]);

  useEffect(() => {
    void fetchWorlds();
  }, [fetchWorlds]);

  const handleCreateCharacter = useCallback(
    (worldId: string): void => {
      router.push(`/world/${worldId}/character/create`);
    },
    [router]
  );

  const handleViewWorld = useCallback(
    (worldId: string): void => {
      router.push(`/world/${worldId}`);
    },
    [router]
  );

  const renderContent = (): React.ReactElement => {
    if (isLoading) {
      return (
        <Box className="flex justify-center py-16">
          <CircularProgress sx={{ color: "#a07d60" }} />
        </Box>
      );
    }

    if (error !== null) {
      return (
        <Box className="py-8">
          <Alert
            severity="error"
            action={
              <Button
                color="inherit"
                size="small"
                onClick={() => {
                  setError(null);
                  void fetchWorlds();
                }}
              >
                Retry
              </Button>
            }
          >
            {error}
          </Alert>
        </Box>
      );
    }

    if (worlds.length === 0) {
      return (
        <Box className="flex justify-center py-16">
          <Typography variant="body1" sx={{ color: "#C9B59C" }}>
            No worlds are available yet.
          </Typography>
        </Box>
      );
    }

    return (
      <Box className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {worlds.map((world, index) => (
          <WorldCard
            key={world.world_id}
            world={world}
            index={index}
            onCreateCharacter={handleCreateCharacter}
            onViewWorld={handleViewWorld}
          />
        ))}
      </Box>
    );
  };

  return (
    <ProtectedRoute>
      <Box sx={{ minHeight: "100vh", bgcolor: "#F9F8F6" }}>
        {/* Page header */}
        <Box
          component="header"
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 1,
            px: { xs: 3, sm: 6 },
            py: 2,
            borderBottom: "1px solid #D9CFC7",
            bgcolor: "#EFE9E3",
          }}
        >
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => router.push("/dashboard")}
            sx={{ textTransform: "none", color: "#5c4230" }}
          >
            Dashboard
          </Button>
          <Typography
            variant="h6"
            fontWeight={700}
            sx={{ ml: 1, color: "#1e1410" }}
          >
            Browse Worlds
          </Typography>
        </Box>

        {/* Content */}
        <Box sx={{ px: { xs: 3, sm: 6 }, py: 4 }}>
          <Typography
            variant="body1"
            sx={{ color: "#C9B59C", mb: 4 }}
          >
            Choose a world to explore its lore and begin creating your character.
          </Typography>
          {renderContent()}
        </Box>
      </Box>
    </ProtectedRoute>
  );
}
