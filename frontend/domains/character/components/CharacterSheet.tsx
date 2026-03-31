"use client";

import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Divider from "@mui/material/Divider";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Typography from "@mui/material/Typography";
import type { AbilityKey, CharacterSheet as CharacterSheetData } from "@/domains/character/types";

/** Ability label metadata for rendering the score grid. */
const ABILITY_LABELS: { key: AbilityKey; abbrev: string; label: string }[] = [
  { key: "strength", abbrev: "STR", label: "Strength" },
  { key: "dexterity", abbrev: "DEX", label: "Dexterity" },
  { key: "constitution", abbrev: "CON", label: "Constitution" },
  { key: "intelligence", abbrev: "INT", label: "Intelligence" },
  { key: "wisdom", abbrev: "WIS", label: "Wisdom" },
  { key: "charisma", abbrev: "CHA", label: "Charisma" },
];

/**
 * Computes the D&D ability score modifier: floor((score - 10) / 2).
 * @param score - The raw ability score (e.g. 15).
 * @returns The modifier as a signed string (e.g. "+2", "-1", "+0").
 */
function formatModifier(score: number): string {
  const mod = Math.floor((score - 10) / 2);
  if (mod > 0) return `+${mod}`;
  return `${mod}`;
}

/** Props for CharacterSheet. */
export interface CharacterSheetProps {
  /** The full character sheet data as returned by the API. */
  readonly character: CharacterSheetData;
}

/**
 * Read-only character sheet display component for US-030.
 * Renders: header (name, class, species), ability score grid with modifiers,
 * background block, and species traits list.
 * All data is display-only — no editing controls are shown.
 */
export function CharacterSheet({
  character,
}: CharacterSheetProps): React.ReactElement {
  const cls = character.character_class;
  const sp = character.species;

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      {/* Header: name, class, species */}
      <Box>
        <Typography
          variant="h4"
          fontWeight={800}
          sx={{ color: "#1e1410", letterSpacing: "-0.02em", mb: 0.5 }}
        >
          {character.name}
        </Typography>
        <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
          <Chip
            label={cls.display_name}
            size="small"
            sx={{
              bgcolor: "#EFE9E3",
              color: "#3a2820",
              fontWeight: 600,
              border: "1px solid #D9CFC7",
            }}
          />
          <Chip
            label={sp.display_name}
            size="small"
            sx={{
              bgcolor: "#EFE9E3",
              color: "#3a2820",
              fontWeight: 600,
              border: "1px solid #D9CFC7",
            }}
          />
          {cls.spellcasting_ability !== null && (
            <Chip
              label="Spellcaster"
              size="small"
              sx={{
                bgcolor: "#a07d60",
                color: "#F9F8F6",
                fontWeight: 600,
              }}
            />
          )}
        </Box>
      </Box>

      <Divider />

      {/* Ability Score Grid — 3 columns */}
      <Box>
        <Typography
          variant="subtitle1"
          fontWeight={700}
          sx={{ mb: 2, color: "#3a2820" }}
        >
          Ability Scores
        </Typography>
        <Box
          className="grid grid-cols-3 gap-3"
          sx={{ maxWidth: 480 }}
        >
          {ABILITY_LABELS.map(({ key, abbrev }) => {
            const score = character.ability_scores[key];
            const mod = formatModifier(score);
            return (
              <Card
                key={key}
                variant="outlined"
                sx={{
                  bgcolor: "#EFE9E3",
                  border: "1px solid #D9CFC7",
                  textAlign: "center",
                }}
              >
                <CardContent sx={{ py: "12px !important", px: 1 }}>
                  <Typography
                    variant="caption"
                    fontWeight={700}
                    sx={{
                      color: "#7d5e45",
                      letterSpacing: "0.08em",
                      textTransform: "uppercase",
                    }}
                  >
                    {abbrev}
                  </Typography>
                  <Typography
                    variant="h5"
                    fontWeight={800}
                    sx={{ color: "#1e1410", lineHeight: 1.2 }}
                  >
                    {score}
                  </Typography>
                  <Typography variant="body2" fontWeight={600} sx={{ color: "#5c4230" }}>
                    {mod}
                  </Typography>
                </CardContent>
              </Card>
            );
          })}
        </Box>
      </Box>

      <Divider />

      {/* Background */}
      {character.background.trim().length > 0 && (
        <Box>
          <Typography
            variant="subtitle1"
            fontWeight={700}
            sx={{ mb: 1, color: "#3a2820" }}
          >
            Background
          </Typography>
          <Typography
            variant="body1"
            sx={{
              color: "#3a2820",
              whiteSpace: "pre-wrap",
              lineHeight: 1.7,
            }}
          >
            {character.background}
          </Typography>
        </Box>
      )}

      {/* Species traits — omit section if empty */}
      {sp.traits.length > 0 && (
        <>
          <Divider />
          <Box>
            <Typography
              variant="subtitle1"
              fontWeight={700}
              sx={{ mb: 1, color: "#3a2820" }}
            >
              Species Traits
            </Typography>
            <List dense disablePadding>
              {sp.traits.map((trait, idx) => (
                <ListItem key={idx} disableGutters disablePadding>
                  <ListItemText
                    primary={trait}
                    primaryTypographyProps={{
                      variant: "body2",
                      color: "text.primary",
                      sx: { "&::before": { content: '"• "' } },
                    }}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        </>
      )}

      {/* Class details strip */}
      <Divider />
      <Box sx={{ display: "flex", gap: 3, flexWrap: "wrap" }}>
        <Box>
          <Typography variant="caption" color="text.secondary" fontWeight={600}>
            HIT DIE
          </Typography>
          <Typography variant="body1" fontWeight={700} sx={{ color: "#1e1410" }}>
            d{cls.hit_die}
          </Typography>
        </Box>
        <Box>
          <Typography variant="caption" color="text.secondary" fontWeight={600}>
            PRIMARY ABILITY
          </Typography>
          <Typography variant="body1" fontWeight={700} sx={{ color: "#1e1410" }}>
            {cls.primary_ability}
          </Typography>
        </Box>
        {cls.spellcasting_ability !== null && (
          <Box>
            <Typography variant="caption" color="text.secondary" fontWeight={600}>
              SPELLCASTING
            </Typography>
            <Typography variant="body1" fontWeight={700} sx={{ color: "#1e1410" }}>
              {cls.spellcasting_ability}
            </Typography>
          </Box>
        )}
        <Box>
          <Typography variant="caption" color="text.secondary" fontWeight={600}>
            SPECIES SIZE
          </Typography>
          <Typography variant="body1" fontWeight={700} sx={{ color: "#1e1410" }}>
            {sp.size}
          </Typography>
        </Box>
        <Box>
          <Typography variant="caption" color="text.secondary" fontWeight={600}>
            SPEED
          </Typography>
          <Typography variant="body1" fontWeight={700} sx={{ color: "#1e1410" }}>
            {sp.speed} ft
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}
