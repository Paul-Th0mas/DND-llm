import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";

/**
 * Loading state for the world detail page.
 * Shown by Next.js while the page is suspending.
 */
export default function WorldDetailLoading(): React.ReactElement {
  return (
    <Box
      className="flex min-h-screen items-center justify-center"
      aria-label="Loading world"
    >
      <CircularProgress sx={{ color: "#a07d60" }} />
    </Box>
  );
}
