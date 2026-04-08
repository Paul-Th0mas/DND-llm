"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Skeleton from "@mui/material/Skeleton";
import Typography from "@mui/material/Typography";
import { getCharacterClasses } from "@/domains/character/services/character.service";
import { ApiError } from "@/lib/api/client";
import type { CharacterClass } from "@/domains/character/types";

/** Props for ClassSelectionGrid. */
export interface ClassSelectionGridProps {
  /** The world theme used to filter available classes. */
  readonly worldTheme: string;
  /** The currently selected class ID, or null if none chosen. */
  readonly selectedClassId: string | null;
  /** Callback invoked when the player selects a class card. */
  readonly onSelect: (classId: string) => void;
}

/**
 * Displays a grid of selectable character class cards filtered by world theme.
 * Handles loading, empty, and error states as per US-026 acceptance criteria.
 * Each card shows: display_name, hit_die as "d{n}", primary_ability,
 * and a "Spellcaster" badge if the class has a spellcasting_ability.
 * Uses Modern Scriptorium visual design (US-060).
 */
export function ClassSelectionGrid({
  worldTheme,
  selectedClassId,
  onSelect,
}: ClassSelectionGridProps): React.ReactElement {
  const [classes, setClasses] = useState<readonly CharacterClass[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    getCharacterClasses(worldTheme)
      .then((data) => {
        if (!cancelled) setClasses(data.classes);
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          if (err instanceof ApiError) {
            setError(`Failed to load classes: ${err.detail}`);
          } else {
            setError("Failed to load character classes.");
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
            getCharacterClasses(worldTheme)
              .then((data) => setClasses(data.classes))
              .catch(() => setError("Failed to load character classes."))
              .finally(() => setIsLoading(false));
          }}
          sx={{ alignSelf: "flex-start", textTransform: "none" }}
        >
          Retry
        </Button>
      </Box>
    );
  }

  if (classes.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary">
        No classes available for this world theme.
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
          Choose Your Path
        </Typography>
        <Typography
          sx={{
            fontFamily: "var(--font-work-sans), sans-serif",
            fontSize: "1.125rem",
            color: "#695e45",
            maxWidth: "42rem",
          }}
        >
          The stars align and your destiny beckons. Select a class to define
          your role in the chronicles yet to be written.
        </Typography>
      </Box>

      {/* Class card grid */}
      <Box className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {classes.map((cls) => {
          const isSelected = cls.id === selectedClassId;

          return (
            <div
              key={cls.id}
              onClick={() => onSelect(cls.id)}
              className="group relative overflow-hidden rounded-xl transition-all duration-300 hover:scale-[1.02] cursor-pointer"
              style={{
                backgroundColor: "#fdf2df",
                boxShadow: isSelected
                  ? "0 0 0 2px rgba(114,90,66,0.2)"
                  : "none",
                outline: isSelected ? "2px solid rgba(114,90,66,0.2)" : "none",
              }}
            >
              {/* Image area */}
              <div className="relative overflow-hidden h-48">
                {/* Spellcaster badge — shown only when class has a spellcasting ability */}
                {cls.spellcasting_ability !== null && (
                  <span
                    className="absolute top-3 left-3 z-10 text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded-full"
                    style={{
                      background: "linear-gradient(135deg, #725a42 0%, #fedcbe 100%)",
                      color: "#fff6f1",
                    }}
                  >
                    Spellcaster
                  </span>
                )}

                <Image
                  src="/character-placeholder.png"
                  alt={cls.display_name}
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
                {/* Row 1: class name + icon */}
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
                    {cls.display_name}
                  </Typography>
                  <span
                    className="material-symbols-outlined"
                    style={{ fontSize: "2rem", color: "#725a42" }}
                  >
                    auto_awesome
                  </span>
                </div>

                {/* Row 2: Hit Die + Primary Stat */}
                <div className="flex gap-4 mb-4">
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
                      Hit Die
                    </p>
                    <Typography
                      sx={{
                        fontFamily: "var(--font-newsreader), serif",
                        fontWeight: 700,
                        fontSize: "1.125rem",
                        color: "#3a311b",
                      }}
                    >
                      d{cls.hit_die}
                    </Typography>
                  </div>

                  {/* Left-border divider on second col */}
                  <div
                    style={{
                      borderLeft: "1px solid #bfb193",
                      paddingLeft: "1rem",
                    }}
                  >
                    <p
                      style={{
                        fontSize: "10px",
                        textTransform: "uppercase",
                        letterSpacing: "0.1em",
                        color: "#86795e",
                        marginBottom: "2px",
                      }}
                    >
                      Primary Stat
                    </p>
                    <Typography
                      sx={{
                        fontFamily: "var(--font-newsreader), serif",
                        fontWeight: 700,
                        fontSize: "1.125rem",
                        color: "#6c5c4d",
                      }}
                    >
                      {cls.primary_ability}
                    </Typography>
                  </div>
                </div>

                {/* Row 3: description placeholder */}
                <p
                  className="mb-5"
                  style={{
                    fontStyle: "italic",
                    fontSize: "0.875rem",
                    color: "#695e45",
                    lineHeight: 1.5,
                  }}
                >
                  A formidable archetype wielding their talents in service of the realm.
                </p>

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
                      onSelect(cls.id);
                    }}
                    className="w-full py-2 font-bold text-[10px] uppercase tracking-widest rounded transition-all hover:bg-[#f5e7cb] hover:text-[#725a42]"
                    style={{
                      border: "1px solid #bfb193",
                      color: "#86795e",
                      background: "transparent",
                      cursor: "pointer",
                    }}
                  >
                    Inscribe Destiny
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
