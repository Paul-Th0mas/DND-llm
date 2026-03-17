"use client";

import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import Typography from "@mui/material/Typography";
import { useCampaignWorldGeneration } from "@/domains/campaign/hooks/useCampaignWorldGeneration";

/** Props for the GenerateCampaignWorldButton component. */
export interface GenerateCampaignWorldButtonProps {
  /** UUID of the campaign to generate a world for. */
  readonly campaignId: string;
  /** JWT access token of the authenticated DM. */
  readonly token: string;
}

/**
 * Button that triggers LLM world generation for a given campaign.
 * Shows a spinner and disables the button while generation is in progress.
 * Displays an error alert if generation fails.
 */
export function GenerateCampaignWorldButton({
  campaignId,
  token,
}: GenerateCampaignWorldButtonProps): React.ReactElement {
  const { generate, isGenerating, error } = useCampaignWorldGeneration();

  function handleClick(): void {
    void generate(campaignId, token);
  }

  if (isGenerating) {
    return (
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 2,
          py: 6,
        }}
      >
        <CircularProgress size={40} />
        <Typography variant="body2" color="text.secondary">
          Generating campaign world — this may take a moment...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
      {error !== null && (
        <Alert severity="error">{error}</Alert>
      )}

      <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 2, py: 4 }}>
        <Typography variant="body1" color="text.secondary" textAlign="center">
          No world has been generated for this campaign yet.
        </Typography>
        <Button
          variant="contained"
          onClick={handleClick}
          disabled={isGenerating}
          sx={{ textTransform: "none", fontWeight: 600, borderRadius: 2 }}
        >
          Generate Campaign World
        </Button>
      </Box>
    </Box>
  );
}
