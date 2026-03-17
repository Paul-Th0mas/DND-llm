"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Divider from "@mui/material/Divider";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import Typography from "@mui/material/Typography";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { DmOnlyRoute } from "@/shared/components/DmOnlyRoute";
import { getCampaignById } from "@/domains/campaign/services/campaign.service";
import { getWorldById } from "@/domains/world/services/world.service";
import {
  selectCampaignWorld,
  useCampaignStore,
} from "@/domains/campaign/store/campaign.store";
import { CampaignWorldView } from "@/domains/campaign/components/CampaignWorldView";
import { GenerateCampaignWorldButton } from "@/domains/campaign/components/GenerateCampaignWorldButton";
import type { WorldDetail } from "@/domains/world/types";
import { ApiError } from "@/lib/api/client";

/** Props for the CampaignWorldPageContent component. */
export interface CampaignWorldPageContentProps {
  readonly campaignId: string;
}

/**
 * Converts an underscore-separated string to Title Case for display.
 * @param value - The raw string (e.g. "MEDIEVAL_FANTASY").
 * @returns A human-readable label (e.g. "Medieval Fantasy").
 */
function toLabel(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * Client component for the campaign world detail page.
 * Renders two tabs:
 *   - "World Lore" — pre-seeded world detail (lore, factions, bosses) fetched from the API.
 *   - "Campaign World" — LLM-generated campaign world from the store, or a generate button.
 * DM-only; players are blocked at the DmOnlyRoute boundary.
 */
export function CampaignWorldPageContent({
  campaignId,
}: CampaignWorldPageContentProps): React.ReactElement {
  const router = useRouter();
  const campaignWorld = useCampaignStore(selectCampaignWorld);
  const [world, setWorld] = useState<WorldDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [token, setToken] = useState("");

  // Read token client-side only.
  useEffect(() => {
    setToken(localStorage.getItem("access_token") ?? "");
  }, []);

  useEffect(() => {
    if (!campaignId) return;

    let cancelled = false;
    const storedToken = localStorage.getItem("access_token") ?? "";

    async function fetchData(): Promise<void> {
      setIsLoading(true);
      setError(null);

      try {
        // Step 1: fetch campaign to get world_id.
        const campaign = await getCampaignById(campaignId, storedToken);
        if (cancelled) return;

        // Step 2: fetch world detail using world_id from campaign.
        const worldDetail = await getWorldById(campaign.world_id);
        if (!cancelled) {
          setWorld(worldDetail);
        }
      } catch (err) {
        if (!cancelled) {
          if (err instanceof ApiError) {
            if (err.status === 404) {
              setError("Campaign or world not found.");
            } else if (err.status === 401 || err.status === 403) {
              setError("You are not authorised to view this campaign.");
            } else {
              setError(`Failed to load: ${err.detail}`);
            }
          } else {
            setError("Failed to load the campaign world. Please try again.");
          }
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    void fetchData();

    return () => {
      cancelled = true;
    };
  }, [campaignId]);

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
            Campaigns
          </Button>
          <Typography variant="h6" fontWeight={700} sx={{ ml: 1 }}>
            Campaign World
          </Typography>
        </Box>

        {/* Tab navigation */}
        <Box sx={{ borderBottom: "1px solid", borderColor: "divider", bgcolor: "background.paper" }}>
          <Tabs
            value={activeTab}
            onChange={(_, v: number) => setActiveTab(v)}
            sx={{ px: { xs: 3, sm: 6 } }}
          >
            <Tab label="World Lore" id="tab-world-lore" aria-controls="tabpanel-world-lore" />
            <Tab label="Campaign World" id="tab-campaign-world" aria-controls="tabpanel-campaign-world" />
          </Tabs>
        </Box>

        {/* Content */}
        <Box sx={{ px: { xs: 3, sm: 6 }, py: 4, maxWidth: 900, mx: "auto" }}>
          {/* Tab 0: Pre-seeded world lore */}
          {activeTab === 0 && (
            <Box role="tabpanel" id="tabpanel-world-lore" aria-labelledby="tab-world-lore">
              {isLoading && (
                <Box sx={{ display: "flex", justifyContent: "center", py: 10 }}>
                  <CircularProgress />
                </Box>
              )}

              {!isLoading && error !== null && (
                <Alert severity="error">{error}</Alert>
              )}

              {!isLoading && error === null && world !== null && (
                <Box sx={{ display: "flex", flexDirection: "column", gap: 4 }}>
                  {/* World name and theme */}
                  <Box>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, mb: 1 }}>
                      <Typography variant="h5" fontWeight={700}>
                        {world.name}
                      </Typography>
                      <Chip label={toLabel(world.theme)} variant="outlined" />
                    </Box>
                    <Typography variant="body1" color="text.secondary">
                      {world.description}
                    </Typography>
                  </Box>

                  <Divider />

                  {/* Lore summary */}
                  <Box>
                    <Typography variant="h6" fontWeight={700} gutterBottom>
                      Lore
                    </Typography>
                    <Typography variant="body2" sx={{ lineHeight: 1.8 }}>
                      {world.lore_summary}
                    </Typography>
                  </Box>

                  {/* Factions */}
                  {world.factions.length > 0 && (
                    <>
                      <Divider />
                      <Box>
                        <Typography variant="h6" fontWeight={700} gutterBottom>
                          Factions
                        </Typography>
                        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                          {world.factions.map((faction) => (
                            <Box
                              key={faction.name}
                              sx={{
                                p: 2,
                                borderRadius: 2,
                                border: "1px solid",
                                borderColor: "divider",
                                bgcolor: "background.paper",
                              }}
                            >
                              <Typography variant="subtitle2" fontWeight={700} gutterBottom>
                                {faction.name}
                              </Typography>
                              <Box sx={{ display: "flex", gap: 1, mb: 1, flexWrap: "wrap" }}>
                                <Chip label={faction.alignment} size="small" variant="outlined" />
                                <Typography variant="caption" color="text.secondary" sx={{ alignSelf: "center" }}>
                                  {faction.public_reputation}
                                </Typography>
                              </Box>
                              <Typography variant="body2" color="text.secondary">
                                {faction.description}
                              </Typography>
                            </Box>
                          ))}
                        </div>
                      </Box>
                    </>
                  )}

                  {/* Bosses */}
                  {world.bosses.length > 0 && (
                    <>
                      <Divider />
                      <Box>
                        <Typography variant="h6" fontWeight={700} gutterBottom>
                          Bosses
                        </Typography>
                        <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
                          {world.bosses.map((boss) => (
                            <Box
                              key={boss.name}
                              sx={{
                                p: 2.5,
                                borderRadius: 2,
                                border: "1px solid",
                                borderColor: "divider",
                                bgcolor: "background.paper",
                              }}
                            >
                              <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, mb: 1 }}>
                                <Typography variant="subtitle1" fontWeight={700}>
                                  {boss.name}
                                </Typography>
                                <Chip label={`CR ${boss.challenge_rating}`} size="small" color="error" variant="outlined" />
                              </Box>
                              <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
                                {boss.description}
                              </Typography>
                              {boss.abilities.length > 0 && (
                                <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, mb: 1.5 }}>
                                  {boss.abilities.map((ability) => (
                                    <Chip key={ability} label={ability} size="small" variant="outlined" />
                                  ))}
                                </Box>
                              )}
                              <Typography variant="body2" sx={{ fontStyle: "italic", color: "text.secondary" }}>
                                {boss.lore}
                              </Typography>
                            </Box>
                          ))}
                        </Box>
                      </Box>
                    </>
                  )}
                </Box>
              )}
            </Box>
          )}

          {/* Tab 1: LLM-generated campaign world */}
          {activeTab === 1 && (
            <Box role="tabpanel" id="tabpanel-campaign-world" aria-labelledby="tab-campaign-world">
              {campaignWorld !== null ? (
                <CampaignWorldView world={campaignWorld} isDM />
              ) : (
                <GenerateCampaignWorldButton campaignId={campaignId} token={token} />
              )}
            </Box>
          )}
        </Box>
      </Box>
    </DmOnlyRoute>
  );
}
