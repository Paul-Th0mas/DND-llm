"use client";

import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import FormControlLabel from "@mui/material/FormControlLabel";
import Switch from "@mui/material/Switch";
import Typography from "@mui/material/Typography";
import { useState } from "react";
import { FactionCard } from "@/domains/campaign/components/FactionCard";
import { NPCCard } from "@/domains/campaign/components/NPCCard";
import { AdventureHookList } from "@/domains/campaign/components/AdventureHookList";
import type { CampaignWorldDetailResponse } from "@/domains/campaign/types";

/** Props for the CampaignWorldView component. */
interface CampaignWorldViewProps {
  readonly world: CampaignWorldDetailResponse;
  /**
   * When true the DM-only toggle switch is rendered, allowing the DM to reveal
   * hidden agendas and NPC secrets. Pass false for player-facing views.
   */
  readonly isDm: boolean;
}

/**
 * Full read-only display of a generated campaign world.
 * Shows world name, premise, starting settlement, factions, key NPCs,
 * adventure hooks by pillar, and the central conflict.
 * DMs can toggle visibility of secrets via an on-screen switch.
 */
export function CampaignWorldView({ world, isDm }: CampaignWorldViewProps): React.ReactElement {
  // DM toggle state: when on, secret sections in faction/NPC cards are visible.
  const [dmSecretsVisible, setDmSecretsVisible] = useState(false);

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 4 }}>
      {/* World header */}
      <Box>
        <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", mb: 0.5 }}>
          <Typography variant="h5" fontWeight={700}>
            {world.world_name}
          </Typography>
          {isDm && (
            <FormControlLabel
              control={
                <Switch
                  checked={dmSecretsVisible}
                  onChange={(e) => setDmSecretsVisible(e.target.checked)}
                  size="small"
                />
              }
              label={
                <Typography variant="caption" color="text.secondary">
                  Show DM secrets
                </Typography>
              }
            />
          )}
        </Box>
        <Typography variant="body1" color="text.secondary">
          {world.premise}
        </Typography>
      </Box>

      <Divider />

      {/* Central conflict — prominent because it drives the whole campaign */}
      <Box
        sx={{
          p: 2,
          bgcolor: "background.default",
          border: "1px solid",
          borderColor: "divider",
          borderRadius: 2,
        }}
      >
        <Typography variant="subtitle1" fontWeight={700} gutterBottom>
          Central Conflict
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {world.central_conflict}
        </Typography>
      </Box>

      <Divider />

      {/* Starting settlement */}
      <Box>
        <Typography variant="subtitle1" fontWeight={600} gutterBottom>
          Starting Settlement
        </Typography>
        <Box
          sx={{
            p: 2,
            border: "1px solid",
            borderColor: "divider",
            borderRadius: 2,
            bgcolor: "background.paper",
            display: "flex",
            flexDirection: "column",
            gap: 0.5,
          }}
        >
          <Typography variant="subtitle2" fontWeight={600}>
            {world.starting_settlement.name}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Population: {world.starting_settlement.population.toLocaleString()} &nbsp;|&nbsp;
            Governance: {world.starting_settlement.governance}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            {world.starting_settlement.description}
          </Typography>
        </Box>
      </Box>

      <Divider />

      {/* Factions */}
      {world.factions.length > 0 && (
        <Box>
          <Typography variant="subtitle1" fontWeight={600} gutterBottom>
            Factions
          </Typography>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
            {world.factions.map((faction) => (
              <FactionCard
                key={faction.name}
                faction={faction}
                showDmControls={isDm && dmSecretsVisible}
              />
            ))}
          </Box>
        </Box>
      )}

      <Divider />

      {/* Key NPCs */}
      {world.key_npcs.length > 0 && (
        <Box>
          <Typography variant="subtitle1" fontWeight={600} gutterBottom>
            Key NPCs
          </Typography>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
            {world.key_npcs.map((npc) => (
              <NPCCard
                key={npc.name}
                npc={npc}
                showDmControls={isDm && dmSecretsVisible}
              />
            ))}
          </Box>
        </Box>
      )}

      <Divider />

      {/* Adventure hooks */}
      {world.adventure_hooks.length > 0 && (
        <Box>
          <Typography variant="subtitle1" fontWeight={600} gutterBottom>
            Adventure Hooks
          </Typography>
          <AdventureHookList hooks={world.adventure_hooks} />
        </Box>
      )}
    </Box>
  );
}
