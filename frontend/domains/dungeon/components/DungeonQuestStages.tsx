"use client";

import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import type { DungeonQuestResponse } from "../types";

/** Props for the DungeonQuestStages component. */
interface DungeonQuestStagesProps {
  /** Ordered list of narrative milestone descriptions from the dungeon quest. */
  readonly stages: DungeonQuestResponse["stages"];
}

/**
 * Renders an ordered list of quest stages with numbered step indicators.
 * Used inside GeneratedDungeonView to display the main quest progression.
 */
export function DungeonQuestStages({ stages }: DungeonQuestStagesProps): React.ReactElement {
  return (
    <Box
      component="ol"
      sx={{
        listStyle: "none",
        p: 0,
        m: 0,
        display: "flex",
        flexDirection: "column",
        gap: 1.5,
      }}
    >
      {stages.map((stage, index) => (
        <Box
          component="li"
          key={index}
          sx={{ display: "flex", gap: 1.5, alignItems: "flex-start" }}
        >
          {/* Numbered step indicator */}
          <Box
            sx={{
              minWidth: 24,
              height: 24,
              borderRadius: "50%",
              bgcolor: "primary.main",
              color: "primary.contrastText",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "0.7rem",
              fontWeight: 700,
              flexShrink: 0,
              mt: 0.25,
            }}
            aria-hidden="true"
          >
            {index + 1}
          </Box>
          <Typography variant="body2" color="text.secondary">
            {stage}
          </Typography>
        </Box>
      ))}
    </Box>
  );
}
