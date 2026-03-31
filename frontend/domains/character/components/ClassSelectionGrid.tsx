"use client";

import { useEffect, useState } from "react";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Skeleton from "@mui/material/Skeleton";
import Typography from "@mui/material/Typography";
import { AppCard } from "@/shared/components/AppCard";
import { getCharacterClasses } from "@/domains/character/services/character.service";
import { ApiError } from "@/lib/api/client";
import type { CharacterClass } from "@/domains/character/types";

/** Props for ClassSelectionGrid. */
export interface ClassSelectionGridProps {
  /** The world theme used to filter available classes. */
  readonly worldTheme: string;
  /** The currently selected class ID, or null if none chosen. */
  readonly selectedClassId: string | null;
  /** Callback invoked when the player selects a class card. */
  readonly onSelect: (classId: string) => void;
}

/**
 * Displays a grid of selectable character class cards filtered by world theme.
 * Handles loading, empty, and error states as per US-026 acceptance criteria.
 * Each card shows: display_name, hit_die as "d{n}", primary_ability,
 * and a "Spellcaster" chip if the class has a spellcasting_ability.
 * Uses AppCard with onClick and selected props for interactive selection.
 */
export function ClassSelectionGrid({
  worldTheme,
  selectedClassId,
  onSelect,
}: ClassSelectionGridProps): React.ReactElement {
  const [classes, setClasses] = useState<readonly CharacterClass[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    getCharacterClasses(worldTheme)
      .then((data) => {
        if (!cancelled) setClasses(data.classes);
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          if (err instanceof ApiError) {
            setError(`Failed to load classes: ${err.detail}`);
          } else {
            setError("Failed to load character classes.");
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
          <Skeleton key={i} variant="rectangular" height={140} sx={{ borderRadius: 2 }} />
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
            getCharacterClasses(worldTheme)
              .then((data) => setClasses(data.classes))
              .catch(() => setError("Failed to load character classes."))
              .finally(() => setIsLoading(false));
          }}
          sx={{ alignSelf: "flex-start", textTransform: "none" }}
        >
          Retry
        </Button>
      </Box>
    );
  }

  if (classes.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary">
        No classes available for this world theme.
      </Typography>
    );
  }

  return (
    <Box className="grid grid-cols-2 gap-4 sm:grid-cols-3">
      {classes.map((cls, index) => {
        const chips = [
          <Chip
            key="hitdie"
            label={`d${cls.hit_die}`}
            size="small"
            variant="outlined"
            sx={{ fontSize: "0.7rem" }}
          />,
          <Chip
            key="ability"
            label={cls.primary_ability}
            size="small"
            variant="outlined"
            sx={{ fontSize: "0.7rem" }}
          />,
        ];

        // Spellcaster chip — only added when a spellcasting ability exists.
        if (cls.spellcasting_ability !== null) {
          chips.push(
            <Chip
              key="spellcaster"
              label="Spellcaster"
              size="small"
              sx={{
                bgcolor: "#a07d60",
                color: "#F9F8F6",
                fontWeight: 600,
                fontSize: "0.65rem",
                height: 20,
              }}
            />
          );
        }

        return (
          <AppCard
            key={cls.id}
            title={cls.display_name}
            chips={chips}
            onClick={() => onSelect(cls.id)}
            selected={cls.id === selectedClassId}
            staggerIndex={index}
          />
        );
      })}
    </Box>
  );
}
