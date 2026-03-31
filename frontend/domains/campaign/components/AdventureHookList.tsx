"use client";

import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Typography from "@mui/material/Typography";
import { AppCard } from "@/shared/components/AppCard";
import type { AdventureHook } from "@/domains/campaign/types";

/** Props for the AdventureHookList component. */
export interface AdventureHookListProps {
  readonly hooks: readonly AdventureHook[];
}

/** Pillar display configuration — label and MUI chip color. */
const PILLAR_CONFIG = {
  combat: { label: "Combat", color: "error" },
  exploration: { label: "Exploration", color: "success" },
  social: { label: "Social", color: "info" },
} as const;

type PillarColor = "error" | "success" | "info";

/**
 * Renders adventure hooks grouped by narrative pillar (Combat, Exploration, Social).
 * Each hook is displayed as an AppCard with the hook text as children and the
 * connected NPC reference as the subtitle when present.
 */
export function AdventureHookList({ hooks }: AdventureHookListProps): React.ReactElement {
  const pillars: Array<"combat" | "exploration" | "social"> = [
    "combat",
    "exploration",
    "social",
  ];

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      {pillars.map((pillar) => {
        const pillarHooks = hooks.filter((h) => h.pillar === pillar);
        if (pillarHooks.length === 0) return null;

        const config = PILLAR_CONFIG[pillar];

        return (
          <Box key={pillar}>
            {/* Pillar label */}
            <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1.5 }}>
              <Chip
                label={config.label}
                size="small"
                color={config.color as PillarColor}
                variant="outlined"
              />
            </Box>

            {/* Hooks in this pillar */}
            <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
              {pillarHooks.map((hook, i) => (
                <AppCard
                  key={i}
                  subtitle={
                    hook.connected_npc
                      ? `Connected NPC: ${hook.connected_npc}`
                      : undefined
                  }
                  staggerIndex={i}
                >
                  <Typography variant="body2">{hook.hook}</Typography>
                </AppCard>
              ))}
            </Box>
          </Box>
        );
      })}
    </Box>
  );
}
