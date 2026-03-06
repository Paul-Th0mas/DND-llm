"use client";

import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import Typography from "@mui/material/Typography";
import { useCampaignWorldGeneration } from "@/domains/campaign/hooks/useCampaignWorldGeneration";

/** Props for the GenerateCampaignWorldButton component. */
interface GenerateCampaignWorldButtonProps {
  readonly campaignId: string;
  readonly token: string;
}

/**
 * Renders a button that triggers POST /api/v1/campaigns/{id}/world.
 * Shows a loading indicator while the request is in flight and surfaces
 * errors inline below the button. On success the campaign store is updated
 * with the generated world detail automatically via the hook.
 */
export function GenerateCampaignWorldButton({
  campaignId,
  token,
}: GenerateCampaignWorldButtonProps): React.ReactElement {
  const { generateWorld, isGeneratingWorld, error } = useCampaignWorldGeneration();

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
      <Button
        variant="contained"
        onClick={() => void generateWorld(campaignId, token)}
        disabled={isGeneratingWorld}
        startIcon={isGeneratingWorld ? <CircularProgress size={16} color="inherit" /> : undefined}
        sx={{ textTransform: "none", fontWeight: 600, borderRadius: 2, alignSelf: "flex-start" }}
      >
        {isGeneratingWorld ? "Generating world..." : "Generate World"}
      </Button>

      {isGeneratingWorld && (
        <Typography variant="caption" color="text.secondary">
          Building your campaign world — this may take a few seconds.
        </Typography>
      )}

      {error !== null && (
        <Alert severity="error" sx={{ fontSize: "0.8rem" }}>
          {error}
        </Alert>
      )}
    </Box>
  );
}
