"use client";

import { useCallback, useEffect, useState } from "react";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Typography from "@mui/material/Typography";
import { getCampaignRoster } from "@/domains/character/services/character.service";
import { ApiError } from "@/lib/api/client";
import type { AbilityKey, CampaignRosterEntry } from "@/domains/character/types";

/** Ability abbreviations used in the compact score strip. */
const ABILITY_ABBREVS: { key: AbilityKey; abbrev: string }[] = [
  { key: "strength", abbrev: "STR" },
  { key: "dexterity", abbrev: "DEX" },
  { key: "constitution", abbrev: "CON" },
  { key: "intelligence", abbrev: "INT" },
  { key: "wisdom", abbrev: "WIS" },
  { key: "charisma", abbrev: "CHA" },
];

/** Props for CampaignPartyRoster. */
export interface CampaignPartyRosterProps {
  /** The UUID of the campaign whose roster to display. */
  readonly campaignId: string;
  /** The JWT access token of the authenticated DM. */
  readonly token: string;
}

/**
 * Displays the party roster for a campaign (DM-only, US-031).
 * Shows all characters linked to the campaign with class, species,
 * ability score strip, and the owning player's username.
 * Handles loading, empty, and error states.
 */
export function CampaignPartyRoster({
  campaignId,
  token,
}: CampaignPartyRosterProps): React.ReactElement {
  const [characters, setCharacters] = useState<readonly CampaignRosterEntry[]>(
    []
  );
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRoster = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getCampaignRoster(campaignId, token);
      setCharacters(data.characters);
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        if (err.status === 403) {
          setError("You do not have permission to view this campaign.");
        } else {
          setError(`Failed to load party roster: ${err.detail}`);
        }
      } else {
        setError("Failed to load the party roster. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  }, [campaignId, token]);

  useEffect(() => {
    void fetchRoster();
  }, [fetchRoster]);

  if (isLoading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
        <CircularProgress size={28} />
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
          onClick={() => void fetchRoster()}
          sx={{ alignSelf: "flex-start", textTransform: "none" }}
        >
          Retry
        </Button>
      </Box>
    );
  }

  if (characters.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary">
        No characters have joined this campaign yet.
      </Typography>
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
      {characters.map((entry) => (
        <Card
          key={entry.id}
          variant="outlined"
          sx={{
            bgcolor: "#EFE9E3",
            border: "1px solid #D9CFC7",
          }}
        >
          <CardContent>
            {/* Character name and class/species */}
            <Box
              sx={{
                display: "flex",
                alignItems: "flex-start",
                justifyContent: "space-between",
                flexWrap: "wrap",
                gap: 1,
                mb: 1,
              }}
            >
              <Box>
                <Typography
                  variant="subtitle1"
                  fontWeight={700}
                  sx={{ color: "#1e1410" }}
                >
                  {entry.name}
                </Typography>
                <Typography variant="body2" sx={{ color: "#7d5e45" }}>
                  {entry.character_class.display_name} &bull; {entry.species.display_name}
                </Typography>
              </Box>
              <Typography variant="caption" color="text.secondary">
                Player: {entry.player.username}
              </Typography>
            </Box>

            {/* Compact ability score strip */}
            <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
              {ABILITY_ABBREVS.map(({ key, abbrev }) => (
                <Chip
                  key={key}
                  label={`${abbrev} ${entry.ability_scores[key]}`}
                  size="small"
                  sx={{
                    bgcolor: "#D9CFC7",
                    color: "#3a2820",
                    fontWeight: 600,
                    fontSize: "0.7rem",
                  }}
                />
              ))}
            </Box>
          </CardContent>
        </Card>
      ))}
    </Box>
  );
}
