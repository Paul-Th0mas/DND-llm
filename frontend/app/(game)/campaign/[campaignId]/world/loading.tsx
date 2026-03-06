import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import Typography from "@mui/material/Typography";

/**
 * Suspense loading UI for the campaign world route.
 * World generation via LLM can take several seconds — this shows while the
 * page bundle loads, not while the API is in flight (that is handled inline).
 */
export default function CampaignWorldLoading(): React.ReactElement {
  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 2,
        bgcolor: "background.default",
      }}
    >
      <CircularProgress size={40} />
      <Typography variant="body2" color="text.secondary">
        Loading campaign world...
      </Typography>
    </Box>
  );
}
