"use client";

import { useState } from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import type { AbilityKey, CharacterSheet as CharacterSheetData } from "@/domains/character/types";

/** Ability label metadata for rendering the score grid. */
const ABILITY_LABELS: { key: AbilityKey; abbrev: string }[] = [
  { key: "strength", abbrev: "STR" },
  { key: "dexterity", abbrev: "DEX" },
  { key: "constitution", abbrev: "CON" },
  { key: "intelligence", abbrev: "INT" },
  { key: "wisdom", abbrev: "WIS" },
  { key: "charisma", abbrev: "CHA" },
];

const TABS = [
  "Character Sheet",
  "Inventory",
  "Spells & Abilities",
  "Campaign Notes",
  "Map",
] as const;

type TabName = (typeof TABS)[number];

/**
 * Formats a D&D ability score modifier as a signed string.
 * @param score - Raw ability score.
 * @returns Signed modifier string (e.g. "+2", "-1", "+0").
 */
function fmtMod(score: number): string {
  const m = Math.floor((score - 10) / 2);
  return m >= 0 ? `+${m}` : `${m}`;
}

/** Props for CharacterSheet. */
export interface CharacterSheetProps {
  /** The full character sheet data as returned by the API. */
  readonly character: CharacterSheetData;
}

/**
 * Gothic Character Folio layout for the character sheet.
 * Renders a tab bar, 3-column body (ability scores | portrait + info | combat + skills),
 * and a dark bottom action bar.
 */
export function CharacterSheet({
  character,
}: CharacterSheetProps): React.ReactElement {
  const [activeTab, setActiveTab] = useState<TabName>("Character Sheet");

  const cls = character.character_class;
  const sp = character.species;
  const scores = character.ability_scores;

  const dexMod = Math.floor((scores.dexterity - 10) / 2);
  const conMod = Math.floor((scores.constitution - 10) / 2);
  const maxHP = cls.hit_die + conMod;
  const baseAC = 10 + dexMod;

  const truncatedBackground =
    character.background.length > 80
      ? `${character.background.slice(0, 80)}...`
      : character.background;

  return (
    <Box
      sx={{
        border: "3px solid #3a2820",
        borderRadius: 2,
        overflow: "hidden",
        bgcolor: "#F9F8F6",
      }}
    >
      {/* Tab navigation bar */}
      <Box
        sx={{
          bgcolor: "#2a1e14",
          display: "flex",
          alignItems: "center",
          px: 1,
          overflowX: "auto",
        }}
      >
        {TABS.map((tab) => (
          <Box
            key={tab}
            onClick={() => setActiveTab(tab)}
            sx={{
              px: 2,
              py: 1.25,
              cursor: "pointer",
              bgcolor: activeTab === tab ? "#5c4230" : "transparent",
              borderRadius: "4px 4px 0 0",
              mr: 0.5,
              flexShrink: 0,
              "&:hover": {
                bgcolor: activeTab === tab ? "#5c4230" : "#3a2820",
              },
            }}
          >
            <Typography
              sx={{
                fontSize: { xs: "0.68rem", md: "0.78rem" },
                fontFamily: "'Cinzel', 'Georgia', serif",
                color: activeTab === tab ? "#EFE9E3" : "#C9B59C",
                whiteSpace: "nowrap",
                userSelect: "none",
              }}
            >
              {tab}
            </Typography>
          </Box>
        ))}
      </Box>

      {/* Main body */}
      {activeTab !== "Character Sheet" ? (
        <Typography sx={{ p: 3, color: "#C9B59C" }}>Coming soon</Typography>
      ) : (
        <Box sx={{ display: "flex", flexDirection: { xs: "column", md: "row" }, minHeight: 460 }}>
          {/* Left panel - ability scores */}
          <Box
            sx={{
              width: { xs: "100%", md: 220 },
              flexShrink: 0,
              borderRight: { xs: "none", md: "2px solid #D9CFC7" },
              borderBottom: { xs: "2px solid #D9CFC7", md: "none" },
              bgcolor: "#EFE9E3",
              p: 2,
            }}
          >
            {/* Title badge */}
            <Box
              sx={{
                border: "2px solid #5c4230",
                borderRadius: 1,
                bgcolor: "#3a2820",
                textAlign: "center",
                py: 1,
                px: 0.5,
              }}
            >
              <Typography
                sx={{
                  fontFamily: "'Cinzel', 'Georgia', serif",
                  color: "#EFE9E3",
                  fontSize: "0.8rem",
                  lineHeight: 1.3,
                }}
              >
                Gothic Character Folio
              </Typography>
            </Box>

            {/* Ability score grid - 2 columns on desktop, 3 columns on mobile */}
            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: { xs: "repeat(3, 1fr)", md: "1fr 1fr" },
                gap: 1.5,
                mt: 2,
              }}
            >
              {ABILITY_LABELS.map(({ key, abbrev }) => {
                const score = scores[key];
                return (
                  <Box
                    key={key}
                    sx={{
                      border: "2px solid #7d5e45",
                      borderRadius: "6px 6px 14px 14px",
                      bgcolor: "#3a2820",
                      textAlign: "center",
                      py: 0.75,
                      px: 0.5,
                    }}
                  >
                    <Typography
                      sx={{
                        fontSize: "0.6rem",
                        color: "#C9B59C",
                        textTransform: "uppercase",
                        letterSpacing: "0.1em",
                      }}
                    >
                      {abbrev}
                    </Typography>
                    <Typography
                      sx={{
                        fontSize: "1.3rem",
                        fontWeight: 700,
                        color: "#EFE9E3",
                        lineHeight: 1.2,
                      }}
                    >
                      {score}
                    </Typography>
                    {/* Modifier pill */}
                    <Box
                      sx={{
                        display: "inline-block",
                        bgcolor: "#5c4230",
                        borderRadius: "8px",
                        px: 0.75,
                        mt: 0.25,
                      }}
                    >
                      <Typography sx={{ fontSize: "0.7rem", color: "#EFE9E3" }}>
                        {fmtMod(score)}
                      </Typography>
                    </Box>
                  </Box>
                );
              })}
            </Box>
          </Box>

          {/* Center panel - portrait + character info */}
          <Box
            sx={{
              flex: 1,
              borderRight: "2px solid #D9CFC7",
              display: "flex",
              flexDirection: "column",
            }}
          >
            {/* Portrait area */}
            <Box
              sx={{
                bgcolor: "#1a1008",
                minHeight: { xs: 160, md: 200 },
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Box
                sx={{
                  width: 120,
                  height: 160,
                  border: "3px solid #a07d60",
                  borderRadius: 1,
                  bgcolor: "#2a1a0a",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <Typography sx={{ color: "#7d5e45", fontSize: "0.8rem" }}>
                  Portrait
                </Typography>
              </Box>
            </Box>

            {/* Character Information section */}
            <Box>
              {/* Section header */}
              <Box sx={{ bgcolor: "#5c4230", px: 1.5, py: 0.5 }}>
                <Typography
                  sx={{
                    fontSize: "0.7rem",
                    fontWeight: 700,
                    color: "#EFE9E3",
                    letterSpacing: "0.08em",
                    textTransform: "uppercase",
                    fontFamily: "'Cinzel', 'Georgia', serif",
                  }}
                >
                  Character Information
                </Typography>
              </Box>

              <Box sx={{ bgcolor: "#F9F8F6", p: 1.5 }}>
                {[
                  { label: "Name", value: character.name },
                  { label: "Race", value: sp.display_name },
                  { label: "Class", value: cls.display_name },
                  { label: "Level", value: "1" },
                  {
                    label: "Background",
                    value: truncatedBackground || "None",
                  },
                ].map(({ label, value }) => (
                  <Box
                    key={label}
                    sx={{ display: "flex", gap: 1, mb: 0.5 }}
                  >
                    <Typography
                      sx={{
                        fontSize: "0.72rem",
                        fontWeight: 700,
                        color: "#3a2820",
                        minWidth: 72,
                        flexShrink: 0,
                      }}
                    >
                      {label}:
                    </Typography>
                    <Typography
                      sx={{ fontSize: "0.72rem", color: "#5c4230" }}
                    >
                      {value}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Box>
          </Box>

          {/* Right panel - combat + skills */}
          <Box
            sx={{
              width: { xs: "100%", md: 260 },
              flexShrink: 0,
              display: "flex",
              flexDirection: "column",
            }}
          >
            {/* Top section: Combat Overview + Equipment side by side */}
            <Box
              sx={{
                display: "flex",
                borderBottom: "2px solid #D9CFC7",
              }}
            >
              {/* Combat Overview */}
              <Box
                sx={{
                  flex: 1,
                  borderRight: "1px solid #D9CFC7",
                  display: "flex",
                  flexDirection: "column",
                }}
              >
                <Box sx={{ bgcolor: "#5c4230", px: 1.5, py: 0.5 }}>
                  <Typography
                    sx={{
                      fontSize: "0.65rem",
                      fontWeight: 700,
                      color: "#EFE9E3",
                      letterSpacing: "0.08em",
                      textTransform: "uppercase",
                      fontFamily: "'Cinzel', 'Georgia', serif",
                    }}
                  >
                    Combat Overview
                  </Typography>
                </Box>

                <Box
                  sx={{
                    p: 1.5,
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: 1,
                  }}
                >
                  {[
                    { label: "HP", value: `${maxHP} / ${maxHP}` },
                    { label: "AC", value: String(baseAC) },
                    { label: "Speed", value: `${sp.speed} ft` },
                    { label: "Init", value: fmtMod(scores.dexterity) },
                  ].map(({ label, value }) => (
                    <Box
                      key={label}
                      sx={{
                        border: "1px solid #D9CFC7",
                        borderRadius: 1,
                        bgcolor: "#EFE9E3",
                        textAlign: "center",
                        py: 0.75,
                      }}
                    >
                      <Typography
                        sx={{
                          fontSize: "0.6rem",
                          color: "#7d5e45",
                          textTransform: "uppercase",
                          letterSpacing: "0.06em",
                          fontWeight: 700,
                        }}
                      >
                        {label}
                      </Typography>
                      <Typography
                        sx={{
                          fontSize: "0.85rem",
                          fontWeight: 700,
                          color: "#1e1410",
                        }}
                      >
                        {value}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </Box>

              {/* Equipment & Spells */}
              <Box sx={{ flex: 1, display: "flex", flexDirection: "column" }}>
                <Box sx={{ bgcolor: "#5c4230", px: 1.5, py: 0.5 }}>
                  <Typography
                    sx={{
                      fontSize: "0.65rem",
                      fontWeight: 700,
                      color: "#EFE9E3",
                      letterSpacing: "0.08em",
                      textTransform: "uppercase",
                      fontFamily: "'Cinzel', 'Georgia', serif",
                    }}
                  >
                    Equipment & Spells
                  </Typography>
                </Box>

                <Box sx={{ p: 1.5 }}>
                  {[
                    { label: "Weapons", value: "-" },
                    { label: "Armor", value: "-" },
                    { label: "Hit Die", value: `d${cls.hit_die}` },
                    { label: "Primary", value: cls.primary_ability },
                    ...(cls.spellcasting_ability !== null
                      ? [
                          {
                            label: "Spell Ability",
                            value: cls.spellcasting_ability,
                          },
                        ]
                      : []),
                  ].map(({ label, value }) => (
                    <Box
                      key={label}
                      sx={{ display: "flex", gap: 0.5, mb: 0.5 }}
                    >
                      <Typography
                        sx={{
                          fontSize: "0.65rem",
                          fontWeight: 700,
                          color: "#3a2820",
                          minWidth: 68,
                          flexShrink: 0,
                        }}
                      >
                        {label}:
                      </Typography>
                      <Typography sx={{ fontSize: "0.65rem", color: "#5c4230" }}>
                        {value}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </Box>
            </Box>

            {/* Bottom section: Skills & Proficiencies */}
            <Box sx={{ flex: 1, display: "flex", flexDirection: "column" }}>
              <Box sx={{ bgcolor: "#5c4230", px: 1.5, py: 0.5 }}>
                <Typography
                  sx={{
                    fontSize: "0.65rem",
                    fontWeight: 700,
                    color: "#EFE9E3",
                    letterSpacing: "0.08em",
                    textTransform: "uppercase",
                    fontFamily: "'Cinzel', 'Georgia', serif",
                  }}
                >
                  Skills & Proficiencies
                </Typography>
              </Box>

              <Box sx={{ flex: 1, p: 1.5, bgcolor: "#F9F8F6" }}>
                {sp.traits.length === 0 ? (
                  <Typography sx={{ fontSize: "0.72rem", color: "#C9B59C" }}>
                    None recorded.
                  </Typography>
                ) : (
                  sp.traits.map((trait, idx) => (
                    <Box
                      key={idx}
                      sx={{ display: "flex", gap: 1, mb: 0.5 }}
                    >
                      <Typography sx={{ fontSize: "0.72rem", color: "#5c4230" }}>
                        ✓
                      </Typography>
                      <Typography sx={{ fontSize: "0.72rem", color: "#3a2820" }}>
                        {trait}
                      </Typography>
                    </Box>
                  ))
                )}
              </Box>
            </Box>
          </Box>
        </Box>
      )}

      {/* Bottom action bar */}
      <Box
        sx={{
          bgcolor: "#2a1e14",
          borderTop: "2px solid #5c4230",
          px: 2,
          py: 1,
          display: "flex",
          alignItems: "center",
          flexWrap: "wrap",
          gap: { xs: 1, md: 2 },
        }}
      >
        {["Save Sheet", "Print Folio"].map((label) => (
          <Box
            key={label}
            sx={{
              border: "1px solid #5c4230",
              borderRadius: 1,
              bgcolor: "#1a1008",
              px: 1.5,
              py: 0.5,
              cursor: "pointer",
              "&:hover": { bgcolor: "#3a2820" },
            }}
          >
            <Typography
              sx={{
                fontSize: "0.75rem",
                color: "#C9B59C",
                fontFamily: "'Cinzel', 'Georgia', serif",
                userSelect: "none",
              }}
            >
              {label}
            </Typography>
          </Box>
        ))}

        <Typography
          sx={{
            fontSize: "0.7rem",
            color: "#7d5e45",
            ml: "auto",
            fontFamily: "'Cinzel', 'Georgia', serif",
          }}
        >
          Gothic Character Folio
        </Typography>
      </Box>
    </Box>
  );
}
