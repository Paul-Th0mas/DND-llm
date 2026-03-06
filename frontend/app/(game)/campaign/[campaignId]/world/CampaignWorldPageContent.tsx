"use client";

import { useParams, useRouter } from "next/navigation";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { DmOnlyRoute } from "@/shared/components/DmOnlyRoute";
import { CampaignWorldView } from "@/domains/campaign/components/CampaignWorldView";
import { GenerateCampaignWorldButton } from "@/domains/campaign/components/GenerateCampaignWorldButton";
import {
  selectCampaignWorld,
  useCampaignStore,
} from "@/domains/campaign/store/campaign.store";
import { useAuthStore, selectUser } from "@/shared/store/auth.store";

/**
 * Client component for the campaign world page.
 * If a world has been generated this session it shows CampaignWorldView.
 * Otherwise it shows the GenerateCampaignWorldButton to trigger generation.
 * Reads the campaign ID from the URL params.
 */
export function CampaignWorldPageContent(): React.ReactElement {
  const router = useRouter();
  const params = useParams();
  // campaignId comes from the [campaignId] segment — always a string in this context.
  const campaignId = typeof params.campaignId === "string" ? params.campaignId : "";
  const campaignWorld = useCampaignStore(selectCampaignWorld);
  const user = useAuthStore(selectUser);
  const token = typeof window !== "undefined" ? (localStorage.getItem("access_token") ?? "") : "";

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
            onClick={() => router.push("/campaign")}
            sx={{ textTransform: "none", color: "text.secondary" }}
          >
            Campaign
          </Button>
          <Typography variant="h6" fontWeight={700} sx={{ ml: 1 }}>
            Campaign World
          </Typography>
        </Box>

        {/* Content */}
        <Box sx={{ px: { xs: 3, sm: 6 }, py: 4, maxWidth: 900, mx: "auto" }}>
          {campaignWorld !== null ? (
            // isDm is always true here — DmOnlyRoute already guards this page.
            <CampaignWorldView world={campaignWorld} isDm={user?.role === "dm"} />
          ) : (
            <Box sx={{ py: 4 }}>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                No world generated yet
              </Typography>
              <Typography variant="body1" color="text.secondary" gutterBottom>
                Generate the campaign world to populate it with settlements, factions, NPCs, and adventure hooks.
              </Typography>
              <Box sx={{ mt: 3 }}>
                <GenerateCampaignWorldButton campaignId={campaignId} token={token} />
              </Box>
            </Box>
          )}
        </Box>
      </Box>
    </DmOnlyRoute>
  );
}
