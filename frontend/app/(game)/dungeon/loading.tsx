"use client";
import { Box, CircularProgress, Typography } from "@mui/material";

/**
 * Suspense loading UI for the dungeon view route.
 * Shown while the page bundle is loading or during navigation.
 */
export default function DungeonLoading() {
  return (
    <Box className="flex flex-col items-center justify-center min-h-screen gap-4">
      <CircularProgress />
      <Typography variant="body2" color="text.secondary">
        Loading dungeon...
      </Typography>
    </Box>
  );
}
