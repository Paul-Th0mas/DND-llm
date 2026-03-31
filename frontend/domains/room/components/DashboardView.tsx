"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import Typography from "@mui/material/Typography";
import { AppCard } from "@/shared/components/AppCard";
import { useAuthStore, selectUser, selectToken } from "@/shared/store/auth.store";
import { useAuth } from "@/domains/auth/hooks/useAuth";
import { CardStyleToggle } from "@/shared/components/CardStyleToggle";
import { CreateCampaignWizard } from "@/domains/campaign/components/CreateCampaignWizard";
import { StartSessionWizard } from "@/domains/campaign/components/StartSessionWizard";
import { useCampaignList } from "@/domains/campaign/hooks/useCampaignList";
import { LobbyTable } from "./LobbyTable";
import { listMyCharacters } from "@/domains/character/services/character.service";
import {
  useCharacterStore,
  selectMyCharacters,
} from "@/domains/character/store/character.store";
import { ApiError } from "@/lib/api/client";

// Tab index constants for readability.
const TAB_LOBBIES = 0 as const;
const TAB_MY_CHARACTERS = 1 as const;
const TAB_CAMPAIGNS = 2 as const;

/**
 * Main dashboard view rendered after authentication.
 * Redesigned with MUI Tabs (US-047):
 *   Tab 0 — Lobbies: existing join-room panel.
 *   Tab 1 — My Characters: list of characters owned by the authenticated user.
 *   Tab 2 — Campaigns (DM only): campaign list and create-campaign wizard.
 * The active tab is local component state — the URL does not change on switch.
 */
export function DashboardView(): React.ReactElement {
  const user = useAuthStore(selectUser);
  const token = useAuthStore(selectToken);
  const { logout } = useAuth();
  const router = useRouter();

  const [activeTab, setActiveTab] = useState<number>(TAB_LOBBIES);
  const [campaignWizardOpen, setCampaignWizardOpen] = useState(false);
  const [sessionWizardCampaignId, setSessionWizardCampaignId] = useState<string | null>(null);

  const { campaigns, isLoading: isCampaignsLoading, error: campaignsError, reload: reloadCampaigns } = useCampaignList(token ?? "");

  // Character list state
  const myCharacters = useCharacterStore(selectMyCharacters);
  const { setMyCharacters } = useCharacterStore();
  const [isLoadingCharacters, setIsLoadingCharacters] = useState(false);
  const [characterError, setCharacterError] = useState<string | null>(null);
  // Track whether we have already fetched for this session.
  const [charactersFetched, setCharactersFetched] = useState(false);

  const fetchMyCharacters = useCallback(async (): Promise<void> => {
    if (!token) return;
    setIsLoadingCharacters(true);
    setCharacterError(null);

    try {
      const data = await listMyCharacters(token);
      setMyCharacters(data.characters);
      setCharactersFetched(true);
    } catch (err: unknown) {
      if (err instanceof ApiError && err.status !== 401) {
        setCharacterError("Could not load your characters. Please try again.");
      }
    } finally {
      setIsLoadingCharacters(false);
    }
  }, [token, setMyCharacters]);

  // Fetch characters when the user first switches to the My Characters tab.
  // The result is cached in the Zustand store; subsequent tab switches do not
  // re-fetch within the same dashboard session.
  useEffect(() => {
    if (activeTab === TAB_MY_CHARACTERS && !charactersFetched && !isLoadingCharacters) {
      void fetchMyCharacters();
    }
  }, [activeTab, charactersFetched, isLoadingCharacters, fetchMyCharacters]);

  if (!user) {
    // Transient state — AuthProvider will redirect to /login.
    return <></>;
  }

  const isDm = user.role === "dm";

  return (
    <Box
      sx={{
        minHeight: "100vh",
        bgcolor: "background.default",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* Top bar */}
      <Box
        component="header"
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          px: { xs: 3, sm: 6 },
          py: 2.5,
          borderBottom: "1px solid",
          borderColor: "divider",
          bgcolor: "background.paper",
        }}
      >
        <Typography
          variant="h6"
          fontWeight={700}
          sx={{ color: "text.primary", letterSpacing: "-0.01em" }}
        >
          Dungeons and Droids
        </Typography>
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <Typography variant="body2" color="text.secondary">
            {user.name}{" "}
            <Box
              component="span"
              sx={{
                fontSize: "0.7rem",
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: "primary.main",
              }}
            >
              {isDm ? "DM" : "Player"}
            </Box>
          </Typography>
          <CardStyleToggle />
          <Button
            size="small"
            variant="outlined"
            onClick={() => {
              logout();
              router.replace("/login");
            }}
            sx={{ textTransform: "none", borderRadius: 2 }}
          >
            Log out
          </Button>
        </Box>
      </Box>

      {/* Tab navigation */}
      <Box
        sx={{
          borderBottom: "1px solid",
          borderColor: "divider",
          bgcolor: "background.paper",
          px: { xs: 3, sm: 6 },
        }}
      >
        <Tabs
          value={activeTab}
          onChange={(_, newValue: number) => setActiveTab(newValue)}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab label="Lobbies" value={TAB_LOBBIES} sx={{ textTransform: "none", fontWeight: 600 }} />
          <Tab label="My Characters" value={TAB_MY_CHARACTERS} sx={{ textTransform: "none", fontWeight: 600 }} />
          {/* Campaigns tab — only rendered in DOM for DM users (AC2). */}
          {isDm && (
            <Tab
              label="Campaigns"
              value={TAB_CAMPAIGNS}
              sx={{ textTransform: "none", fontWeight: 600 }}
            />
          )}
        </Tabs>
      </Box>

      {/* Tab panels */}
      <Box sx={{ flex: 1, px: { xs: 3, sm: 6 }, py: 4 }}>
        {/* Lobbies tab — shows the live lobby browser (US-032/US-033) */}
        {activeTab === TAB_LOBBIES && (
          <Box>
            <Typography
              variant="h5"
              fontWeight={700}
              sx={{ mb: 3, color: "text.primary" }}
            >
              Open Lobbies
            </Typography>
            <LobbyTable token={token ?? ""} />
          </Box>
        )}

        {/* My Characters tab (AC5-AC7, AC11-AC12) */}
        {activeTab === TAB_MY_CHARACTERS && (
          <Box>
            <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 3 }}>
              <Typography
                variant="h5"
                fontWeight={700}
                sx={{ color: "text.primary" }}
              >
                My Characters
              </Typography>
              <Button
                component={Link}
                href="/world"
                variant="contained"
                sx={{
                  textTransform: "none",
                  bgcolor: "#7d5e45",
                  "&:hover": { bgcolor: "#5c4230" },
                }}
              >
                Create Character
              </Button>
            </Box>

            {isLoadingCharacters && (
              <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
                <CircularProgress />
              </Box>
            )}

            {!isLoadingCharacters && characterError !== null && (
              <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
                <Alert severity="error">{characterError}</Alert>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => {
                    setCharactersFetched(false);
                    void fetchMyCharacters();
                  }}
                  sx={{ alignSelf: "flex-start", textTransform: "none" }}
                >
                  Retry
                </Button>
              </Box>
            )}

            {!isLoadingCharacters && characterError === null && charactersFetched && (
              <>
                {myCharacters === null || myCharacters.length === 0 ? (
                  <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
                    <Typography
                      variant="body2"
                      sx={{ color: "#C9B59C" }}
                    >
                      You have not created any characters yet.
                    </Typography>
                    <Button
                      component={Link}
                      href="/world"
                      variant="outlined"
                      sx={{
                        alignSelf: "flex-start",
                        textTransform: "none",
                        borderColor: "#7d5e45",
                        color: "#7d5e45",
                        "&:hover": {
                          borderColor: "#5c4230",
                          color: "#5c4230",
                        },
                      }}
                    >
                      Browse Worlds
                    </Button>
                  </Box>
                ) : (
                  <Box className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {myCharacters.map((character, index) => (
                      <Link
                        key={character.id}
                        href={`/world/${character.world_id}/character/${character.id}`}
                        style={{ textDecoration: "none", display: "block" }}
                      >
                        <AppCard
                          title={character.name}
                          subtitle={
                            character.class_name !== null
                              ? `${character.class_name}${character.species_name !== null ? ` \u2022 ${character.species_name}` : ""}`
                              : undefined
                          }
                          chips={
                            character.world_name !== null
                              ? [
                                  <Chip
                                    key="world"
                                    label={character.world_name}
                                    size="small"
                                    sx={{
                                      bgcolor: "#D9CFC7",
                                      color: "#3a2820",
                                      fontSize: "0.7rem",
                                    }}
                                  />,
                                ]
                              : undefined
                          }
                          staggerIndex={index}
                        />
                      </Link>
                    ))}
                  </Box>
                )}
              </>
            )}
          </Box>
        )}

        {/* Campaigns tab — DM only (AC8). Never rendered for players (isDm guard). */}
        {isDm && activeTab === TAB_CAMPAIGNS && (
          <Box>
            <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 3 }}>
              <Typography variant="h5" fontWeight={700} sx={{ color: "text.primary" }}>
                My Campaigns
              </Typography>
              <Button
                variant="contained"
                onClick={() => setCampaignWizardOpen(true)}
                sx={{
                  textTransform: "none",
                  fontWeight: 600,
                  borderRadius: 2,
                  bgcolor: "#7d5e45",
                  "&:hover": { bgcolor: "#5c4230" },
                }}
              >
                Create Campaign
              </Button>
            </Box>

            {isCampaignsLoading && (
              <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
                <CircularProgress />
              </Box>
            )}

            {!isCampaignsLoading && campaignsError !== null && (
              <Alert
                severity="error"
                action={
                  <Button color="inherit" size="small" onClick={reloadCampaigns}>
                    Retry
                  </Button>
                }
              >
                {campaignsError}
              </Alert>
            )}

            {!isCampaignsLoading && campaignsError === null && campaigns.length === 0 && (
              <Typography variant="body2" sx={{ color: "#C9B59C" }}>
                You have not created any campaigns yet.
              </Typography>
            )}

            {!isCampaignsLoading && campaignsError === null && campaigns.length > 0 && (
              <Box className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {campaigns.map((campaign, index) => (
                  <Box
                    key={campaign.campaign_id}
                    onClick={() => router.push(`/campaign/${campaign.campaign_id}`)}
                    sx={{ cursor: "pointer" }}
                  >
                    <AppCard
                      title={campaign.name}
                      chips={[
                        <Chip
                          key="tone"
                          label={campaign.tone.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                          size="small"
                          sx={{ bgcolor: "#D9CFC7", color: "#3a2820", fontSize: "0.7rem" }}
                        />,
                      ]}
                      actions={
                        <Button
                          variant="outlined"
                          size="small"
                          fullWidth
                          onClick={(e) => {
                            // Prevent the card-level navigation from firing.
                            e.stopPropagation();
                            setSessionWizardCampaignId(campaign.campaign_id);
                          }}
                          sx={{
                            textTransform: "none",
                            borderColor: "#7d5e45",
                            color: "#7d5e45",
                            "&:hover": { borderColor: "#5c4230", color: "#5c4230" },
                          }}
                        >
                          Start Session
                        </Button>
                      }
                      staggerIndex={index}
                    >
                      <Typography variant="caption" color="text.secondary">
                        {campaign.player_count}{" "}
                        {campaign.player_count === 1 ? "player" : "players"}
                        {campaign.world_name !== null && ` \u2022 ${campaign.world_name}`}
                      </Typography>
                    </AppCard>
                  </Box>
                ))}
              </Box>
            )}
          </Box>
        )}
      </Box>

      {/* Campaign creation wizard — DM only */}
      {isDm && (
        <CreateCampaignWizard
          open={campaignWizardOpen}
          onClose={() => setCampaignWizardOpen(false)}
          onCreated={(id) => {
            setCampaignWizardOpen(false);
            reloadCampaigns();
            router.push(`/campaign/${id}/world`);
          }}
        />
      )}

      {/* Session wizard — opens when a campaign's Start Session is clicked */}
      {isDm && sessionWizardCampaignId !== null && (
        <StartSessionWizard
          open
          onClose={() => {
            setSessionWizardCampaignId(null);
            reloadCampaigns();
          }}
          campaignId={sessionWizardCampaignId}
        />
      )}
    </Box>
  );
}
