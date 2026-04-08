"use client";

import { useState } from "react";
import Box from "@mui/material/Box";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import Typography from "@mui/material/Typography";
import { ABILITY_DESCRIPTIONS } from "@/domains/character/constants/abilityDescriptions";
import type { AbilityKey, AbilityScores, ScoreMethod } from "@/domains/character/types";

/** Standard array values that must each be assigned exactly once. */
const STANDARD_ARRAY = [15, 14, 13, 12, 10, 8] as const;

/** Ordered list of all ability keys with display labels and abbreviations. */
const ABILITY_LABELS: { key: AbilityKey; label: string; abbrev: string }[] = [
  { key: "strength", label: "Strength", abbrev: "STR" },
  { key: "dexterity", label: "Dexterity", abbrev: "DEX" },
  { key: "constitution", label: "Constitution", abbrev: "CON" },
  { key: "intelligence", label: "Intelligence", abbrev: "INT" },
  { key: "wisdom", label: "Wisdom", abbrev: "WIS" },
  { key: "charisma", label: "Charisma", abbrev: "CHA" },
];

/**
 * Point Buy cost table: score 8-15 maps to a point cost.
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

/** Computes the D&D modifier from an ability score. */
function getModifier(score: number): number {
  return Math.floor((score - 10) / 2);
}

/** Returns modifier formatted with a leading sign, e.g. +2 or -1. */
function formatModifier(mod: number): string {
  return mod >= 0 ? `+${mod}` : String(mod);
}

/**
 * Ability score assignment step for the character creation wizard.
 * Supports Standard Array (assign 15,14,13,12,10,8) and Point Buy (27 points, 8-15 range).
 * Renders a bento-grid layout with an assignment panel and a derived stats sidebar
 * per the Modern Scriptorium design system (US-062).
 */
export function AbilityScoreStep({
  scoreMethod,
  abilityScores,
  onMethodChange,
  onScoresChange,
}: AbilityScoreStepProps): React.ReactElement {
  // Standard Array local state - which value is assigned to which ability.
  const [saAssignment, setSaAssignment] = useState<StandardArrayAssignment>(
    EMPTY_SA_ASSIGNMENT
  );

  // Point Buy local state - scores for each ability.
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
      // All abilities assigned - propagate to parent.
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
    if (remaining < 0) return; // Over budget - block the change.
    setPbScores(updated);
    onScoresChange(updated);
  }

  // ---------------------------------------------------------------------------
  // Tab change handler - reset local state when switching methods.
  // ---------------------------------------------------------------------------

  function handleMethodSwitch(method: ScoreMethod): void {
    onMethodChange(method);
    onScoresChange(null);
    if (method === "standard_array") {
      setSaAssignment(EMPTY_SA_ASSIGNMENT);
    } else {
      setPbScores(DEFAULT_PB_SCORES);
    }
  }

  const pbRemaining = pointsRemaining(pbScores);

  // Resolve effective scores for derived stats sidebar.
  // When method is point_buy we always have pbScores; for standard_array use abilityScores if complete.
  const effectiveScores: AbilityScores | null =
    scoreMethod === "point_buy" ? pbScores : abilityScores;

  const dexMod = effectiveScores ? getModifier(effectiveScores.dexterity) : null;
  const conMod = effectiveScores ? getModifier(effectiveScores.constitution) : null;
  const wisMod = effectiveScores ? getModifier(effectiveScores.wisdom) : null;

  const derivedAC = dexMod !== null ? 10 + dexMod : null;
  const derivedInit = dexMod;
  // HP cannot be computed without the selected class hit die, which is not a prop.
  const derivedHP: null = null;
  const derivedPassivePerception = wisMod !== null ? 10 + wisMod : null;

  const scoresComplete = abilityScores !== null;

  return (
    <Box>
      {/* Page header */}
      <Typography
        component="h2"
        sx={{
          fontFamily: "var(--font-newsreader), serif",
          fontStyle: "italic",
          fontWeight: 400,
          fontSize: { xs: "2.25rem", md: "3rem" },
          color: "#3a311b",
          mb: 1,
        }}
      >
        The Measure of a Hero
      </Typography>

      {/* 12-column bento grid */}
      <div className="grid grid-cols-12 gap-6 mt-8">
        {/* ------------------------------------------------------------------ */}
        {/* Assignment panel - 8 cols */}
        {/* ------------------------------------------------------------------ */}
        <div className="col-span-12 md:col-span-8">
          <Box
            sx={{
              bgcolor: "#fdf2df",
              borderRadius: "0.75rem",
              p: 4,
              position: "relative",
              overflow: "hidden",
              borderLeft: "4px solid rgba(114,90,66,0.3)",
            }}
          >
            {/* Method selector tabs */}
            <div className="flex gap-2 mb-6">
              {(["standard_array", "point_buy"] as const).map((method) => {
                const isActive = scoreMethod === method;
                const label = method === "standard_array" ? "Standard Array" : "Point Buy";
                return (
                  <button
                    key={method}
                    type="button"
                    onClick={() => handleMethodSwitch(method)}
                    className="px-4 py-2 font-bold text-sm rounded transition-all"
                    style={
                      isActive
                        ? {
                            background: "linear-gradient(135deg, #725a42 0%, #fedcbe 100%)",
                            color: "#fff6f1",
                            border: "none",
                            cursor: "default",
                          }
                        : {
                            background: "transparent",
                            color: "#86795e",
                            border: "1px solid #bfb193",
                            cursor: "pointer",
                          }
                    }
                  >
                    {label}
                  </button>
                );
              })}
            </div>

            {/* Panel heading with icon */}
            <div className="flex items-center gap-2 mb-4">
              <span
                className="material-symbols-outlined"
                style={{ color: "#725a42", fontSize: "1.5rem" }}
              >
                analytics
              </span>
              <Typography
                sx={{
                  fontFamily: "var(--font-newsreader), serif",
                  fontWeight: 700,
                  fontSize: "1.25rem",
                  color: "#3a311b",
                }}
              >
                {scoreMethod === "standard_array" ? "Standard Array" : "Point Buy"}
              </Typography>
            </div>

            {/* ---- Standard Array ---- */}
            {scoreMethod === "standard_array" && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {ABILITY_LABELS.map(({ key, label }) => {
                  const used = usedSaValues();
                  const currentVal = saAssignment[key];
                  const modifier =
                    currentVal !== null ? getModifier(currentVal) : null;

                  return (
                    <div
                      key={key}
                      className="flex items-center justify-between p-4 rounded-lg transition-colors"
                      style={{ backgroundColor: "#fff8f1" }}
                      onMouseEnter={(e) => {
                        (e.currentTarget as HTMLDivElement).style.backgroundColor =
                          "#f1e1c1";
                      }}
                      onMouseLeave={(e) => {
                        (e.currentTarget as HTMLDivElement).style.backgroundColor =
                          "#fff8f1";
                      }}
                    >
                      <div>
                        <h4
                          style={{
                            fontWeight: 700,
                            color: "#725a42",
                            letterSpacing: "0.05em",
                            fontSize: "0.875rem",
                            textTransform: "uppercase",
                            margin: 0,
                          }}
                        >
                          {label}
                        </h4>
                        <p
                          style={{
                            fontStyle: "italic",
                            fontSize: "0.75rem",
                            color: "#86795e",
                            margin: 0,
                          }}
                        >
                          {ABILITY_DESCRIPTIONS[key] ?? ""}
                        </p>
                      </div>

                      <div className="flex items-center gap-3">
                        <Select
                          size="small"
                          value={currentVal ?? ""}
                          onChange={(e) =>
                            handleSaSelect(key, e.target.value as number | "")
                          }
                          sx={{
                            minWidth: 72,
                            bgcolor: "#fdf2df",
                            "& .MuiOutlinedInput-notchedOutline": {
                              borderColor: "#bfb193",
                            },
                            "&:hover .MuiOutlinedInput-notchedOutline": {
                              borderColor: "#725a42",
                            },
                          }}
                        >
                          <MenuItem value="">
                            <em>--</em>
                          </MenuItem>
                          {STANDARD_ARRAY.map((val) => (
                            <MenuItem
                              key={val}
                              value={val}
                              // Disable if already used by another ability.
                              disabled={
                                used.includes(val) && currentVal !== val
                              }
                            >
                              {val}
                            </MenuItem>
                          ))}
                        </Select>

                        {/* Modifier badge */}
                        <div
                          style={{
                            width: 40,
                            height: 40,
                            borderRadius: "50%",
                            backgroundColor: "#fedcbe",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            fontFamily: "var(--font-newsreader), serif",
                            fontWeight: 700,
                            fontSize: "0.9375rem",
                            color: "#3a311b",
                          }}
                        >
                          {modifier !== null ? formatModifier(modifier) : "--"}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* ---- Point Buy ---- */}
            {scoreMethod === "point_buy" && (
              <div>
                {/* Points remaining badge */}
                <div className="flex items-center gap-3 mb-4">
                  <p style={{ fontSize: "0.875rem", color: "#695e45" }}>
                    Scores range from {PB_MIN} to {PB_MAX}. Budget:{" "}
                    {POINT_BUY_BUDGET} points.
                  </p>
                  <span
                    className="px-3 py-1 rounded-full text-xs font-bold"
                    style={{
                      background:
                        pbRemaining < 0
                          ? "#c62828"
                          : "linear-gradient(135deg, #725a42 0%, #fedcbe 100%)",
                      color: "#fff6f1",
                    }}
                  >
                    {pbRemaining} pts left
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {ABILITY_LABELS.map(({ key, label }) => {
                    const currentScore = pbScores[key];
                    const modifier = getModifier(currentScore);

                    return (
                      <div
                        key={key}
                        className="flex items-center justify-between p-4 rounded-lg transition-colors"
                        style={{ backgroundColor: "#fff8f1" }}
                        onMouseEnter={(e) => {
                          (e.currentTarget as HTMLDivElement).style.backgroundColor =
                            "#f1e1c1";
                        }}
                        onMouseLeave={(e) => {
                          (e.currentTarget as HTMLDivElement).style.backgroundColor =
                            "#fff8f1";
                        }}
                      >
                        <div>
                          <h4
                            style={{
                              fontWeight: 700,
                              color: "#725a42",
                              letterSpacing: "0.05em",
                              fontSize: "0.875rem",
                              textTransform: "uppercase",
                              margin: 0,
                            }}
                          >
                            {label}
                          </h4>
                          <p
                            style={{
                              fontStyle: "italic",
                              fontSize: "0.75rem",
                              color: "#86795e",
                              margin: 0,
                            }}
                          >
                            {ABILITY_DESCRIPTIONS[key] ?? ""}
                          </p>
                        </div>

                        <div className="flex items-center gap-3">
                          {/* Decrement button */}
                          <button
                            type="button"
                            onClick={() =>
                              handlePbChange(key, Math.max(PB_MIN, currentScore - 1))
                            }
                            disabled={currentScore <= PB_MIN}
                            className="w-8 h-8 rounded flex items-center justify-center font-bold transition-colors"
                            style={{
                              border: "1px solid #bfb193",
                              color: currentScore <= PB_MIN ? "#bfb193" : "#725a42",
                              background: "transparent",
                              cursor: currentScore <= PB_MIN ? "not-allowed" : "pointer",
                            }}
                          >
                            -
                          </button>

                          {/* Score value */}
                          <span
                            style={{
                              width: 28,
                              textAlign: "center",
                              fontWeight: 700,
                              fontSize: "1rem",
                              color: "#1e1410",
                            }}
                          >
                            {currentScore}
                          </span>

                          {/* Increment button */}
                          <button
                            type="button"
                            onClick={() =>
                              handlePbChange(
                                key,
                                Math.min(PB_MAX, currentScore + 1)
                              )
                            }
                            disabled={
                              currentScore >= PB_MAX ||
                              pbRemaining -
                                (POINT_BUY_COSTS[currentScore + 1] ?? 0) +
                                (POINT_BUY_COSTS[currentScore] ?? 0) <
                                0
                            }
                            className="w-8 h-8 rounded flex items-center justify-center font-bold transition-colors"
                            style={{
                              border: "1px solid #bfb193",
                              color:
                                currentScore >= PB_MAX ||
                                pbRemaining -
                                  (POINT_BUY_COSTS[currentScore + 1] ?? 0) +
                                  (POINT_BUY_COSTS[currentScore] ?? 0) <
                                  0
                                  ? "#bfb193"
                                  : "#725a42",
                              background: "transparent",
                              cursor:
                                currentScore >= PB_MAX ||
                                pbRemaining -
                                  (POINT_BUY_COSTS[currentScore + 1] ?? 0) +
                                  (POINT_BUY_COSTS[currentScore] ?? 0) <
                                  0
                                  ? "not-allowed"
                                  : "pointer",
                            }}
                          >
                            +
                          </button>

                          {/* Modifier badge */}
                          <div
                            style={{
                              width: 40,
                              height: 40,
                              borderRadius: "50%",
                              backgroundColor: "#fedcbe",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              fontFamily: "var(--font-newsreader), serif",
                              fontWeight: 700,
                              fontSize: "0.9375rem",
                              color: "#3a311b",
                            }}
                          >
                            {formatModifier(modifier)}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </Box>
        </div>

        {/* ------------------------------------------------------------------ */}
        {/* Derived stats sidebar - 4 cols */}
        {/* ------------------------------------------------------------------ */}
        <div className="col-span-12 md:col-span-4">
          <Box
            sx={{
              bgcolor: "#f1e1c1",
              borderRadius: "0.75rem",
              p: 4,
              position: "sticky",
              top: "6rem",
            }}
          >
            <Typography
              sx={{
                fontFamily: "var(--font-newsreader), serif",
                fontWeight: 700,
                fontSize: "1.125rem",
                color: "#3a311b",
                mb: 2,
                pb: 2,
                borderBottom: "1px solid rgba(114,90,66,0.2)",
              }}
            >
              Derived Statistics
            </Typography>

            <div className="flex flex-col gap-4">
              {/* AC */}
              <DerivedStatRow
                icon="shield"
                label="Armor Class"
                value={derivedAC !== null ? String(derivedAC) : "--"}
                formula="10 + DEX mod"
              />

              {/* Initiative */}
              <DerivedStatRow
                icon="bolt"
                label="Initiative"
                value={derivedInit !== null ? formatModifier(derivedInit) : "--"}
                formula="DEX modifier"
              />

              {/* Hit Points - cannot compute without class hit die */}
              <DerivedStatRow
                icon="favorite"
                label="Hit Points"
                value={derivedHP ?? "--"}
                formula="Base Class + CON mod"
              />

              {/* CON mod info row (supplementary) */}
              {conMod !== null && (
                <p
                  style={{
                    fontSize: "10px",
                    color: "#86795e",
                    textAlign: "center",
                    marginTop: "-8px",
                  }}
                >
                  CON mod: {formatModifier(conMod)}
                </p>
              )}

              {/* Passive Perception - bordered box */}
              <Box
                sx={{
                  mt: 1,
                  p: 2,
                  borderRadius: "0.5rem",
                  border: "1px solid rgba(114,90,66,0.2)",
                  bgcolor: "#fff8f1",
                }}
              >
                <DerivedStatRow
                  icon="visibility"
                  label="Passive Perception"
                  value={
                    derivedPassivePerception !== null
                      ? String(derivedPassivePerception)
                      : "--"
                  }
                  formula="10 + WIS mod"
                />
              </Box>
            </div>

            {/* Finalize Abilities button */}
            <button
              type="button"
              disabled={!scoresComplete}
              className="w-full mt-6 py-3 font-bold text-sm uppercase tracking-widest rounded transition-all"
              style={
                scoresComplete
                  ? {
                      background:
                        "linear-gradient(135deg, #725a42 0%, #fedcbe 100%)",
                      color: "#fff6f1",
                      border: "none",
                      cursor: "default",
                    }
                  : {
                      background: "#fdf2df",
                      color: "#bfb193",
                      border: "1px solid #bfb193",
                      cursor: "not-allowed",
                      opacity: 0.6,
                    }
              }
            >
              {scoresComplete ? "Abilities Set" : "Finalize Abilities"}
            </button>
          </Box>
        </div>
      </div>
    </Box>
  );
}

/** Props for DerivedStatRow. */
interface DerivedStatRowProps {
  /** Material Symbol icon name. */
  readonly icon: string;
  /** Display label for the stat. */
  readonly label: string;
  /** Computed value string. */
  readonly value: string;
  /** Short formula hint displayed on the right. */
  readonly formula: string;
}

/**
 * Renders a single row in the derived statistics sidebar.
 * Shows an icon, label, value, and a formula hint.
 */
function DerivedStatRow({
  icon,
  label,
  value,
  formula,
}: DerivedStatRowProps): React.ReactElement {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-4">
        <div
          className="flex items-center justify-center rounded-lg"
          style={{
            width: 48,
            height: 48,
            backgroundColor: "#fff8f1",
            flexShrink: 0,
          }}
        >
          <span
            className="material-symbols-outlined"
            style={{ color: "#725a42", fontSize: "1.5rem" }}
          >
            {icon}
          </span>
        </div>
        <div>
          <p
            style={{
              fontSize: "10px",
              textTransform: "uppercase",
              letterSpacing: "0.1em",
              color: "#86795e",
              margin: 0,
            }}
          >
            {label}
          </p>
          <p
            style={{
              fontFamily: "var(--font-newsreader), serif",
              fontSize: "1.5rem",
              fontWeight: 700,
              color: "#3a311b",
              margin: 0,
              lineHeight: 1.2,
            }}
          >
            {value}
          </p>
        </div>
      </div>
      <div
        style={{
          fontSize: "10px",
          color: "#86795e",
          textAlign: "right",
          maxWidth: 80,
          lineHeight: 1.3,
        }}
      >
        {formula}
      </div>
    </div>
  );
}
