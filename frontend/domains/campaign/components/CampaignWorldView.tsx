"use client";

import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Divider from "@mui/material/Divider";
import Typography from "@mui/material/Typography";
import type { CampaignWorldDetailResponse } from "@/domains/campaign/types";
import { FactionCard } from "@/domains/campaign/components/FactionCard";
import { NPCCard } from "@/domains/campaign/components/NPCCard";
import { AdventureHookList } from "@/domains/campaign/components/AdventureHookList";

/** Props for the CampaignWorldView component. */
export interface CampaignWorldViewProps {
  /** The generated campaign world to display. */
  readonly world: CampaignWorldDetailResponse;
  /** When true, DM-only sections (hidden agendas, NPC secrets) are rendered. */
  readonly isDM: boolean;
}

/**
 * Full read-only display of a generated campaign world.
 * Shows world name, premise, starting settlement, central conflict, factions, NPCs, and adventure hooks.
 * DM-only sections are conditionally rendered based on the isDM prop.
 */
export function CampaignWorldView({ world, isDM }: CampaignWorldViewProps): React.ReactElement {
  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 4 }}>
      {/* World name and premise */}
      <Box>
        <Typography variant="h5" fontWeight={700} gutterBottom>
          {world.world_name}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {world.premise}
        </Typography>
      </Box>

      <Divider />

      {/* Starting settlement */}
      <Box>
        <Typography variant="h6" fontWeight={700} gutterBottom>
          Starting Settlement
        </Typography>
        <Box
          sx={{
            p: 2.5,
            border: "1px solid",
            borderColor: "divider",
            borderRadius: 2,
            bgcolor: "background.paper",
            display: "flex",
            flexDirection: "column",
            gap: 1,
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, flexWrap: "wrap" }}>
            <Typography variant="subtitle1" fontWeight={700}>
              {world.starting_settlement.name}
            </Typography>
            <Chip label={world.starting_settlement.governance} size="small" variant="outlined" />
            <Chip
              label={`Pop. ${world.starting_settlement.population}`}
              size="small"
              variant="outlined"
            />
          </Box>
          <Typography variant="body2" color="text.secondary">
            {world.starting_settlement.description}
          </Typography>
        </Box>
      </Box>

      <Divider />

      {/* Central conflict */}
      <Box>
        <Typography variant="h6" fontWeight={700} gutterBottom>
          Central Conflict
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ lineHeight: 1.8 }}>
          {world.central_conflict}
        </Typography>
      </Box>

      {/* Factions */}
      {world.factions.length > 0 && (
        <>
          <Divider />
          <Box>
            <Typography variant="h6" fontWeight={700} gutterBottom>
              Factions
            </Typography>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {world.factions.map((faction) => (
                <FactionCard key={faction.name} faction={faction} isDM={isDM} />
              ))}
            </div>
          </Box>
        </>
      )}

      {/* Key NPCs */}
      {world.key_npcs.length > 0 && (
        <>
          <Divider />
          <Box>
            <Typography variant="h6" fontWeight={700} gutterBottom>
              Key NPCs
            </Typography>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {world.key_npcs.map((npc) => (
                <NPCCard key={npc.name} npc={npc} isDM={isDM} />
              ))}
            </div>
          </Box>
        </>
      )}

      {/* Adventure hooks */}
      {world.adventure_hooks.length > 0 && (
        <>
          <Divider />
          <Box>
            <Typography variant="h6" fontWeight={700} gutterBottom>
              Adventure Hooks
            </Typography>
            <AdventureHookList hooks={world.adventure_hooks} />
          </Box>
        </>
      )}
    </Box>
  );
}
