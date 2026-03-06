"use client";

import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Collapse from "@mui/material/Collapse";
import IconButton from "@mui/material/IconButton";
import Typography from "@mui/material/Typography";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import { useState } from "react";
import type { NpcResponse } from "@/domains/campaign/types";

/** Props for the NPCCard component. */
interface NPCCardProps {
  readonly npc: NpcResponse;
  /** When true the DM secret toggle is rendered. */
  readonly showDmControls: boolean;
}

/**
 * Displays a single key NPC with species, role, personality, and stat block reference.
 * For the DM, a toggleable secret section reveals information hidden from players.
 */
export function NPCCard({ npc, showDmControls }: NPCCardProps): React.ReactElement {
  const [secretVisible, setSecretVisible] = useState(false);

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
      {/* Header row */}
      <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, flexWrap: "wrap" }}>
          <Typography variant="subtitle2" fontWeight={600}>
            {npc.name}
          </Typography>
          <Chip label={npc.species} size="small" variant="outlined" />
          <Chip label={npc.role} size="small" color="primary" />
        </Box>
        {showDmControls && (
          <IconButton
            size="small"
            onClick={() => setSecretVisible((v) => !v)}
            aria-label={secretVisible ? "Hide NPC secret" : "Reveal NPC secret"}
          >
            {secretVisible ? <VisibilityOffIcon fontSize="small" /> : <VisibilityIcon fontSize="small" />}
          </IconButton>
        )}
      </Box>

      <Typography variant="body2" color="text.secondary">
        {npc.personality}
      </Typography>

      {npc.stat_block_ref !== null && (
        <Typography variant="caption" color="text.secondary">
          Stat block: {npc.stat_block_ref}
        </Typography>
      )}

      {showDmControls && (
        <Collapse in={secretVisible}>
          <Box
            sx={{
              mt: 1,
              p: 1.5,
              bgcolor: "warning.light",
              borderRadius: 1,
              opacity: 0.9,
            }}
          >
            <Typography variant="caption" fontWeight={600} color="warning.dark">
              DM only — Secret
            </Typography>
            <Typography variant="body2" color="text.primary" sx={{ mt: 0.5 }}>
              {npc.secret}
            </Typography>
          </Box>
        </Collapse>
      )}
    </Box>
  );
}
