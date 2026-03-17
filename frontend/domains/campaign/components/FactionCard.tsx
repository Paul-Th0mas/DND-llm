"use client";

import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Typography from "@mui/material/Typography";
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
 */
export function FactionCard({ faction, isDM }: FactionCardProps): React.ReactElement {
  return (
    <Box
      sx={{
        p: 2,
        border: "1px solid",
        borderColor: "divider",
        borderRadius: 2,
        bgcolor: "background.paper",
        display: "flex",
        flexDirection: "column",
        gap: 1,
      }}
    >
      <Typography variant="subtitle2" fontWeight={600}>
        {faction.name}
      </Typography>

      <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap", alignItems: "center" }}>
        <Chip label="Faction" size="small" variant="outlined" />
        <Typography variant="caption" color="text.secondary">
          {faction.public_reputation}
        </Typography>
      </Box>

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
    </Box>
  );
}
