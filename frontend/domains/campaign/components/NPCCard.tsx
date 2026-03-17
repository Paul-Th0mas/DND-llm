"use client";

import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Typography from "@mui/material/Typography";
import type { CampaignNPC } from "@/domains/campaign/types";

/** Props for the NPCCard component. */
export interface NPCCardProps {
  /** The campaign NPC to display. */
  readonly npc: CampaignNPC;
  /** When true, the DM-only secret section is rendered. */
  readonly isDM: boolean;
}

/**
 * Displays a single campaign NPC card with name, species, role, personality, and stat block reference.
 * When isDM is true, also renders the NPC's secret in a styled DM-only section.
 */
export function NPCCard({ npc, isDM }: NPCCardProps): React.ReactElement {
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
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, flexWrap: "wrap" }}>
        <Typography variant="subtitle2" fontWeight={600}>
          {npc.name}
        </Typography>
        <Chip label={npc.species} size="small" variant="outlined" />
        <Chip label={npc.role} size="small" color="primary" variant="outlined" />
      </Box>

      <Typography variant="body2" color="text.secondary">
        {npc.personality}
      </Typography>

      {npc.stat_block_ref && (
        <Typography variant="caption" color="text.disabled">
          Stat block: {npc.stat_block_ref}
        </Typography>
      )}

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
            DM Only — Secret
          </Typography>
          <Typography variant="body2" sx={{ color: "#EFE9E3" }}>
            {npc.secret}
          </Typography>
        </Box>
      )}
    </Box>
  );
}
