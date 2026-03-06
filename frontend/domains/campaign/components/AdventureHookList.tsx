"use client";

import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Typography from "@mui/material/Typography";
import type { AdventureHookResponse } from "@/domains/campaign/types";

// Display labels and colours for each narrative pillar.
const PILLAR_META: Record<string, { label: string; color: "error" | "success" | "info" }> = {
  COMBAT: { label: "Combat", color: "error" },
  EXPLORATION: { label: "Exploration", color: "success" },
  SOCIAL: { label: "Social", color: "info" },
};

/** Props for the AdventureHookList component. */
interface AdventureHookListProps {
  readonly hooks: readonly AdventureHookResponse[];
}

/**
 * Renders adventure hooks grouped by narrative pillar (Combat / Exploration / Social).
 * Each hook shows a pillar badge, the hook description, and an optional connected NPC.
 */
export function AdventureHookList({ hooks }: AdventureHookListProps): React.ReactElement {
  // Group hooks by pillar while preserving insertion order within each group.
  const pillars = ["COMBAT", "EXPLORATION", "SOCIAL"] as const;
  const grouped = pillars
    .map((pillar) => ({
      pillar,
      hooks: hooks.filter((h) => h.pillar === pillar),
    }))
    .filter((group) => group.hooks.length > 0);

  // Also collect hooks with unknown pillars so nothing is silently dropped.
  const knownPillars = new Set(pillars as readonly string[]);
  const unknown = hooks.filter((h) => !knownPillars.has(h.pillar));

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      {grouped.map(({ pillar, hooks: pillarHooks }) => {
        const meta = PILLAR_META[pillar] ?? { label: pillar, color: "info" as const };
        return (
          <Box key={pillar}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
              <Chip label={meta.label} size="small" color={meta.color} />
            </Box>
            <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
              {pillarHooks.map((hook, i) => (
                <Box
                  key={i}
                  sx={{
                    p: 1.5,
                    border: "1px solid",
                    borderColor: "divider",
                    borderRadius: 1,
                    bgcolor: "background.paper",
                  }}
                >
                  <Typography variant="body2" color="text.primary">
                    {hook.hook}
                  </Typography>
                  {hook.connected_npc !== null && (
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                      Connected NPC: {hook.connected_npc}
                    </Typography>
                  )}
                </Box>
              ))}
            </Box>
          </Box>
        );
      })}

      {unknown.length > 0 && (
        <Box>
          <Typography variant="caption" color="text.secondary" sx={{ mb: 1 }}>
            Other hooks
          </Typography>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
            {unknown.map((hook, i) => (
              <Box
                key={i}
                sx={{
                  p: 1.5,
                  border: "1px solid",
                  borderColor: "divider",
                  borderRadius: 1,
                }}
              >
                <Typography variant="body2">{hook.hook}</Typography>
              </Box>
            ))}
          </Box>
        </Box>
      )}
    </Box>
  );
}
