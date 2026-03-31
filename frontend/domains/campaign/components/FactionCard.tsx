"use client";

import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Typography from "@mui/material/Typography";
import { AppCard } from "@/shared/components/AppCard";
import type { CampaignFaction } from "@/domains/campaign/types";

/** Props for the FactionCard component. */
export interface FactionCardProps {
  /** The campaign faction to display. */
  readonly faction: CampaignFaction;
  /** When true, the DM-only hidden agenda section is rendered. */
  readonly isDM: boolean;
}

/**
 * Displays a single campaign faction card with name, goals, and public reputation.
 * When isDM is true, also renders the hidden agenda in a styled DM-only section.
 * Uses AppCard for consistent theming across card style modes.
 */
export function FactionCard({ faction, isDM }: FactionCardProps): React.ReactElement {
  return (
    <AppCard
      title={faction.name}
      chips={[
        <Chip key="faction" label="Faction" size="small" variant="outlined" />,
      ]}
    >
      <Typography variant="caption" color="text.secondary">
        {faction.public_reputation}
      </Typography>

      <Typography variant="body2" color="text.secondary">
        {faction.goals}
      </Typography>

      {isDM && (
        <Box
          sx={{
            mt: 0.5,
            p: 1.5,
            borderRadius: 1,
            // Uses parchment-700 as a muted dark background to signal DM-only content.
            bgcolor: "#5c4230",
            color: "#F9F8F6",
          }}
        >
          <Typography
            variant="caption"
            sx={{ fontWeight: 700, display: "block", mb: 0.5, color: "#C9B59C" }}
          >
            DM Only — Hidden Agenda
          </Typography>
          <Typography variant="body2" sx={{ color: "#EFE9E3" }}>
            {faction.hidden_agenda}
          </Typography>
        </Box>
      )}
    </AppCard>
  );
}
