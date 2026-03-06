"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import AddIcon from "@mui/icons-material/Add";
import { DmOnlyRoute } from "@/shared/components/DmOnlyRoute";
import { CreateCampaignWizard } from "@/domains/campaign/components/CreateCampaignWizard";
import { selectCampaignId, useCampaignStore } from "@/domains/campaign/store/campaign.store";

/**
 * Client component for the campaign creation page.
 * Shows a prompt to create a campaign if none exists, or a link to the
 * campaign world page if a campaign has already been created this session.
 */
export function CampaignPageContent(): React.ReactElement {
  const router = useRouter();
  const [wizardOpen, setWizardOpen] = useState(false);
  const campaignId = useCampaignStore(selectCampaignId);

  function handleCreated(id: string): void {
    router.push(`/campaign/${id}/world`);
  }

  return (
    <DmOnlyRoute>
      <Box sx={{ minHeight: "100vh", bgcolor: "background.default" }}>
        {/* Page header */}
        <Box
          component="header"
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 1,
            px: { xs: 3, sm: 6 },
            py: 2,
            borderBottom: "1px solid",
            borderColor: "divider",
            bgcolor: "background.paper",
          }}
        >
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => router.push("/dashboard")}
            sx={{ textTransform: "none", color: "text.secondary" }}
          >
            Dashboard
          </Button>
          <Typography variant="h6" fontWeight={700} sx={{ ml: 1 }}>
            Campaign
          </Typography>
        </Box>

        {/* Content */}
        <Box
          sx={{
            px: { xs: 3, sm: 6 },
            py: 8,
            maxWidth: 600,
            mx: "auto",
            textAlign: "center",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 3,
          }}
        >
          {campaignId !== null ? (
            <>
              <Typography variant="h6" fontWeight={600}>
                Campaign created
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Your campaign is ready. Proceed to generate the world.
              </Typography>
              <Button
                variant="contained"
                onClick={() => router.push(`/campaign/${campaignId}/world`)}
                sx={{ textTransform: "none", fontWeight: 600, borderRadius: 2 }}
              >
                View Campaign World
              </Button>
            </>
          ) : (
            <>
              <Typography variant="h5" fontWeight={700}>
                Create a Campaign
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Define your campaign requirements and let the AI generate a complete world for you.
              </Typography>
              <Button
                variant="contained"
                size="large"
                startIcon={<AddIcon />}
                onClick={() => setWizardOpen(true)}
                sx={{
                  textTransform: "none",
                  fontWeight: 600,
                  fontSize: "1rem",
                  borderRadius: 2.5,
                  px: 4,
                  py: 1.5,
                }}
              >
                Create Campaign
              </Button>
            </>
          )}
        </Box>
      </Box>

      <CreateCampaignWizard
        open={wizardOpen}
        onClose={() => setWizardOpen(false)}
        onCreated={handleCreated}
      />
    </DmOnlyRoute>
  );
}
