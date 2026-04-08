"use client";

import Image from "next/image";
import Link from "next/link";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import Typography from "@mui/material/Typography";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import EditIcon from "@mui/icons-material/Edit";
import MapIcon from "@mui/icons-material/Map";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import type { CharacterSummary } from "@/domains/character/types";

/** Props for the CharacterCard component. */
export interface CharacterCardProps {
  /** Character summary data from the list endpoint. */
  readonly character: CharacterSummary;
}

/**
 * Displays a single character as an editorial card in the Modern Scriptorium style.
 * Features a portrait image (placeholder when none available), class/species metadata,
 * a serif name heading, world association, and action buttons.
 *
 * Used in the "My Characters" tab of DashboardView.
 */
export function CharacterCard({ character }: CharacterCardProps): React.ReactElement {
  const viewSheetHref = `/world/${character.world_id}/character/${character.id}`;

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        bgcolor: "#fdf2df",
        borderRadius: "0.75rem",
        overflow: "hidden",
        transition: "box-shadow 500ms ease",
        "&:hover": {
          boxShadow: "0 24px 48px rgba(58,49,27,0.07)",
        },
        // On hover, desaturate effect reversal and scale are handled on the img via CSS.
        "&:hover .char-img": {
          filter: "grayscale(0)",
          transform: "scale(1.05)",
        },
        "&:hover .char-name": {
          color: "#725a42",
        },
      }}
    >
      {/* Portrait image — 16:9 aspect ratio */}
      <Box
        sx={{
          position: "relative",
          width: "100%",
          paddingTop: "56.25%", // 16:9
          overflow: "hidden",
        }}
      >
        <Image
          src="/character-placeholder.png"
          alt={character.name}
          fill
          className="char-img"
          style={{
            objectFit: "cover",
            filter: "grayscale(0.2)",
            transition: "filter 700ms ease, transform 700ms ease",
          }}
        />
        {/* Bottom-to-transparent gradient overlay */}
        <Box
          sx={{
            position: "absolute",
            inset: 0,
            background:
              "linear-gradient(to top, #fdf2df 0%, transparent 60%)",
          }}
        />
      </Box>

      {/* Card body — overlaps image with -mt-12 */}
      <Box
        sx={{
          p: 4,
          display: "flex",
          flexDirection: "column",
          gap: 3,
          mt: -6,
          position: "relative",
          zIndex: 1,
        }}
      >
        {/* Class + Species label */}
        <Box sx={{ display: "flex", flexDirection: "column", gap: 0.25 }}>
          {(character.class_name !== null || character.species_name !== null) && (
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                gap: 1,
                fontFamily: "var(--font-work-sans), sans-serif",
                fontSize: "0.65rem",
                fontWeight: 700,
                letterSpacing: "0.15em",
                textTransform: "uppercase",
                color: "rgba(114,90,66,0.7)",
              }}
            >
              {character.class_name !== null && (
                <span>{character.class_name}</span>
              )}
              {character.class_name !== null && character.species_name !== null && (
                <Box
                  component="span"
                  sx={{
                    width: 4,
                    height: 4,
                    borderRadius: "50%",
                    bgcolor: "#bfb193",
                    display: "inline-block",
                  }}
                />
              )}
              {character.species_name !== null && (
                <span>{character.species_name}</span>
              )}
            </Box>
          )}

          {/* Name — large Newsreader serif */}
          <Typography
            component="h2"
            className="char-name"
            sx={{
              fontFamily: "var(--font-newsreader), serif",
              fontSize: { xs: "2rem", sm: "2.25rem" },
              fontWeight: 700,
              color: "#3a311b",
              letterSpacing: "-0.02em",
              lineHeight: 1.1,
              transition: "color 300ms ease",
            }}
          >
            {character.name}
          </Typography>
        </Box>

        {/* Metadata row — world name */}
        {character.world_name !== null && (
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              gap: 3,
              color: "#695e45",
            }}
          >
            <Box sx={{ display: "flex", alignItems: "center", gap: 0.75 }}>
              <MapIcon sx={{ fontSize: 16 }} />
              <Typography
                component="span"
                sx={{
                  fontFamily: "var(--font-work-sans), sans-serif",
                  fontSize: "0.8rem",
                  fontWeight: 500,
                }}
              >
                {character.world_name}
              </Typography>
            </Box>
          </Box>
        )}

        {/* Footer actions */}
        <Box
          sx={{
            pt: 2,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            borderTop: "1px solid rgba(191,177,147,0.15)",
          }}
        >
          {/* View Sheet link */}
          <Link href={viewSheetHref} style={{ textDecoration: "none" }}>
            <Box
              component="span"
              sx={{
                display: "inline-flex",
                alignItems: "center",
                gap: 0.75,
                fontFamily: "var(--font-work-sans), sans-serif",
                fontSize: "0.8rem",
                fontWeight: 700,
                color: "#725a42",
                px: 1.5,
                py: 1,
                borderRadius: "0.375rem",
                cursor: "pointer",
                transition: "background-color 150ms ease",
                "&:hover": { bgcolor: "#f5e7cb" },
                "& .arrow-icon": {
                  transition: "transform 150ms ease",
                },
                "&:hover .arrow-icon": {
                  transform: "translateX(3px)",
                },
              }}
            >
              View Sheet
              <ArrowForwardIcon className="arrow-icon" sx={{ fontSize: 14 }} />
            </Box>
          </Link>

          {/* Action icon buttons */}
          <Box sx={{ display: "flex", ml: "-4px" }}>
            <IconButton
              size="small"
              sx={{
                width: 32,
                height: 32,
                bgcolor: "#f1e1c1",
                border: "2px solid #fdf2df",
                borderRadius: "50%",
                color: "#695e45",
                "&:hover": { bgcolor: "#f5e7cb" },
              }}
            >
              <EditIcon sx={{ fontSize: 14 }} />
            </IconButton>
            <IconButton
              size="small"
              sx={{
                width: 32,
                height: 32,
                bgcolor: "#f1e1c1",
                border: "2px solid #fdf2df",
                borderRadius: "50%",
                color: "#695e45",
                ml: "-4px",
                "&:hover": { bgcolor: "#f5e7cb" },
              }}
            >
              <MoreVertIcon sx={{ fontSize: 14 }} />
            </IconButton>
          </Box>
        </Box>
      </Box>
    </Box>
  );
}
