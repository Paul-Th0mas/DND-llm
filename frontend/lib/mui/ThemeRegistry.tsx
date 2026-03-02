"use client";

import { AppRouterCacheProvider } from "@mui/material-nextjs/v15-appRouter";
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { theme } from "./theme";

interface ThemeRegistryProps {
  readonly children: React.ReactNode;
}

/**
 * Wraps the application with MUI ThemeProvider and CssBaseline.
 * AppRouterCacheProvider ensures emotion styles are correctly injected
 * during SSR with the Next.js App Router, preventing hydration mismatches.
 * Must be rendered as a Client Component because MUI requires it.
 * Place this in the root layout to apply the theme globally.
 */
export function ThemeRegistry({ children }: ThemeRegistryProps) {
  return (
    <AppRouterCacheProvider>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </AppRouterCacheProvider>
  );
}
