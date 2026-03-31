"use client";

import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Typography from "@mui/material/Typography";
import { AppCard } from "@/shared/components/AppCard";
import type { CampaignNPC } from "@/domains/campaign/types";

/** Props for the NPCCard component. */
export interface NPCCardProps {
  /** The campaign NPC to display. */
  readonly npc: CampaignNPC;
  /** When true, the DM-only secret section is rendered. */
  readonly isDM: boolean;
}

/**
 * Displays a single campaign NPC card with name, species chip, role chip,
 * personality, and stat block reference. When isDM is true, also renders the
 * NPC's secret in a styled DM-only section. Uses AppCard for consistent theming.
 */
export function NPCCard({ npc, isDM }: NPCCardProps): React.ReactElement {
  return (
    <AppCard
      title={npc.name}
      chips={[
        <Chip key="species" label={npc.species} size="small" variant="outlined" />,
        <Chip key="role" label={npc.role} size="small" color="primary" variant="outlined" />,
      ]}
    >
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
    </AppCard>
  );
}
