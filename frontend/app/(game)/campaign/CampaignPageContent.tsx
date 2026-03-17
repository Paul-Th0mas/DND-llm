"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Skeleton from "@mui/material/Skeleton";
import Typography from "@mui/material/Typography";
import AddIcon from "@mui/icons-material/Add";
import { DmOnlyRoute } from "@/shared/components/DmOnlyRoute";
import { StartSessionWizard } from "@/domains/campaign/components/StartSessionWizard";
import { useCampaignList } from "@/domains/campaign/hooks/useCampaignList";

/**
 * Converts an underscore-separated string to Title Case for display.
 * @param value - The raw string (e.g. "dark_fantasy").
 * @returns A human-readable label (e.g. "Dark Fantasy").
 */
function toLabel(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * Formats an ISO date string to a short human-readable date (e.g. "12 Mar 2026").
 * @param iso - ISO 8601 date string from the backend.
 * @returns Formatted date string.
 */
function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

/**
 * Three skeleton placeholder cards shown while the campaign list is loading.
 * Uses MUI Skeleton to match the shape of a real campaign card.
 */
function SkeletonCards(): React.ReactElement {
  return (
    <>
      {[0, 1, 2].map((i) => (
        <Card key={i} variant="outlined">
          <CardContent>
            <Skeleton variant="text" width="60%" height={28} />
            <Skeleton variant="text" width="40%" height={20} sx={{ mt: 1 }} />
            <Skeleton variant="text" width="50%" height={20} />
            <Skeleton
              variant="rectangular"
              width={80}
              height={32}
              sx={{ mt: 2, borderRadius: 1 }}
            />
          </CardContent>
        </Card>
      ))}
    </>
  );
}

/**
 * Client component for the campaign list hub page.
 * Fetches all DM-owned campaigns and displays them in a card grid.
 * New campaign flow navigates to /world instead of opening an inline wizard.
 * Each card exposes a "Start Session" button that opens StartSessionWizard
 * for that specific campaign without navigating away.
 */
export function CampaignPageContent(): React.ReactElement {
  const router = useRouter();
  // wizardCampaignId is non-null when the session wizard is open for a campaign.
  const [wizardCampaignId, setWizardCampaignId] = useState<string | null>(null);

  // Safe to read localStorage here because this is a client component.
  const token =
    typeof window !== "undefined"
      ? (localStorage.getItem("access_token") ?? "")
      : "";
  const { campaigns, isLoading, error, reload } = useCampaignList(token);

  function handleWizardClose(): void {
    setWizardCampaignId(null);
    // Refresh dungeon counts in case a session was started.
    reload();
  }

  return (
    <DmOnlyRoute>
      <Box sx={{ minHeight: "100vh", bgcolor: "background.default" }}>
        {/* Page header with breadcrumb */}
        <Box
          component="header"
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            px: { xs: 3, sm: 6 },
            py: 2,
            borderBottom: "1px solid",
            borderColor: "divider",
            bgcolor: "background.paper",
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <Link href="/dashboard" style={{ textDecoration: "none" }}>
              <Typography
                variant="body2"
                sx={{
                  color: "text.secondary",
                  "&:hover": { color: "text.primary" },
                }}
              >
                Dashboard
              </Typography>
            </Link>
            <Typography variant="body2" color="text.disabled">
              /
            </Typography>
            <Typography variant="body2" fontWeight={700}>
              Campaigns
            </Typography>
          </Box>

          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => router.push("/world")}
            sx={{ textTransform: "none", fontWeight: 600, borderRadius: 2 }}
          >
            New Campaign
          </Button>
        </Box>

        {/* Main content */}
        <Box sx={{ px: { xs: 3, sm: 6 }, py: 4, maxWidth: 1100, mx: "auto" }}>
          {/* Error state with retry */}
          {!isLoading && error !== null && (
            <Alert
              severity="error"
              sx={{ mb: 3 }}
              action={
                <Button color="inherit" size="small" onClick={reload}>
                  Retry
                </Button>
              }
            >
              {error}
            </Alert>
          )}

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {/* New Campaign slot — always rendered first */}
            <Card
              variant="outlined"
              sx={{
                border: "2px dashed",
                borderColor: "divider",
                cursor: "pointer",
                "&:hover": { borderColor: "primary.main" },
              }}
              onClick={() => router.push("/world")}
            >
              <CardContent
                sx={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  minHeight: 140,
                  gap: 1,
                }}
              >
                <AddIcon sx={{ fontSize: 32, color: "text.disabled" }} />
                <Typography variant="body2" color="text.secondary" fontWeight={600}>
                  New Campaign
                </Typography>
              </CardContent>
            </Card>

            {/* Loading placeholders */}
            {isLoading && <SkeletonCards />}

            {/* Empty state — shown after load when no campaigns exist */}
            {!isLoading && error === null && campaigns.length === 0 && (
              <Box
                sx={{
                  gridColumn: "1 / -1",
                  display: "flex",
                  justifyContent: "center",
                  py: 6,
                }}
              >
                <Box
                  sx={{
                    border: "2px dashed",
                    borderColor: "divider",
                    borderRadius: 2,
                    p: 4,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: 1.5,
                    maxWidth: 340,
                    textAlign: "center",
                  }}
                >
                  <AddIcon sx={{ fontSize: 40, color: "text.disabled" }} />
                  <Typography variant="body1" color="text.secondary">
                    Create your first campaign
                  </Typography>
                  <Button
                    variant="contained"
                    onClick={() => router.push("/world")}
                    sx={{ textTransform: "none", borderRadius: 2, mt: 1 }}
                  >
                    Get started
                  </Button>
                </Box>
              </Box>
            )}

            {/* Campaign cards */}
            {!isLoading &&
              campaigns.map((campaign) => (
                <Card key={campaign.campaign_id} variant="outlined">
                  {/* CardActionArea handles the navigate-to-detail click */}
                  <CardActionArea
                    onClick={() =>
                      router.push(`/campaign/${campaign.campaign_id}`)
                    }
                  >
                    <CardContent>
                      <Typography variant="subtitle1" fontWeight={700} gutterBottom>
                        {campaign.name}
                      </Typography>

                      <Box
                        sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}
                      >
                        <Chip
                          label={toLabel(campaign.tone)}
                          size="small"
                          variant="outlined"
                        />
                        <Typography variant="caption" color="text.secondary">
                          {campaign.player_count}{" "}
                          {campaign.player_count === 1 ? "player" : "players"}
                        </Typography>
                      </Box>

                      <Typography
                        variant="caption"
                        color="text.secondary"
                        display="block"
                        gutterBottom
                      >
                        {campaign.world_name ?? "World unavailable"}
                      </Typography>

                      <Box
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          mt: 1,
                        }}
                      >
                        <Typography variant="caption" color="text.disabled">
                          {formatDate(campaign.created_at)}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {campaign.dungeon_count}{" "}
                          {campaign.dungeon_count === 1 ? "dungeon" : "dungeons"}
                        </Typography>
                      </Box>
                    </CardContent>
                  </CardActionArea>

                  {/* Start Session button sits outside CardActionArea so its click
                      does not also trigger the card navigation. */}
                  <Box sx={{ px: 2, pb: 2 }}>
                    <Button
                      variant="outlined"
                      size="small"
                      fullWidth
                      onClick={(e) => {
                        e.stopPropagation();
                        setWizardCampaignId(campaign.campaign_id);
                      }}
                      sx={{ textTransform: "none", borderRadius: 2 }}
                    >
                      Start Session
                    </Button>
                  </Box>
                </Card>
              ))}
          </div>
        </Box>
      </Box>

      {/* Session wizard — rendered only when a campaign is selected */}
      {wizardCampaignId !== null && (
        <StartSessionWizard
          open
          onClose={handleWizardClose}
          campaignId={wizardCampaignId}
        />
      )}
    </DmOnlyRoute>
  );
}
