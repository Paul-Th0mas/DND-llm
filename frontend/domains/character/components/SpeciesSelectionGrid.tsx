"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Skeleton from "@mui/material/Skeleton";
import Typography from "@mui/material/Typography";
import { getCharacterSpecies } from "@/domains/character/services/character.service";
import { ApiError } from "@/lib/api/client";
import type { CharacterSpecies } from "@/domains/character/types";

/** Props for SpeciesSelectionGrid. */
export interface SpeciesSelectionGridProps {
  /** The world theme used to filter available species. */
  readonly worldTheme: string;
  /** The currently selected species ID, or null if none chosen. */
  readonly selectedSpeciesId: string | null;
  /** Callback invoked when the player selects a species card. */
  readonly onSelect: (speciesId: string) => void;
}

/**
 * Displays a grid of selectable character species cards filtered by world theme.
 * Handles loading, empty, and error states as per US-027 acceptance criteria.
 * Each card shows: display_name, size, speed as "{n} ft", and all traits.
 * Uses Modern Scriptorium visual design (US-061).
 */
export function SpeciesSelectionGrid({
  worldTheme,
  selectedSpeciesId,
  onSelect,
}: SpeciesSelectionGridProps): React.ReactElement {
  const [species, setSpecies] = useState<readonly CharacterSpecies[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    getCharacterSpecies(worldTheme)
      .then((data) => {
        if (!cancelled) setSpecies(data.species);
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          if (err instanceof ApiError) {
            setError(`Failed to load species: ${err.detail}`);
          } else {
            setError("Failed to load character species.");
          }
        }
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [worldTheme]);

  if (isLoading) {
    return (
      <Box className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton
            key={i}
            variant="rectangular"
            height={288}
            sx={{ borderRadius: "0.75rem", bgcolor: "#fdf2df" }}
          />
        ))}
      </Box>
    );
  }

  if (error !== null) {
    return (
      <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
        <Alert severity="error">{error}</Alert>
        <Button
          variant="outlined"
          size="small"
          onClick={() => {
            setError(null);
            setIsLoading(true);
            getCharacterSpecies(worldTheme)
              .then((data) => setSpecies(data.species))
              .catch(() => setError("Failed to load character species."))
              .finally(() => setIsLoading(false));
          }}
          sx={{ alignSelf: "flex-start", textTransform: "none" }}
        >
          Retry
        </Button>
      </Box>
    );
  }

  if (species.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary">
        No species available for this world theme.
      </Typography>
    );
  }

  return (
    <Box>
      {/* Hero header */}
      <Box sx={{ mb: 6 }}>
        <Typography
          component="h2"
          sx={{
            fontFamily: "var(--font-newsreader), serif",
            fontWeight: 800,
            fontSize: { xs: "2.75rem", md: "3.75rem" },
            color: "#3a311b",
            lineHeight: 1.1,
            mb: 1.5,
          }}
        >
          Choose Your Species
        </Typography>
        <Typography
          sx={{
            fontFamily: "var(--font-work-sans), sans-serif",
            fontSize: "1.125rem",
            color: "#695e45",
            maxWidth: "42rem",
          }}
        >
          Your species defines your heritage and innate capabilities. It is the
          vessel through which your legend shall be poured. Choose wisely, for
          these traits are woven into your very soul.
        </Typography>
      </Box>

      {/* Species card grid */}
      <Box className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {species.map((sp) => {
          const isSelected = sp.id === selectedSpeciesId;

          return (
            <div
              key={sp.id}
              onClick={() => onSelect(sp.id)}
              className="group relative overflow-hidden rounded-xl transition-all duration-300 hover:scale-[1.02] cursor-pointer"
              style={{
                backgroundColor: "#fdf2df",
                outline: isSelected ? "2px solid rgba(114,90,66,0.2)" : "none",
              }}
            >
              {/* Image area */}
              <div className="relative overflow-hidden h-48">
                <Image
                  src="/character-placeholder.png"
                  alt={sp.display_name}
                  fill
                  className="object-cover transition-transform duration-500 group-hover:scale-110"
                />
                {/* Gradient overlay fading into the card background */}
                <div
                  className="absolute inset-0"
                  style={{
                    background: "linear-gradient(to top, #fdf2df 0%, transparent 60%)",
                  }}
                />
              </div>

              {/* Card body */}
              <div className="p-6">
                {/* Row 1: species name + icon */}
                <div className="flex items-center justify-between mb-4">
                  <Typography
                    component="h3"
                    sx={{
                      fontFamily: "var(--font-newsreader), serif",
                      fontWeight: 700,
                      fontSize: "1.875rem",
                      color: "#725a42",
                      lineHeight: 1,
                    }}
                  >
                    {sp.display_name}
                  </Typography>
                  <span
                    className="material-symbols-outlined"
                    style={{ fontSize: "2rem", color: "#bfb193" }}
                  >
                    shield
                  </span>
                </div>

                {/* Row 2: Size + Speed */}
                <div className="flex gap-4 mb-6">
                  <div>
                    <p
                      style={{
                        fontSize: "10px",
                        textTransform: "uppercase",
                        letterSpacing: "0.1em",
                        color: "#86795e",
                        marginBottom: "2px",
                      }}
                    >
                      Size
                    </p>
                    <p
                      style={{
                        fontWeight: 700,
                        fontSize: "0.9375rem",
                        color: "#3a311b",
                      }}
                    >
                      {sp.size}
                    </p>
                  </div>

                  {/* Vertical divider */}
                  <div
                    className="h-8 self-center"
                    style={{ width: "1px", background: "rgba(191,177,147,0.2)" }}
                  />

                  <div>
                    <p
                      style={{
                        fontSize: "10px",
                        textTransform: "uppercase",
                        letterSpacing: "0.1em",
                        color: "#86795e",
                        marginBottom: "2px",
                      }}
                    >
                      Speed
                    </p>
                    <p
                      style={{
                        fontWeight: 700,
                        fontSize: "0.9375rem",
                        color: "#3a311b",
                      }}
                    >
                      {sp.speed} ft
                    </p>
                  </div>
                </div>

                {/* Row 3: traits list */}
                {sp.traits.length > 0 && (
                  <div className="flex flex-col gap-1 mb-5">
                    {sp.traits.map((trait, idx) => (
                      <div key={idx} className="flex items-center gap-2">
                        <span
                          className="material-symbols-outlined"
                          style={{ fontSize: "0.875rem", color: "#86795e" }}
                        >
                          auto_awesome
                        </span>
                        <span
                          style={{
                            fontSize: "0.875rem",
                            color: "#695e45",
                          }}
                        >
                          {trait}
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Row 4: action button */}
                {isSelected ? (
                  <button
                    type="button"
                    onClick={(e) => e.stopPropagation()}
                    className="w-full py-2 font-bold text-[10px] uppercase tracking-widest rounded transition-all"
                    style={{
                      background: "linear-gradient(135deg, #725a42 0%, #fedcbe 100%)",
                      color: "#fff6f1",
                      border: "none",
                      cursor: "default",
                    }}
                  >
                    Current Choice
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelect(sp.id);
                    }}
                    className="w-full py-2 font-bold text-[10px] uppercase tracking-widest rounded transition-all hover:bg-[#f5e7cb] hover:text-[#725a42]"
                    style={{
                      border: "1px solid #bfb193",
                      color: "#86795e",
                      background: "transparent",
                      cursor: "pointer",
                    }}
                  >
                    Select {sp.display_name}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </Box>
    </Box>
  );
}
