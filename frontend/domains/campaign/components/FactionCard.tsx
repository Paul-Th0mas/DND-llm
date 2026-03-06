"use client";

import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Collapse from "@mui/material/Collapse";
import IconButton from "@mui/material/IconButton";
import Typography from "@mui/material/Typography";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import { useState } from "react";
import type { FactionResponse } from "@/domains/campaign/types";

/** Props for the FactionCard component. */
interface FactionCardProps {
  readonly faction: FactionResponse;
  /** When true the DM secret (hidden_agenda) toggle is rendered. */
  readonly showDmControls: boolean;
}

/**
 * Displays a single campaign faction with its goals, public reputation,
 * and (for the DM) a toggleable hidden agenda section.
 */
export function FactionCard({ faction, showDmControls }: FactionCardProps): React.ReactElement {
  const [agendaVisible, setAgendaVisible] = useState(false);

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
      <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <Typography variant="subtitle2" fontWeight={600}>
          {faction.name}
        </Typography>
        {showDmControls && (
          <IconButton
            size="small"
            onClick={() => setAgendaVisible((v) => !v)}
            aria-label={agendaVisible ? "Hide hidden agenda" : "Reveal hidden agenda"}
          >
            {agendaVisible ? <VisibilityOffIcon fontSize="small" /> : <VisibilityIcon fontSize="small" />}
          </IconButton>
        )}
      </Box>

      <Box sx={{ display: "flex", gap: 0.5, flexWrap: "wrap" }}>
        <Chip label="Goals" size="small" variant="outlined" />
        <Typography variant="body2" color="text.secondary">
          {faction.goals}
        </Typography>
      </Box>

      <Box sx={{ display: "flex", gap: 0.5, flexWrap: "wrap" }}>
        <Chip label="Public reputation" size="small" variant="outlined" />
        <Typography variant="body2" color="text.secondary">
          {faction.public_reputation}
        </Typography>
      </Box>

      {showDmControls && (
        <Collapse in={agendaVisible}>
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
              DM only — Hidden Agenda
            </Typography>
            <Typography variant="body2" color="text.primary" sx={{ mt: 0.5 }}>
              {faction.hidden_agenda}
            </Typography>
          </Box>
        </Collapse>
      )}
    </Box>
  );
}
