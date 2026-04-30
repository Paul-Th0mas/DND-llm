"use client";

import { useEffect, useState } from "react";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import Typography from "@mui/material/Typography";
import { getCampaignRoster } from "@/domains/character/services/character.service";
import { ApiError } from "@/lib/api/client";
import type { CampaignRosterEntry } from "@/domains/character/types";

/** Props for CampaignPartyRoster. */
export interface CampaignPartyRosterProps {
  /** The UUID of the campaign whose roster is displayed. */
  readonly campaignId: string;
  /** The JWT access token of the authenticated DM. */
  readonly token: string;
}

/**
 * Displays the full character roster for a campaign, visible to the DM only.
 * Fetches GET /api/v1/campaigns/{campaignId}/characters and renders each
 * character entry with their name, class, species, and linked player username.
 *
 * @param props - CampaignPartyRosterProps including campaignId and token.
 */
export function CampaignPartyRoster({
  campaignId,
  token,
}: CampaignPartyRosterProps): React.ReactElement {
  const [entries, setEntries] = useState<readonly CampaignRosterEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetch(): Promise<void> {
      setLoading(true);
      setError(null);
      try {
        const data = await getCampaignRoster(campaignId, token);
        if (!cancelled) {
          setEntries(data.characters);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof ApiError ? err.detail : "Failed to load party roster."
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void fetch();
    return () => {
      cancelled = true;
    };
  }, [campaignId, token]);

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 2 }}>
        <CircularProgress size={24} />
      </Box>
    );
  }

  if (error !== null) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (entries.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary">
        No characters linked yet.
      </Typography>
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
      {entries.map((entry) => (
        <Box
          key={entry.id}
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            p: 1.5,
            border: "1px solid",
            borderColor: "divider",
            borderRadius: 1,
          }}
        >
          <Box>
            <Typography variant="body2" fontWeight={600}>
              {entry.name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {entry.character_class.display_name} - {entry.species.display_name}
            </Typography>
          </Box>
          <Typography variant="caption" color="text.secondary">
            {entry.player.username}
          </Typography>
        </Box>
      ))}
    </Box>
  );
}
