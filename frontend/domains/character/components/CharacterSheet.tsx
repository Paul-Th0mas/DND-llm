"use client";

import { useState } from "react";
import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
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
 * Character sheet layout using the parchment palette.
 * Renders a tab bar, 3-column body (ability scores | portrait + info | combat + skills),
 * and a bottom action bar.
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
        border: "2px solid #D9CFC7",
        borderRadius: 2,
        overflow: "hidden",
        bgcolor: "#F9F8F6",
      }}
    >
      {/* Tab navigation bar */}
      <Box
        sx={{
          bgcolor: "#EFE9E3",
          borderBottom: "1px solid #D9CFC7",
          display: "flex",
          alignItems: "flex-end",
          px: 1,
          pt: 1,
          overflowX: "auto",
          gap: 0.5,
        }}
      >
        {TABS.map((tab) => (
          <Box
            key={tab}
            onClick={() => setActiveTab(tab)}
            sx={{
              px: 2,
              py: 0.75,
              cursor: "pointer",
              bgcolor: activeTab === tab ? "#F9F8F6" : "transparent",
              border: "1px solid",
              borderColor: activeTab === tab ? "#D9CFC7" : "transparent",
              borderBottom: activeTab === tab ? "1px solid #F9F8F6" : "1px solid transparent",
              borderRadius: "4px 4px 0 0",
              flexShrink: 0,
              mb: "-1px",
              "&:hover": {
                bgcolor: activeTab === tab ? "#F9F8F6" : "#D9CFC7",
              },
            }}
          >
            <Typography
              sx={{
                fontSize: { xs: "0.68rem", md: "0.78rem" },
                fontFamily: "'Cinzel', 'Georgia', serif",
                color: activeTab === tab ? "#3a2820" : "#7d5e45",
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
        <Typography sx={{ p: 3, color: "#7d5e45" }}>Coming soon</Typography>
      ) : (
        <Box sx={{ display: "flex", flexDirection: { xs: "column", md: "row" }, minHeight: 460 }}>
          {/* Left panel - ability scores */}
          <Box
            sx={{
              width: { xs: "100%", md: 200 },
              flexShrink: 0,
              borderRight: { xs: "none", md: "1px solid #D9CFC7" },
              borderBottom: { xs: "1px solid #D9CFC7", md: "none" },
              bgcolor: "#F9F8F6",
              p: 2,
            }}
          >
            {/* Title badge */}
            <Box
              sx={{
                border: "1px solid #C9B59C",
                borderRadius: 1,
                bgcolor: "#EFE9E3",
                textAlign: "center",
                py: 0.75,
                px: 0.5,
                mb: 2,
              }}
            >
              <Typography
                sx={{
                  fontFamily: "'Cinzel', 'Georgia', serif",
                  color: "#5c4230",
                  fontSize: "0.75rem",
                  lineHeight: 1.3,
                  fontWeight: 600,
                }}
              >
                Character Folio
              </Typography>
            </Box>

            {/* Ability score grid */}
            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: { xs: "repeat(3, 1fr)", md: "1fr 1fr" },
                gap: 1,
              }}
            >
              {ABILITY_LABELS.map(({ key, abbrev }) => {
                const score = scores[key];
                return (
                  <Box
                    key={key}
                    sx={{
                      border: "1px solid #C9B59C",
                      borderRadius: 1,
                      bgcolor: "#EFE9E3",
                      textAlign: "center",
                      py: 0.75,
                      px: 0.5,
                    }}
                  >
                    <Typography
                      sx={{
                        fontSize: "0.6rem",
                        color: "#7d5e45",
                        textTransform: "uppercase",
                        letterSpacing: "0.1em",
                        fontWeight: 700,
                      }}
                    >
                      {abbrev}
                    </Typography>
                    <Typography
                      sx={{
                        fontSize: "1.25rem",
                        fontWeight: 700,
                        color: "#1e1410",
                        lineHeight: 1.2,
                      }}
                    >
                      {score}
                    </Typography>
                    {/* Modifier pill */}
                    <Box
                      sx={{
                        display: "inline-block",
                        bgcolor: "#a07d60",
                        borderRadius: "8px",
                        px: 0.75,
                        mt: 0.25,
                      }}
                    >
                      <Typography sx={{ fontSize: "0.7rem", color: "#F9F8F6", fontWeight: 600 }}>
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
              borderRight: { xs: "none", md: "1px solid #D9CFC7" },
              borderBottom: { xs: "1px solid #D9CFC7", md: "none" },
              display: "flex",
              flexDirection: "column",
            }}
          >
            {/* Portrait area */}
            <Box
              sx={{
                bgcolor: "#EFE9E3",
                minHeight: { xs: 140, md: 180 },
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                borderBottom: "1px solid #D9CFC7",
              }}
            >
              <Box
                sx={{
                  width: 100,
                  height: 140,
                  border: "1px solid #C9B59C",
                  borderRadius: 1,
                  bgcolor: "#D9CFC7",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <Typography sx={{ color: "#7d5e45", fontSize: "0.75rem" }}>
                  Portrait
                </Typography>
              </Box>
            </Box>

            {/* Character Information section */}
            <Box>
              {/* Section header */}
              <Box sx={{ bgcolor: "#EFE9E3", borderBottom: "1px solid #D9CFC7", px: 1.5, py: 0.5 }}>
                <Typography
                  sx={{
                    fontSize: "0.65rem",
                    fontWeight: 700,
                    color: "#5c4230",
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
                  { label: "Background", value: truncatedBackground || "None" },
                ].map(({ label, value }) => (
                  <Box key={label} sx={{ display: "flex", gap: 1, mb: 0.5 }}>
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
                    <Typography sx={{ fontSize: "0.72rem", color: "#5c4230" }}>
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
            <Box sx={{ display: "flex", borderBottom: "1px solid #D9CFC7" }}>
              {/* Combat Overview */}
              <Box
                sx={{
                  flex: 1,
                  borderRight: "1px solid #D9CFC7",
                  display: "flex",
                  flexDirection: "column",
                }}
              >
                <Box sx={{ bgcolor: "#EFE9E3", borderBottom: "1px solid #D9CFC7", px: 1.5, py: 0.5 }}>
                  <Typography
                    sx={{
                      fontSize: "0.6rem",
                      fontWeight: 700,
                      color: "#5c4230",
                      letterSpacing: "0.08em",
                      textTransform: "uppercase",
                      fontFamily: "'Cinzel', 'Georgia', serif",
                    }}
                  >
                    Combat
                  </Typography>
                </Box>

                <Box
                  sx={{
                    p: 1.5,
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: 1,
                    bgcolor: "#F9F8F6",
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
                        sx={{ fontSize: "0.85rem", fontWeight: 700, color: "#1e1410" }}
                      >
                        {value}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </Box>

              {/* Equipment & Spells */}
              <Box sx={{ flex: 1, display: "flex", flexDirection: "column" }}>
                <Box sx={{ bgcolor: "#EFE9E3", borderBottom: "1px solid #D9CFC7", px: 1.5, py: 0.5 }}>
                  <Typography
                    sx={{
                      fontSize: "0.6rem",
                      fontWeight: 700,
                      color: "#5c4230",
                      letterSpacing: "0.08em",
                      textTransform: "uppercase",
                      fontFamily: "'Cinzel', 'Georgia', serif",
                    }}
                  >
                    Equipment
                  </Typography>
                </Box>

                <Box sx={{ p: 1.5, bgcolor: "#F9F8F6" }}>
                  {[
                    { label: "Weapons", value: "-" },
                    { label: "Armor", value: "-" },
                    { label: "Hit Die", value: `d${cls.hit_die}` },
                    { label: "Primary", value: cls.primary_ability },
                    ...(cls.spellcasting_ability !== null
                      ? [{ label: "Spell Ability", value: cls.spellcasting_ability }]
                      : []),
                  ].map(({ label, value }) => (
                    <Box key={label} sx={{ display: "flex", gap: 0.5, mb: 0.5 }}>
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
              <Box sx={{ bgcolor: "#EFE9E3", borderBottom: "1px solid #D9CFC7", px: 1.5, py: 0.5 }}>
                <Typography
                  sx={{
                    fontSize: "0.65rem",
                    fontWeight: 700,
                    color: "#5c4230",
                    letterSpacing: "0.08em",
                    textTransform: "uppercase",
                    fontFamily: "'Cinzel', 'Georgia', serif",
                  }}
                >
                  Skills & Traits
                </Typography>
              </Box>

              <Box sx={{ flex: 1, p: 1.5, bgcolor: "#F9F8F6" }}>
                {sp.traits.length === 0 ? (
                  <Typography sx={{ fontSize: "0.72rem", color: "#C9B59C" }}>
                    None recorded.
                  </Typography>
                ) : (
                  sp.traits.map((trait, idx) => (
                    <Box key={idx} sx={{ display: "flex", gap: 1, mb: 0.5 }}>
                      <Typography sx={{ fontSize: "0.72rem", color: "#a07d60" }}>-</Typography>
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
      <Divider sx={{ borderColor: "#D9CFC7" }} />
      <Box
        sx={{
          bgcolor: "#EFE9E3",
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
              border: "1px solid #C9B59C",
              borderRadius: 1,
              bgcolor: "#F9F8F6",
              px: 1.5,
              py: 0.5,
              cursor: "pointer",
              "&:hover": { bgcolor: "#D9CFC7" },
            }}
          >
            <Typography
              sx={{
                fontSize: "0.75rem",
                color: "#5c4230",
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
            color: "#C9B59C",
            ml: "auto",
            fontFamily: "'Cinzel', 'Georgia', serif",
          }}
        >
          Character Folio
        </Typography>
      </Box>
    </Box>
  );
}
