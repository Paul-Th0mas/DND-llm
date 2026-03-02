"use client";

import { createTheme } from "@mui/material/styles";

// Parchment earth tone palette — sourced from project design tokens.
const palette = {
  parchment50: "#F9F8F6",
  parchment100: "#EFE9E3",
  parchment200: "#D9CFC7",
  parchment300: "#C9B59C",
  parchment400: "#b89a7e",
  parchment500: "#a07d60",
  parchment600: "#7d5e45",
  parchment700: "#5c4230",
  parchment800: "#3a2820",
  parchment900: "#1e1410",
} as const;

/**
 * MUI theme for the DnD Frontend application.
 * Maps the parchment palette to MUI theme tokens.
 * Import this and pass it to ThemeProvider in the root layout.
 */
export const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      light: palette.parchment400,
      main: palette.parchment500,
      dark: palette.parchment600,
      contrastText: palette.parchment50,
    },
    secondary: {
      light: palette.parchment200,
      main: palette.parchment300,
      dark: palette.parchment400,
      contrastText: palette.parchment800,
    },
    background: {
      default: palette.parchment50,
      paper: palette.parchment100,
    },
    text: {
      primary: palette.parchment900,
      secondary: palette.parchment700,
      disabled: palette.parchment300,
    },
    divider: palette.parchment200,
  },
  typography: {
    fontFamily: "var(--font-geist-sans), Arial, Helvetica, sans-serif",
  },
  shape: {
    borderRadius: 8,
  },
});
