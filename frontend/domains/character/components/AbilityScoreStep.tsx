"use client";

import { useState } from "react";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import Typography from "@mui/material/Typography";
import type { AbilityKey, AbilityScores, ScoreMethod } from "@/domains/character/types";

/** Standard array values that must each be assigned exactly once. */
const STANDARD_ARRAY = [15, 14, 13, 12, 10, 8] as const;

/** Ordered list of all ability keys with display labels. */
const ABILITY_LABELS: { key: AbilityKey; label: string; abbrev: string }[] = [
  { key: "strength", label: "Strength", abbrev: "STR" },
  { key: "dexterity", label: "Dexterity", abbrev: "DEX" },
  { key: "constitution", label: "Constitution", abbrev: "CON" },
  { key: "intelligence", label: "Intelligence", abbrev: "INT" },
  { key: "wisdom", label: "Wisdom", abbrev: "WIS" },
  { key: "charisma", label: "Charisma", abbrev: "CHA" },
];

/**
 * Point Buy cost table: score 8–15 maps to a point cost.
 * Source: D&D 5e standard point buy rules.
 */
const POINT_BUY_COSTS: Record<number, number> = {
  8: 0,
  9: 1,
  10: 2,
  11: 3,
  12: 4,
  13: 5,
  14: 7,
  15: 9,
};

const POINT_BUY_BUDGET = 27 as const;
// Valid point buy score range.
const PB_MIN = 8 as const;
const PB_MAX = 15 as const;

/** Props for AbilityScoreStep. */
export interface AbilityScoreStepProps {
  /** The current score method tab selection. */
  readonly scoreMethod: ScoreMethod;
  /** The currently assigned ability scores, or null if none set. */
  readonly abilityScores: AbilityScores | null;
  /** Callback when the method tab changes. */
  readonly onMethodChange: (method: ScoreMethod) => void;
  /** Callback when valid scores are fully assigned. */
  readonly onScoresChange: (scores: AbilityScores | null) => void;
}

/** Default ability score record with all values at 8 (Point Buy starting point). */
const DEFAULT_PB_SCORES: AbilityScores = {
  strength: 8,
  dexterity: 8,
  constitution: 8,
  intelligence: 8,
  wisdom: 8,
  charisma: 8,
};

/** Empty standard array assignment: maps each AbilityKey to null (unassigned). */
type StandardArrayAssignment = Record<AbilityKey, number | null>;

const EMPTY_SA_ASSIGNMENT: StandardArrayAssignment = {
  strength: null,
  dexterity: null,
  constitution: null,
  intelligence: null,
  wisdom: null,
  charisma: null,
};

/**
 * Ability score assignment step for the character creation wizard.
 * Supports Standard Array (assign 15,14,13,12,10,8) and Point Buy (27 points, 8-15 range).
 */
export function AbilityScoreStep({
  scoreMethod,
  abilityScores,
  onMethodChange,
  onScoresChange,
}: AbilityScoreStepProps): React.ReactElement {
  // Standard Array local state — which value is assigned to which ability.
  const [saAssignment, setSaAssignment] = useState<StandardArrayAssignment>(
    EMPTY_SA_ASSIGNMENT
  );

  // Point Buy local state — scores for each ability.
  const [pbScores, setPbScores] = useState<AbilityScores>(
    abilityScores ?? DEFAULT_PB_SCORES
  );

  // ---------------------------------------------------------------------------
  // Standard Array helpers
  // ---------------------------------------------------------------------------

  /** Scores that have already been assigned to an ability. */
  function usedSaValues(): number[] {
    return Object.values(saAssignment).filter(
      (v): v is number => v !== null
    );
  }

  /** Returns true if all six standard array values have been placed. */
  function isSaComplete(assignment: StandardArrayAssignment): boolean {
    return Object.values(assignment).every((v) => v !== null);
  }

  function handleSaSelect(key: AbilityKey, value: number | ""): void {
    const numValue = value === "" ? null : Number(value);
    const updated = { ...saAssignment, [key]: numValue };
    setSaAssignment(updated);

    if (isSaComplete(updated)) {
      // All abilities assigned — propagate to parent.
      onScoresChange({
        strength: updated.strength ?? 8,
        dexterity: updated.dexterity ?? 8,
        constitution: updated.constitution ?? 8,
        intelligence: updated.intelligence ?? 8,
        wisdom: updated.wisdom ?? 8,
        charisma: updated.charisma ?? 8,
      });
    } else {
      onScoresChange(null);
    }
  }

  // ---------------------------------------------------------------------------
  // Point Buy helpers
  // ---------------------------------------------------------------------------

  function pointsSpent(scores: AbilityScores): number {
    return ABILITY_LABELS.reduce((total, { key }) => {
      return total + (POINT_BUY_COSTS[scores[key]] ?? 0);
    }, 0);
  }

  function pointsRemaining(scores: AbilityScores): number {
    return POINT_BUY_BUDGET - pointsSpent(scores);
  }

  function handlePbChange(key: AbilityKey, value: number): void {
    const updated = { ...pbScores, [key]: value };
    const remaining = pointsRemaining(updated);
    if (remaining < 0) return; // Over budget — block the change.
    setPbScores(updated);
    onScoresChange(updated);
  }

  // ---------------------------------------------------------------------------
  // Tab change handler — reset local state when switching methods.
  // ---------------------------------------------------------------------------

  function handleTabChange(_: React.SyntheticEvent, newMethod: ScoreMethod): void {
    onMethodChange(newMethod);
    onScoresChange(null);
    if (newMethod === "standard_array") {
      setSaAssignment(EMPTY_SA_ASSIGNMENT);
    } else {
      setPbScores(DEFAULT_PB_SCORES);
    }
  }

  const pbRemaining = pointsRemaining(pbScores);

  return (
    <Box>
      {/* Method tabs */}
      <Tabs
        value={scoreMethod}
        onChange={handleTabChange}
        sx={{ mb: 3, borderBottom: "1px solid", borderColor: "divider" }}
      >
        <Tab
          value="standard_array"
          label="Standard Array"
          sx={{ textTransform: "none", fontWeight: 600 }}
        />
        <Tab
          value="point_buy"
          label="Point Buy"
          sx={{ textTransform: "none", fontWeight: 600 }}
        />
      </Tabs>

      {/* Standard Array */}
      {scoreMethod === "standard_array" && (
        <Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Assign each of the following values to one ability: 15, 14, 13, 12, 10, 8.
            Each value may only be used once.
          </Typography>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            {ABILITY_LABELS.map(({ key, label }) => {
              const used = usedSaValues();
              return (
                <Box
                  key={key}
                  sx={{ display: "flex", alignItems: "center", gap: 2 }}
                >
                  <Typography
                    variant="body1"
                    fontWeight={600}
                    sx={{ width: 110, color: "#3a2820" }}
                  >
                    {label}
                  </Typography>
                  <FormControl size="small" sx={{ minWidth: 100 }}>
                    <InputLabel>Score</InputLabel>
                    <Select
                      value={saAssignment[key] ?? ""}
                      label="Score"
                      onChange={(e) =>
                        handleSaSelect(key, e.target.value as number | "")
                      }
                    >
                      <MenuItem value="">
                        <em>—</em>
                      </MenuItem>
                      {STANDARD_ARRAY.map((val) => (
                        <MenuItem
                          key={val}
                          value={val}
                          // Disable if already used by another ability.
                          disabled={
                            used.includes(val) && saAssignment[key] !== val
                          }
                        >
                          {val}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Box>
              );
            })}
          </Box>
        </Box>
      )}

      {/* Point Buy */}
      {scoreMethod === "point_buy" && (
        <Box>
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              gap: 2,
              mb: 2,
            }}
          >
            <Typography variant="body2" color="text.secondary">
              Scores range from {PB_MIN} to {PB_MAX}. Budget: {POINT_BUY_BUDGET} points.
            </Typography>
            <Chip
              label={`Points remaining: ${pbRemaining}`}
              size="small"
              sx={{
                bgcolor: pbRemaining < 0 ? "#c62828" : "#a07d60",
                color: "#F9F8F6",
                fontWeight: 700,
              }}
            />
          </Box>

          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            {ABILITY_LABELS.map(({ key, label }) => {
              const currentScore = pbScores[key];
              return (
                <Box
                  key={key}
                  sx={{ display: "flex", alignItems: "center", gap: 2 }}
                >
                  <Typography
                    variant="body1"
                    fontWeight={600}
                    sx={{ width: 110, color: "#3a2820" }}
                  >
                    {label}
                  </Typography>

                  {/* Decrement button */}
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() =>
                      handlePbChange(key, Math.max(PB_MIN, currentScore - 1))
                    }
                    disabled={currentScore <= PB_MIN}
                    sx={{ minWidth: 32, px: 0.5 }}
                  >
                    -
                  </Button>

                  <Typography
                    variant="body1"
                    fontWeight={700}
                    sx={{ width: 28, textAlign: "center", color: "#1e1410" }}
                  >
                    {currentScore}
                  </Typography>

                  {/* Increment button */}
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() =>
                      handlePbChange(key, Math.min(PB_MAX, currentScore + 1))
                    }
                    disabled={
                      currentScore >= PB_MAX ||
                      pbRemaining - (POINT_BUY_COSTS[currentScore + 1] ?? 0) +
                        (POINT_BUY_COSTS[currentScore] ?? 0) <
                        0
                    }
                    sx={{ minWidth: 32, px: 0.5 }}
                  >
                    +
                  </Button>

                  <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                    Cost: {POINT_BUY_COSTS[currentScore] ?? 0}
                  </Typography>
                </Box>
              );
            })}
          </Box>
        </Box>
      )}
    </Box>
  );
}
