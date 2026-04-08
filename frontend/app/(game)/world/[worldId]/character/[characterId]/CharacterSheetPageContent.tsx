"use client";

import { useEffect, useReducer, useState } from "react";
import { useRouter } from "next/navigation";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Skeleton from "@mui/material/Skeleton";
import Typography from "@mui/material/Typography";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { ProtectedRoute } from "@/shared/components/ProtectedRoute";
import { CharacterSheet } from "@/domains/character/components/CharacterSheet";
import { getCharacterSheet } from "@/domains/character/services/character.service";
import { ApiError } from "@/lib/api/client";
import type { CharacterSheet as CharacterSheetData } from "@/domains/character/types";

/** Props for the world-scoped CharacterSheetPageContent. */
export interface CharacterSheetPageContentProps {
  /** The UUID of the world this character belongs to. */
  readonly worldId: string;
  /** The UUID of the character to display. */
  readonly characterId: string;
}

/**
 * Client component for the world-scoped character sheet page.
 * Fetches the character sheet for the authenticated player and renders it.
 * Returns 403 if the character belongs to another player, 404 if not found.
 * Route: /world/{worldId}/character/{characterId}
 */
export function CharacterSheetPageContent({
  worldId,
  characterId,
}: CharacterSheetPageContentProps): React.ReactElement {
  const router = useRouter();
  const [character, setCharacter] = useState<CharacterSheetData | null>(null);
  const [{ isLoading, error }, dispatch] = useReducer(
    (
      state: { isLoading: boolean; error: string | null },
      action:
        | { type: "start" }
        | { type: "done" }
        | { type: "error"; message: string }
    ) => {
      switch (action.type) {
        case "start": return { isLoading: true, error: null };
        case "done": return { ...state, isLoading: false };
        case "error": return { isLoading: false, error: action.message };
      }
    },
    { isLoading: true, error: null }
  );

  // Read token on the client side only — localStorage is not available in SSR.
  const token =
    typeof window !== "undefined"
      ? (localStorage.getItem("access_token") ?? "")
      : "";

  useEffect(() => {
    if (!characterId || !token) return;

    let cancelled = false;
    dispatch({ type: "start" });

    getCharacterSheet(characterId, token)
      .then((data) => {
        if (!cancelled) setCharacter(data);
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          if (err instanceof ApiError) {
            if (err.status === 403) {
              dispatch({
                type: "error",
                message: "You do not have permission to view this character sheet.",
              });
            } else if (err.status === 404) {
              dispatch({ type: "error", message: "Character not found." });
            } else {
              dispatch({
                type: "error",
                message: `Failed to load character sheet: ${err.detail}`,
              });
            }
          } else {
            dispatch({ type: "error", message: "Failed to load the character sheet." });
          }
        }
      })
      .finally(() => {
        if (!cancelled) dispatch({ type: "done" });
      });

    return () => {
      cancelled = true;
    };
  }, [characterId, token]);

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
            Character Sheet
          </Typography>
        </Box>

        {/* Content */}
        <Box sx={{ px: { xs: 2, sm: 4 }, py: 4, maxWidth: 1100, mx: "auto" }}>
          {isLoading && (
            <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
              <Skeleton variant="text" width="40%" height={48} />
              <Skeleton variant="rectangular" height={160} />
              <Skeleton variant="text" width="60%" />
              <Skeleton variant="rectangular" height={120} />
            </Box>
          )}

          {!isLoading && error !== null && (
            <Alert severity="error">{error}</Alert>
          )}

          {!isLoading && error === null && character !== null && (
            <CharacterSheet character={character} />
          )}
        </Box>
      </Box>
    </ProtectedRoute>
  );
}
