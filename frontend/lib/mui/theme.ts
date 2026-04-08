"use client";

import { createTheme } from "@mui/material/styles";

// "Modern Scriptorium" palette — sourced from stitch design system.
// Warmer, amber-leaning parchment tones with earthy browns.
const palette = {
  surface: "#fff8f1",
  surfaceContainerLow: "#fdf2df",
  surfaceContainerHigh: "#f5e7cb",
  surfaceContainerHighest: "#f1e1c1",
  onSurface: "#3a311b",
  onSurfaceVariant: "#695e45",
  primary: "#725a42",
  primaryDim: "#654e37",
  onPrimary: "#fff6f1",
  primaryContainer: "#fedcbe",
  onPrimaryContainer: "#654d37",
  outlineVariant: "#bfb193",
  outline: "#86795e",
  error: "#9e422c",
} as const;

/**
 * MUI theme for the DnD Frontend application.
 * Implements the "Modern Scriptorium" design system.
 * Uses Work Sans for UI text and Newsreader for editorial headings.
 */
export const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      light: palette.primaryContainer,
      main: palette.primary,
      dark: palette.primaryDim,
      contrastText: palette.onPrimary,
    },
    secondary: {
      light: palette.surfaceContainerLow,
      main: palette.outlineVariant,
      dark: palette.outline,
      contrastText: palette.onSurface,
    },
    background: {
      default: palette.surface,
      paper: palette.surfaceContainerLow,
    },
    text: {
      primary: palette.onSurface,
      secondary: palette.onSurfaceVariant,
      disabled: palette.outlineVariant,
    },
    divider: palette.outlineVariant,
    error: {
      main: palette.error,
    },
  },
  typography: {
    fontFamily: "var(--font-work-sans), Arial, Helvetica, sans-serif",
  },
  shape: {
    // sm radius from design system — approachable, never sharp 90-degree corners.
    borderRadius: 6,
  },
});
