"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Divider from "@mui/material/Divider";
import Typography from "@mui/material/Typography";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { getCharacterSheet } from "@/domains/character/services/character.service";
import { ApiError } from "@/lib/api/client";
import type { AbilityKey, CharacterSheet } from "@/domains/character/types";

/** Ordered list of ability score display metadata. */
const ABILITY_LABELS: { key: AbilityKey; abbrev: string }[] = [
  { key: "strength", abbrev: "STR" },
  { key: "dexterity", abbrev: "DEX" },
  { key: "constitution", abbrev: "CON" },
  { key: "intelligence", abbrev: "INT" },
  { key: "wisdom", abbrev: "WIS" },
  { key: "charisma", abbrev: "CHA" },
];

/** Props for CharacterDetailPageContent. */
export interface CharacterDetailPageContentProps {
  /** The UUID of the campaign this character belongs to. */
  readonly campaignId: string;
  /** The UUID of the character to display. */
  readonly characterId: string;
}

/**
 * Computes the D&D ability score modifier from a raw score.
 * Formula: floor((score - 10) / 2).
 * Returns a string prefixed with "+" for non-negative values (e.g. "+2", "+0", "-1").
 * @param score - The raw ability score (typically 1-20).
 * @returns The formatted modifier string.
 */
function formatModifier(score: number): string {
  const mod = Math.floor((score - 10) / 2);
  return mod >= 0 ? `+${mod}` : `${mod}`;
}

/**
 * Client component for the character sheet page (US-030).
 * Fetches the character by ID and renders a read-only sheet with:
 * - Header: name, class, and species chips
 * - Ability scores: 6-cell grid with score and computed modifier
 * - Background block
 * - Traits list (omitted when empty)
 * - Back link to the campaign detail page
 */
export function CharacterDetailPageContent({
  campaignId,
  characterId,
}: CharacterDetailPageContentProps): React.ReactElement {
  const [character, setCharacter] = useState<CharacterSheet | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!characterId) return;

    let cancelled = false;
    const token = localStorage.getItem("access_token") ?? "";

    async function fetchCharacter(): Promise<void> {
      setIsLoading(true);
      setError(null);
      try {
        const data = await getCharacterSheet(characterId, token);
        if (!cancelled) {
          setCharacter(data);
        }
      } catch (err: unknown) {
        if (!cancelled) {
          if (err instanceof ApiError) {
            if (err.status === 404) {
              setError("Character not found.");
            } else if (err.status === 401 || err.status === 403) {
              setError("You are not authorised to view this character.");
            } else {
              setError(`Failed to load character: ${err.detail}`);
            }
          } else {
            setError("Failed to load the character. Please try again.");
          }
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    void fetchCharacter();

    return () => {
      cancelled = true;
    };
  }, [characterId]);

  return (
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
          component={Link}
          href={`/campaign/${campaignId}`}
          startIcon={<ArrowBackIcon />}
          sx={{ textTransform: "none", color: "#5c4230" }}
        >
          Campaign
        </Button>
        <Typography variant="h6" fontWeight={700} sx={{ ml: 1, color: "#1e1410" }}>
          Character Sheet
        </Typography>
      </Box>

      {/* Content */}
      <Box sx={{ px: { xs: 3, sm: 6 }, py: 4, maxWidth: 720, mx: "auto" }}>
        {isLoading && (
          <Box sx={{ display: "flex", justifyContent: "center", py: 10 }}>
            <CircularProgress />
          </Box>
        )}

        {!isLoading && error !== null && (
          <Alert severity="error">{error}</Alert>
        )}

        {!isLoading && error === null && character !== null && (
          <Box sx={{ display: "flex", flexDirection: "column", gap: 4 }}>
            {/* Header: name + class/species chips */}
            <Box>
              <Typography
                variant="h4"
                fontWeight={700}
                sx={{ color: "#1e1410", mb: 1.5 }}
              >
                {character.name}
              </Typography>
              <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
                <Chip
                  label={character.character_class.display_name}
                  size="small"
                  sx={{
                    bgcolor: "#a07d60",
                    color: "#F9F8F6",
                    fontWeight: 600,
                  }}
                />
                <Chip
                  label={character.species.display_name}
                  size="small"
                  sx={{
                    bgcolor: "#C9B59C",
                    color: "#1e1410",
                    fontWeight: 600,
                  }}
                />
              </Box>
            </Box>

            <Divider sx={{ borderColor: "#D9CFC7" }} />

            {/* Ability Scores — 6-cell grid */}
            <Box>
              <Typography
                variant="subtitle1"
                fontWeight={600}
                gutterBottom
                sx={{ color: "#1e1410" }}
              >
                Ability Scores
              </Typography>
              <Box
                sx={{
                  display: "grid",
                  gridTemplateColumns: "repeat(3, 1fr)",
                  gap: 2,
                }}
                className="sm:grid-cols-6"
              >
                {ABILITY_LABELS.map(({ key, abbrev }) => {
                  const score = character.ability_scores[key];
                  return (
                    <Box
                      key={key}
                      sx={{
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        gap: 0.5,
                        p: 2,
                        border: "1px solid #D9CFC7",
                        borderRadius: 2,
                        bgcolor: "#EFE9E3",
                      }}
                    >
                      <Typography
                        variant="caption"
                        fontWeight={700}
                        sx={{ color: "#7d5e45", letterSpacing: "0.08em" }}
                      >
                        {abbrev}
                      </Typography>
                      <Typography
                        variant="h5"
                        fontWeight={700}
                        sx={{ color: "#1e1410", lineHeight: 1 }}
                      >
                        {score}
                      </Typography>
                      <Chip
                        label={formatModifier(score)}
                        size="small"
                        sx={{
                          bgcolor: "#D9CFC7",
                          color: "#3a2820",
                          fontWeight: 700,
                          fontSize: "0.75rem",
                          height: 22,
                        }}
                      />
                    </Box>
                  );
                })}
              </Box>
            </Box>

            <Divider sx={{ borderColor: "#D9CFC7" }} />

            {/* Background */}
            <Box>
              <Typography
                variant="subtitle1"
                fontWeight={600}
                gutterBottom
                sx={{ color: "#1e1410" }}
              >
                Background
              </Typography>
              <Typography variant="body1" sx={{ color: "#3a2820" }}>
                {character.background}
              </Typography>
            </Box>

            {/* Traits — omitted when the species has no traits */}
            {character.species.traits.length > 0 && (
              <>
                <Divider sx={{ borderColor: "#D9CFC7" }} />
                <Box>
                  <Typography
                    variant="subtitle1"
                    fontWeight={600}
                    gutterBottom
                    sx={{ color: "#1e1410" }}
                  >
                    Traits
                  </Typography>
                  <Box
                    component="ul"
                    sx={{ m: 0, pl: 2.5, display: "flex", flexDirection: "column", gap: 0.5 }}
                  >
                    {character.species.traits.map((trait) => (
                      <Typography
                        key={trait}
                        component="li"
                        variant="body2"
                        sx={{ color: "#3a2820" }}
                      >
                        {trait}
                      </Typography>
                    ))}
                  </Box>
                </Box>
              </>
            )}
          </Box>
        )}
      </Box>
    </Box>
  );
}
