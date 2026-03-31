"use client";

import { useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Divider from "@mui/material/Divider";
import Typography from "@mui/material/Typography";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { AppCard } from "@/shared/components/AppCard";
import { ProtectedRoute } from "@/shared/components/ProtectedRoute";
import { getWorldById } from "@/domains/world/services/world.service";
import {
  useWorldStore,
  selectSelectedWorld,
  selectWorldIsLoading,
} from "@/domains/world/store/world.store";
import type { PresetBoss, PresetFaction, WorldTheme } from "@/domains/world/types";

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

/** Props for FactionCard. */
interface FactionCardProps {
  readonly faction: PresetFaction;
}

/**
 * Displays a single faction using AppCard.
 * Shows the faction's name, alignment chip, and public reputation.
 */
function FactionCard({ faction }: FactionCardProps): React.ReactElement {
  return (
    <AppCard
      title={faction.name}
      chips={[
        <Chip
          key="alignment"
          label={`Alignment: ${faction.alignment}`}
          size="small"
          variant="outlined"
          sx={{ fontSize: "0.7rem" }}
        />,
      ]}
    >
      <Typography variant="body2" sx={{ color: "#5c4230" }}>
        {faction.public_reputation}
      </Typography>
    </AppCard>
  );
}

/** Props for BossCard. */
interface BossCardProps {
  readonly boss: PresetBoss;
}

/**
 * Displays a single boss using AppCard.
 * Shows the boss's name and challenge rating chip.
 */
function BossCard({ boss }: BossCardProps): React.ReactElement {
  return (
    <AppCard
      title={boss.name}
      chips={[
        <Chip
          key="cr"
          label={`CR ${boss.challenge_rating}`}
          size="small"
          color="error"
          variant="outlined"
          sx={{ fontSize: "0.7rem" }}
        />,
      ]}
    />
  );
}

/** Props for WorldDetailPageContent. */
export interface WorldDetailPageContentProps {
  /** The UUID of the world to display, sourced from the URL segment. */
  readonly worldId: string;
}

/**
 * Client component for the /world/[worldId] detail page.
 * Fetches and renders full world detail including lore, factions, and bosses.
 * If the store already holds the correct world (matching worldId), uses cached data.
 * Wraps content in ProtectedRoute so only authenticated users can view it.
 */
export function WorldDetailPageContent({
  worldId,
}: WorldDetailPageContentProps): React.ReactElement {
  const router = useRouter();
  const selectedWorld = useWorldStore(selectSelectedWorld);
  const isLoading = useWorldStore(selectWorldIsLoading);
  const setSelectedWorld = useWorldStore((state) => state.setSelectedWorld);
  const setLoading = useWorldStore((state) => state.setLoading);
  const setError = useWorldStore((state) => state.setError);
  const error = useWorldStore((state) => state.error);

  const fetchWorld = useCallback(async (): Promise<void> => {
    // Use cached data if the store already holds detail for this exact world.
    if (selectedWorld !== null && selectedWorld.world_id === worldId) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await getWorldById(worldId);
      setSelectedWorld(data);
    } catch {
      setError("Failed to load world details. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [worldId, selectedWorld, setLoading, setError, setSelectedWorld]);

  useEffect(() => {
    void fetchWorld();
  }, [fetchWorld]);

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
                  void fetchWorld();
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

    if (selectedWorld === null || selectedWorld.world_id !== worldId) {
      return (
        <Box className="flex justify-center py-16">
          <CircularProgress sx={{ color: "#a07d60" }} />
        </Box>
      );
    }

    const world = selectedWorld;

    return (
      <Box className="flex flex-col gap-6">
        {/* Title and theme */}
        <Box sx={{ display: "flex", alignItems: "flex-start", gap: 2, flexWrap: "wrap" }}>
          <Typography
            variant="h4"
            fontWeight={700}
            sx={{ color: "#1e1410", flexGrow: 1 }}
          >
            {world.name}
          </Typography>
          <Chip
            label={formatTheme(world.theme)}
            sx={{
              bgcolor: "#a07d60",
              color: "#F9F8F6",
              fontWeight: 600,
              flexShrink: 0,
              alignSelf: "center",
            }}
          />
        </Box>

        {/* Description */}
        <Typography variant="body1" sx={{ color: "#3a2820" }}>
          {world.description}
        </Typography>

        {/* Create a Character CTA */}
        <Box>
          <Button
            variant="contained"
            size="large"
            onClick={() => router.push(`/world/${worldId}/character/create`)}
            sx={{
              bgcolor: "#7d5e45",
              "&:hover": { bgcolor: "#5c4230" },
              textTransform: "none",
              fontWeight: 600,
              borderRadius: 2,
            }}
          >
            Create a Character in this World
          </Button>
        </Box>

        <Divider sx={{ borderColor: "#D9CFC7" }} />

        {/* Lore section */}
        <Box>
          <Typography
            variant="h6"
            fontWeight={700}
            sx={{ color: "#1e1410", mb: 1 }}
          >
            Lore
          </Typography>
          <Typography variant="body1" sx={{ color: "#3a2820" }}>
            {world.lore_summary}
          </Typography>
        </Box>

        <Divider sx={{ borderColor: "#D9CFC7" }} />

        {/* Factions section */}
        <Box>
          <Typography
            variant="h6"
            fontWeight={700}
            sx={{ color: "#1e1410", mb: 2 }}
          >
            Factions
          </Typography>
          {world.factions.length === 0 ? (
            <Typography variant="body2" sx={{ color: "#C9B59C" }}>
              None
            </Typography>
          ) : (
            <Box className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {world.factions.map((faction) => (
                <FactionCard key={faction.name} faction={faction} />
              ))}
            </Box>
          )}
        </Box>

        <Divider sx={{ borderColor: "#D9CFC7" }} />

        {/* Bosses section */}
        <Box>
          <Typography
            variant="h6"
            fontWeight={700}
            sx={{ color: "#1e1410", mb: 2 }}
          >
            Bosses
          </Typography>
          {world.bosses.length === 0 ? (
            <Typography variant="body2" sx={{ color: "#C9B59C" }}>
              None
            </Typography>
          ) : (
            <Box className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {world.bosses.map((boss) => (
                <BossCard key={boss.name} boss={boss} />
              ))}
            </Box>
          )}
        </Box>
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
            onClick={() => router.push("/world")}
            sx={{ textTransform: "none", color: "#5c4230" }}
          >
            Back to Worlds
          </Button>
        </Box>

        {/* Content */}
        <Box sx={{ px: { xs: 3, sm: 6 }, py: 4, maxWidth: 1200, mx: "auto" }}>
          {renderContent()}
        </Box>
      </Box>
    </ProtectedRoute>
  );
}
