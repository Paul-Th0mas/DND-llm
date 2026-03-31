"use client";

import { useEffect, useState } from "react";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Collapse from "@mui/material/Collapse";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Skeleton from "@mui/material/Skeleton";
import Typography from "@mui/material/Typography";
import { AppCard } from "@/shared/components/AppCard";
import { getCharacterSpecies } from "@/domains/character/services/character.service";
import { ApiError } from "@/lib/api/client";
import type { CharacterSpecies } from "@/domains/character/types";

// Maximum number of traits shown before "Show more" expands the list.
const TRAITS_PREVIEW_COUNT = 3 as const;

/** Props for SpeciesSelectionGrid. */
export interface SpeciesSelectionGridProps {
  /** The world theme used to filter available species. */
  readonly worldTheme: string;
  /** The currently selected species ID, or null if none chosen. */
  readonly selectedSpeciesId: string | null;
  /** Callback invoked when the player selects a species card. */
  readonly onSelect: (speciesId: string) => void;
}

/**
 * Displays a grid of selectable character species cards filtered by world theme.
 * Handles loading, empty, and error states as per US-027 acceptance criteria.
 * Each card shows: display_name, size, speed as "{n} ft", and traits (up to 3,
 * expandable to show all). archetype_key is never shown to the player.
 * Uses AppCard with onClick and selected props for interactive selection.
 */
export function SpeciesSelectionGrid({
  worldTheme,
  selectedSpeciesId,
  onSelect,
}: SpeciesSelectionGridProps): React.ReactElement {
  const [species, setSpecies] = useState<readonly CharacterSpecies[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // Tracks which card has its traits expanded (by species id).
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    getCharacterSpecies(worldTheme)
      .then((data) => {
        if (!cancelled) setSpecies(data.species);
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          if (err instanceof ApiError) {
            setError(`Failed to load species: ${err.detail}`);
          } else {
            setError("Failed to load character species.");
          }
        }
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [worldTheme]);

  if (isLoading) {
    return (
      <Box className="grid grid-cols-2 gap-4 sm:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} variant="rectangular" height={160} sx={{ borderRadius: 2 }} />
        ))}
      </Box>
    );
  }

  if (error !== null) {
    return (
      <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
        <Alert severity="error">{error}</Alert>
        <Button
          variant="outlined"
          size="small"
          onClick={() => {
            setError(null);
            setIsLoading(true);
            getCharacterSpecies(worldTheme)
              .then((data) => setSpecies(data.species))
              .catch(() => setError("Failed to load character species."))
              .finally(() => setIsLoading(false));
          }}
          sx={{ alignSelf: "flex-start", textTransform: "none" }}
        >
          Retry
        </Button>
      </Box>
    );
  }

  if (species.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary">
        No species available for this world theme.
      </Typography>
    );
  }

  return (
    <Box className="grid grid-cols-2 gap-4 sm:grid-cols-3">
      {species.map((sp, index) => {
        const isExpanded = expandedId === sp.id;
        const hasMoreTraits = sp.traits.length > TRAITS_PREVIEW_COUNT;
        const visibleTraits = isExpanded
          ? sp.traits
          : sp.traits.slice(0, TRAITS_PREVIEW_COUNT);

        return (
          <AppCard
            key={sp.id}
            title={sp.display_name}
            chips={[
              <Chip
                key="size"
                label={sp.size}
                size="small"
                variant="outlined"
                sx={{ fontSize: "0.7rem" }}
              />,
              <Chip
                key="speed"
                label={`${sp.speed} ft`}
                size="small"
                variant="outlined"
                sx={{ fontSize: "0.7rem" }}
              />,
            ]}
            onClick={() => onSelect(sp.id)}
            selected={sp.id === selectedSpeciesId}
            staggerIndex={index}
          >
            {sp.traits.length > 0 && (
              <Box sx={{ mt: 0.5 }}>
                <List dense disablePadding>
                  {visibleTraits.map((trait, idx) => (
                    <ListItem key={idx} disableGutters disablePadding>
                      <ListItemText
                        primary={trait}
                        primaryTypographyProps={{
                          variant: "body2",
                          color: "text.secondary",
                          sx: { "&::before": { content: '"• "' } },
                        }}
                      />
                    </ListItem>
                  ))}
                </List>

                {hasMoreTraits && (
                  <Collapse in={!isExpanded}>
                    <Button
                      size="small"
                      variant="text"
                      onClick={(e) => {
                        // Stop propagation so clicking "Show more" does not
                        // trigger the AppCard onClick (species selection).
                        e.stopPropagation();
                        setExpandedId(sp.id);
                      }}
                      sx={{
                        textTransform: "none",
                        color: "#7d5e45",
                        p: 0,
                        mt: 0.5,
                        minWidth: 0,
                      }}
                    >
                      Show more ({sp.traits.length - TRAITS_PREVIEW_COUNT} more)
                    </Button>
                  </Collapse>
                )}
              </Box>
            )}
          </AppCard>
        );
      })}
    </Box>
  );
}
