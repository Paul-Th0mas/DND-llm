"use client";

import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import Typography from "@mui/material/Typography";

/**
 * Suspense loading UI for the campaign detail route.
 * Shown while the page bundle is loading or during navigation.
 */
export default function CampaignDetailLoading(): React.ReactElement {
  return (
    <Box className="flex flex-col items-center justify-center min-h-screen gap-4">
      <CircularProgress />
      <Typography variant="body2" color="text.secondary">
        Loading campaign...
      </Typography>
    </Box>
  );
}
