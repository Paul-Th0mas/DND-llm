"use client";

import React, { useState } from "react";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Divider from "@mui/material/Divider";
import Typography from "@mui/material/Typography";
import { AppCard } from "@/shared/components/AppCard";
import type { DungeonRoomResponse, RoomType, SkillCheck } from "../types";

// Dark fantasy badge colors per room type (US-037).
const ROOM_TYPE_BADGE: Record<RoomType, { bgcolor: string; color: string }> = {
  BOSS:     { bgcolor: "#5a1010", color: "#f5d0d0" },
  COMBAT:   { bgcolor: "#5a1010", color: "#f5d0d0" },
  TREASURE: { bgcolor: "#5a3a00", color: "#f5e0a0" },
  SHOP:     { bgcolor: "#5a3a00", color: "#f5e0a0" },
  REST:     { bgcolor: "#1a3a2a", color: "#c0e0d0" },
  EVENT:    { bgcolor: "#1a1a4a", color: "#c0c0f0" },
};

const BADGE_FALLBACK: { bgcolor: string; color: string } = {
  bgcolor: "#2a2a2a",
  color: "#e0e0e0",
};

/**
 * Converts a SCREAMING_SNAKE_CASE enum value to Title Case for display.
 * @param value - The raw enum string (e.g. "MEDIEVAL_FANTASY").
 * @returns A human-readable label (e.g. "Medieval Fantasy").
 */
function toLabel(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

/** Props for the RollCheckDialog component. */
interface RollCheckDialogProps {
  readonly open: boolean;
  readonly check: SkillCheck;
  readonly onClose: () => void;
  readonly onConfirm: (rollResult: number) => void;
}

/**
 * Modal dialog that lets the player enter a d20 roll result for a skill check.
 * Displays the skill type and DC, accepts a numeric input, and emits the result.
 */
function RollCheckDialog({ open, check, onClose, onConfirm }: RollCheckDialogProps): React.ReactElement {
  const [value, setValue] = useState<string>("");

  function handleConfirm(): void {
    const parsed = parseInt(value, 10);
    if (!isNaN(parsed) && parsed >= 1 && parsed <= 30) {
      onConfirm(parsed);
      setValue("");
      onClose();
    }
  }

  function handleClose(): void {
    setValue("");
    onClose();
  }

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="xs" fullWidth>
      <DialogTitle sx={{ fontFamily: "var(--font-medieval-sharp)", color: "#3a2820" }}>
        {toLabel(check.type)} Check
      </DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
          DC {check.dc} - Enter your d20 roll result:
        </Typography>
        <input
          type="number"
          min={1}
          max={30}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") handleConfirm(); }}
          style={{
            width: "100%",
            padding: "8px 12px",
            border: "1px solid #C9B59C",
            borderRadius: "4px",
            fontSize: "1rem",
            background: "#F9F8F6",
            color: "#3a2820",
          }}
          autoFocus
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} color="inherit">
          Cancel
        </Button>
        <Button
          onClick={handleConfirm}
          variant="contained"
          disabled={value === "" || isNaN(parseInt(value, 10))}
          sx={{ bgcolor: "#7d5e45", "&:hover": { bgcolor: "#5c4230" } }}
        >
          Roll
        </Button>
      </DialogActions>
    </Dialog>
  );
}

/** Props for the DungeonRoomCard component. */
export interface DungeonRoomCardProps {
  readonly room: DungeonRoomResponse;
  /** Optional stagger index for the card entrance animation. */
  readonly index?: number;
  /**
   * Called when the player submits a skill check roll.
   * @param roomIndex - The room's index within the dungeon.
   * @param skillType - The skill check type (e.g. "Perception").
   * @param dc - The difficulty class for the check.
   * @param rollResult - The d20 roll value the player entered.
   */
  readonly onRollCheck?: (roomIndex: number, skillType: string, dc: number, rollResult: number) => void;
}

/**
 * Displays a single generated dungeon room with its type badge, name,
 * description, and structured content (enemies, skill checks, loot, NPCs).
 * Falls back to legacy flat fields when structured data is absent.
 *
 * US-068: Renders structured enemies/mechanics/loot/npc_data sections.
 * US-037: Dark fantasy badge colors per room type.
 * US-035: Room name in MedievalSharp via AppCard title prop.
 * US-034: Magic border image on the inner content zone.
 * US-036: Inner content area is max-height capped and scrollable.
 */
export function DungeonRoomCard({ room, index = 0, onRollCheck }: DungeonRoomCardProps): React.ReactElement {
  const badge = ROOM_TYPE_BADGE[room.room_type] ?? BADGE_FALLBACK;
  const [activeCheck, setActiveCheck] = useState<SkillCheck | null>(null);

  // Determine enemy list: prefer structured data, fall back to legacy flat field.
  const enemyNames: readonly string[] = room.enemies
    ? [
        ...room.enemies.initial,
        ...(room.enemies.boss ? [room.enemies.boss] : []),
      ]
    : room.enemy_names;

  // Skill checks from structured mechanics, or empty.
  const skillChecks: readonly SkillCheck[] = room.mechanics?.skill_checks ?? [];

  // Rest benefit (REST rooms).
  const restBenefit: string | null = room.mechanics?.rest_benefit ?? null;

  // NPC names: prefer structured npc_data, fall back to legacy flat field.
  const npcNames: readonly string[] = room.npc_data
    ? room.npc_data.map((n) => n.name)
    : room.npc_names;

  function handleRollResult(rollResult: number): void {
    if (activeCheck !== null && onRollCheck !== undefined) {
      onRollCheck(room.index, activeCheck.type, activeCheck.dc, rollResult);
    }
  }

  return (
    <>
      <AppCard
        title={`${room.index + 1}. ${room.name}`}
        chips={[
          <Chip
            key="type"
            label={toLabel(room.room_type)}
            size="small"
            sx={{
              fontWeight: 600,
              fontSize: "0.7rem",
              bgcolor: badge.bgcolor,
              color: badge.color,
              "&:hover": { bgcolor: badge.bgcolor },
            }}
          />,
        ]}
        staggerIndex={index}
      >
        {/*
          US-034: Inner content container with magic border image frame.
          US-036: maxHeight + overflowY create the scrollable zone.
        */}
        <Box
          sx={{
            px: 3,
            py: 2.5,
            border: "2px solid #5c4230",
            borderImage: "url('/images/magic-border.png') 30 fill stretch",
            boxSizing: "border-box",
            width: "100%",
            maxHeight: "340px",
            overflowY: "auto",
            display: "flex",
            flexDirection: "column",
            gap: 1.5,
            scrollbarColor: "#a07d60 #1a1a1a",
            scrollbarWidth: "thin",
            "&::-webkit-scrollbar": { width: "6px" },
            "&::-webkit-scrollbar-track": { bgcolor: "#1a1a1a" },
            "&::-webkit-scrollbar-thumb": { bgcolor: "#a07d60", borderRadius: "3px" },
          }}
        >
          <Typography variant="body2" color="text.secondary">
            {room.description}
          </Typography>

          {/* Enemies (structured or legacy) */}
          {enemyNames.length > 0 && (
            <Box>
              <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                Enemies:
              </Typography>
              <Box sx={{ display: "flex", gap: 0.5, flexWrap: "wrap", mt: 0.5 }}>
                {enemyNames.map((name) => (
                  <Chip key={name} label={name} size="small" variant="outlined" />
                ))}
              </Box>
              {/* Special attacks (BOSS rooms) */}
              {room.enemies?.special_attacks && room.enemies.special_attacks.length > 0 && (
                <Typography variant="caption" color="error.light" sx={{ display: "block", mt: 0.5, fontStyle: "italic" }}>
                  Special: {room.enemies.special_attacks.join(", ")}
                </Typography>
              )}
            </Box>
          )}

          {/* Skill checks with Roll Check buttons (US-070) */}
          {skillChecks.length > 0 && (
            <Box>
              <Divider sx={{ borderColor: "#C9B59C", mb: 1 }} />
              <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                Skill Checks:
              </Typography>
              <Box sx={{ display: "flex", flexDirection: "column", gap: 0.75, mt: 0.5 }}>
                {skillChecks.map((check) => (
                  <Box key={check.type} sx={{ display: "flex", alignItems: "center", gap: 1, flexWrap: "wrap" }}>
                    <Typography variant="caption" sx={{ color: "#5c4230", fontWeight: 600, minWidth: 80 }}>
                      {toLabel(check.type)} DC {check.dc}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ flex: 1 }}>
                      {check.on_success}
                    </Typography>
                    {onRollCheck !== undefined && (
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => setActiveCheck(check)}
                        sx={{
                          fontSize: "0.65rem",
                          py: 0.25,
                          px: 1,
                          borderColor: "#7d5e45",
                          color: "#7d5e45",
                          "&:hover": { borderColor: "#5c4230", color: "#5c4230" },
                        }}
                      >
                        Roll Check
                      </Button>
                    )}
                  </Box>
                ))}
              </Box>
            </Box>
          )}

          {/* Rest benefit (REST rooms) */}
          {restBenefit !== null && (
            <Typography variant="caption" color="success.light" sx={{ fontStyle: "italic" }}>
              {restBenefit}
            </Typography>
          )}

          {/* Loot table (TREASURE rooms) */}
          {room.loot_table !== undefined && room.loot_table !== null && room.loot_table.length > 0 && (
            <Box>
              <Divider sx={{ borderColor: "#C9B59C", mb: 1 }} />
              <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                Loot:
              </Typography>
              <Box sx={{ display: "flex", flexDirection: "column", gap: 0.5, mt: 0.5 }}>
                {room.loot_table.map((item) => (
                  <Box key={item.item} sx={{ display: "flex", gap: 1, alignItems: "center" }}>
                    <Typography variant="caption" sx={{ color: "#a07d60" }}>
                      {item.item} x{item.quantity}
                    </Typography>
                    {item.value !== null && (
                      <Typography variant="caption" color="text.secondary">
                        ({item.value})
                      </Typography>
                    )}
                    {item.rarity !== null && (
                      <Chip label={item.rarity} size="small" sx={{ fontSize: "0.6rem", height: 16 }} />
                    )}
                  </Box>
                ))}
              </Box>
            </Box>
          )}

          {/* NPC inventory (SHOP rooms) */}
          {room.npc_data !== undefined && room.npc_data !== null && room.npc_data.length > 0 && (
            <Box>
              <Divider sx={{ borderColor: "#C9B59C", mb: 1 }} />
              <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                NPCs:
              </Typography>
              {room.npc_data.map((npc) => (
                <Box key={npc.name} sx={{ mt: 0.5 }}>
                  <Typography variant="caption" sx={{ color: "#5c4230", fontWeight: 600 }}>
                    {npc.name} - {npc.role}
                  </Typography>
                  {npc.inventory.length > 0 && (
                    <Box sx={{ display: "flex", gap: 0.5, flexWrap: "wrap", mt: 0.25 }}>
                      {npc.inventory.map((inv) => (
                        <Chip
                          key={inv.item}
                          label={`${inv.item} (${inv.price}gp)`}
                          size="small"
                          variant="outlined"
                          sx={{ fontSize: "0.65rem" }}
                        />
                      ))}
                    </Box>
                  )}
                </Box>
              ))}
            </Box>
          )}

          {/* Legacy NPC names fallback (when npc_data is absent) */}
          {(room.npc_data === undefined || room.npc_data === null) && npcNames.length > 0 && (
            <Box>
              <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                NPCs:
              </Typography>
              <Box sx={{ display: "flex", gap: 0.5, flexWrap: "wrap", mt: 0.5 }}>
                {npcNames.map((name) => (
                  <Chip key={name} label={name} size="small" variant="outlined" />
                ))}
              </Box>
            </Box>
          )}

          {/* Game effects (US-071): rendered per effect type if mechanics present */}
          {room.mechanics !== undefined && room.mechanics !== null && room.mechanics.game_effects.length > 0 && (
            <Box>
              <Divider sx={{ borderColor: "#C9B59C", mb: 1 }} />
              <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                Effects:
              </Typography>
              <Box sx={{ display: "flex", flexDirection: "column", gap: 0.5, mt: 0.5 }}>
                {room.mechanics.game_effects.map((effect, i) => (
                  <Typography key={i} variant="caption" color="text.secondary" sx={{ fontStyle: "italic" }}>
                    {toLabel(effect.effect_type)} on {effect.trigger.trigger_action}
                    {effect.value !== null ? ` (${effect.value})` : ""}
                    {effect.item_id !== null ? ` - ${effect.item_id}` : ""}
                  </Typography>
                ))}
              </Box>
            </Box>
          )}
        </Box>
      </AppCard>

      {activeCheck !== null && (
        <RollCheckDialog
          open={true}
          check={activeCheck}
          onClose={() => setActiveCheck(null)}
          onConfirm={handleRollResult}
        />
      )}
    </>
  );
}
