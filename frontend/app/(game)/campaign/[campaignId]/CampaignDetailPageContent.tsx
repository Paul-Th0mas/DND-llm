"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Divider from "@mui/material/Divider";
import Skeleton from "@mui/material/Skeleton";
import Typography from "@mui/material/Typography";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { ProtectedRoute } from "@/shared/components/ProtectedRoute";
import { getCampaignById, listCampaignDungeons } from "@/domains/campaign/services/campaign.service";
import { getWorldById } from "@/domains/world/services/world.service";
import { StartSessionWizard } from "@/domains/campaign/components/StartSessionWizard";
import { CampaignPartyRoster } from "@/domains/character/components/CampaignPartyRoster";
import { CharacterPickerModal } from "@/domains/character/components/CharacterPickerModal";
import { useAuthStore, selectUser } from "@/shared/store/auth.store";
import { ApiError } from "@/lib/api/client";
import type { CampaignDetail } from "@/domains/campaign/types";
import type { WorldDetail } from "@/domains/world/types";
import type { DungeonSummary } from "@/domains/dungeon/types";

/** Props for the CampaignDetailPageContent component. */
export interface CampaignDetailPageContentProps {
  readonly campaignId: string;
}

// Maximum number of past dungeons to display in the list.
const MAX_PAST_DUNGEONS = 10 as const;

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
 * Client component for the campaign detail page.
 * Fetches the campaign by ID, its associated world, and the list of past dungeons.
 * Provides a "Start Session" button that opens StartSessionWizard, which generates
 * a dungeon and immediately creates a game room in a single two-step flow.
 * Restricted to DM users via DmOnlyRoute.
 */
export function CampaignDetailPageContent({
  campaignId,
}: CampaignDetailPageContentProps): React.ReactElement {
  const router = useRouter();
  const user = useAuthStore(selectUser);
  const isDm = user?.role === "dm";

  const [campaign, setCampaign] = useState<CampaignDetail | null>(null);
  const [world, setWorld] = useState<WorldDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Dungeon list has its own loading/error state so it doesn't block the rest
  // of the page (AC3: skeleton in section only; AC5: isolated error).
  const [dungeons, setDungeons] = useState<readonly DungeonSummary[]>([]);
  const [dungeonsLoading, setDungeonsLoading] = useState(true);
  const [dungeonsError, setDungeonsError] = useState<string | null>(null);

  const [wizardOpen, setWizardOpen] = useState(false);
  const [pickerOpen, setPickerOpen] = useState(false);
  // Roster key incremented after a successful link to force CampaignPartyRoster to re-fetch.
  const [rosterKey, setRosterKey] = useState(0);

  useEffect(() => {
    if (!campaignId) return;

    let cancelled = false;
    const token = localStorage.getItem("access_token") ?? "";

    async function fetchCampaignAndWorld(): Promise<void> {
      setIsLoading(true);
      setError(null);

      try {
        const campaignData = await getCampaignById(campaignId, token);
        if (cancelled) return;

        const worldData = await getWorldById(campaignData.world_id);

        if (!cancelled) {
          setCampaign(campaignData);
          setWorld(worldData);
        }
      } catch (err) {
        if (!cancelled) {
          if (err instanceof ApiError) {
            if (err.status === 404) {
              setError("Campaign not found.");
            } else if (err.status === 401 || err.status === 403) {
              setError("You are not authorised to view this campaign.");
            } else {
              setError(`Failed to load campaign: ${err.detail}`);
            }
          } else {
            setError("Failed to load the campaign. Please try again.");
          }
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    async function fetchDungeons(): Promise<void> {
      setDungeonsLoading(true);
      setDungeonsError(null);

      try {
        const list = await listCampaignDungeons(campaignId, token);
        if (!cancelled) {
          setDungeons(list.slice(0, MAX_PAST_DUNGEONS));
        }
      } catch {
        if (!cancelled) {
          setDungeonsError("Failed to load past dungeons.");
        }
      } finally {
        if (!cancelled) setDungeonsLoading(false);
      }
    }

    // Run both fetches in parallel — dungeon list does not block campaign display.
    void fetchCampaignAndWorld();
    void fetchDungeons();

    return () => {
      cancelled = true;
    };
  }, [campaignId]);

  function handleSessionStarted(): void {
    // Refresh the dungeon list after a successful session start so the new
    // dungeon and room appear immediately without a full page reload.
    const token = localStorage.getItem("access_token") ?? "";
    setDungeonsLoading(true);
    setDungeonsError(null);
    listCampaignDungeons(campaignId, token)
      .then((list) => {
        setDungeons(list.slice(0, MAX_PAST_DUNGEONS));
      })
      .catch(() => {
        setDungeonsError("Failed to refresh past dungeons.");
      })
      .finally(() => {
        setDungeonsLoading(false);
      });
  }

  return (
    <ProtectedRoute>
      <Box sx={{ minHeight: "100vh", bgcolor: "background.default" }}>
        {/* Page header */}
        <Box
          component="header"
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 1,
            px: { xs: 3, sm: 6 },
            py: 2,
            borderBottom: "1px solid",
            borderColor: "divider",
            bgcolor: "background.paper",
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <Button
              startIcon={<ArrowBackIcon />}
              onClick={() => router.push("/campaign")}
              sx={{ textTransform: "none", color: "text.secondary" }}
            >
              Campaigns
            </Button>
            <Typography variant="h6" fontWeight={700} sx={{ ml: 1 }}>
              Campaign Detail
            </Typography>
          </Box>

          <Box sx={{ display: "flex", gap: 1 }}>
            {/* DM-only: start a new session */}
            {isDm && campaign !== null && (
              <Button
                variant="contained"
                onClick={() => setWizardOpen(true)}
                sx={{
                  textTransform: "none",
                  fontWeight: 600,
                  borderRadius: 2,
                  bgcolor: "#7d5e45",
                  "&:hover": { bgcolor: "#5c4230" },
                }}
              >
                Start Session
              </Button>
            )}

            {/* Player-only: link a character to this campaign */}
            {!isDm && campaign !== null && (
              <Button
                variant="contained"
                onClick={() => setPickerOpen(true)}
                sx={{
                  textTransform: "none",
                  fontWeight: 600,
                  borderRadius: 2,
                  bgcolor: "#a07d60",
                  "&:hover": { bgcolor: "#7d5e45" },
                }}
              >
                Join with Character
              </Button>
            )}
          </Box>
        </Box>

        {/* Content */}
        <Box sx={{ px: { xs: 3, sm: 6 }, py: 4, maxWidth: 900, mx: "auto" }}>
          {isLoading && (
            <Box sx={{ display: "flex", justifyContent: "center", py: 10 }}>
              <CircularProgress />
            </Box>
          )}

          {!isLoading && error !== null && (
            <Alert severity="error">{error}</Alert>
          )}

          {!isLoading && error === null && campaign !== null && (
            <Box sx={{ display: "flex", flexDirection: "column", gap: 4 }}>
              {/* Campaign overview */}
              <Box>
                <Typography variant="h5" fontWeight={700} gutterBottom>
                  {campaign.name}
                </Typography>
                <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, mb: 1 }}>
                  <Chip label={toLabel(campaign.tone)} variant="outlined" size="small" />
                  <Chip label={campaign.edition} variant="outlined" size="small" />
                  <Chip
                    label={`${campaign.player_count} player${campaign.player_count !== 1 ? "s" : ""}`}
                    variant="outlined"
                    size="small"
                  />
                  <Chip
                    label={`Levels ${campaign.level_range.start}–${campaign.level_range.end}`}
                    variant="outlined"
                    size="small"
                  />
                </Box>
                {world !== null && (
                  <Typography variant="body2" color="text.secondary">
                    World:{" "}
                    <Link
                      href={`/campaign/${campaignId}/world`}
                      style={{ color: "#a07d60" }}
                    >
                      {world.name}
                    </Link>
                  </Typography>
                )}
              </Box>

              <Divider />

              {/* Themes */}
              {campaign.themes.length > 0 && (
                <Box>
                  <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                    Themes
                  </Typography>
                  <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
                    {campaign.themes.map((theme) => (
                      <Chip key={theme} label={theme} size="small" variant="outlined" />
                    ))}
                  </Box>
                </Box>
              )}

              {/* Content Boundaries */}
              {campaign.content_boundaries.lines.length > 0 && (
                <>
                  <Divider />
                  <Box>
                    <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                      Content Boundaries
                    </Typography>
                    <Box>
                      <Typography
                        variant="caption"
                        color="text.secondary"
                        fontWeight={600}
                      >
                        Lines (never depicted)
                      </Typography>
                      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, mt: 0.5 }}>
                        {campaign.content_boundaries.lines.map((line) => (
                          <Chip
                            key={line}
                            label={line}
                            size="small"
                            color="error"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    </Box>
                  </Box>
                </>
              )}

              {/* Party Roster — DM sees full roster; player sees their own joined status */}
              <Divider />
              <Box>
                <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                  Party
                </Typography>
                {isDm && (
                  <CampaignPartyRoster
                    key={rosterKey}
                    campaignId={campaignId}
                    token={localStorage.getItem("access_token") ?? ""}
                  />
                )}
                {!isDm && (
                  <Typography variant="body2" color="text.secondary">
                    Use the "Join with Character" button to link one of your characters to this
                    campaign.
                  </Typography>
                )}
              </Box>

              {/* Past Dungeons — loading and errors are isolated to this section (AC3, AC5) */}
              <Divider />
              <Box>
                <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                  Past Dungeons {!dungeonsLoading && `(${dungeons.length})`}
                </Typography>

                {dungeonsLoading && (
                  <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
                    <Skeleton variant="rounded" height={72} />
                    <Skeleton variant="rounded" height={72} />
                    <Skeleton variant="rounded" height={72} />
                  </Box>
                )}

                {!dungeonsLoading && dungeonsError !== null && (
                  <Alert severity="error" sx={{ mt: 1 }}>{dungeonsError}</Alert>
                )}

                {!dungeonsLoading && dungeonsError === null && dungeons.length === 0 && (
                  <Typography variant="body2" color="text.secondary">
                    No dungeons generated yet. Use the Start Session button to create one.
                  </Typography>
                )}

                {!dungeonsLoading && dungeonsError === null && dungeons.length > 0 && (
                  <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
                    {dungeons.map((dungeon) => (
                      <Box
                        key={dungeon.dungeon_id}
                        sx={{
                          p: 2,
                          border: "1px solid",
                          borderColor: "divider",
                          borderRadius: 2,
                          bgcolor: "background.paper",
                          display: "flex",
                          alignItems: "flex-start",
                          justifyContent: "space-between",
                          gap: 2,
                          flexWrap: "wrap",
                        }}
                      >
                        <Box sx={{ flex: 1, minWidth: 0 }}>
                          <Typography variant="subtitle2" fontWeight={600}>
                            {dungeon.name}
                          </Typography>
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{
                              mt: 0.25,
                              overflow: "hidden",
                              textOverflow: "ellipsis",
                              whiteSpace: "nowrap",
                            }}
                          >
                            {dungeon.premise}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {dungeon.room_count} rooms &mdash;{" "}
                            {new Date(dungeon.created_at).toLocaleDateString()}
                          </Typography>
                        </Box>
                        <Box
                          sx={{
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "flex-end",
                            gap: 1,
                            flexShrink: 0,
                          }}
                        >
                          {/* View dungeon detail */}
                          <Button
                            component={Link}
                            href={`/dungeon/${dungeon.dungeon_id}`}
                            size="small"
                            variant="outlined"
                            sx={{ textTransform: "none", borderRadius: 2 }}
                          >
                            View Dungeon
                          </Button>

                          {/* Room status — shown when a room exists for this dungeon */}
                          {dungeon.room !== null ? (
                            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                              <Chip
                                label={dungeon.room.is_active ? "Active" : "Closed"}
                                size="small"
                                sx={{
                                  bgcolor: dungeon.room.is_active ? "#a07d60" : "#C9B59C",
                                  color: dungeon.room.is_active ? "#F9F8F6" : "#3a2820",
                                  fontWeight: 600,
                                  fontSize: "0.7rem",
                                }}
                              />
                              <Button
                                component={Link}
                                href={`/room/${dungeon.room.room_id}`}
                                size="small"
                                variant="outlined"
                                sx={{ textTransform: "none", borderRadius: 2 }}
                              >
                                {dungeon.room.room_name}
                              </Button>
                            </Box>
                          ) : (
                            /* No room yet — link to dungeon detail where one can be created */
                            <Button
                              component={Link}
                              href={`/dungeon/${dungeon.dungeon_id}`}
                              size="small"
                              variant="text"
                              sx={{
                                textTransform: "none",
                                borderRadius: 2,
                                color: "#7d5e45",
                              }}
                            >
                              Create Room
                            </Button>
                          )}
                        </Box>
                      </Box>
                    ))}
                  </Box>
                )}
              </Box>
            </Box>
          )}
        </Box>

        {/* Start Session Wizard — DM only */}
        <StartSessionWizard
          open={wizardOpen}
          campaignId={campaignId}
          onClose={() => {
            setWizardOpen(false);
            handleSessionStarted();
          }}
        />

        {/* Character Picker Modal — player only */}
        <CharacterPickerModal
          open={pickerOpen}
          campaignId={campaignId}
          token={localStorage.getItem("access_token") ?? ""}
          onClose={() => setPickerOpen(false)}
          onLinked={() => {
            setPickerOpen(false);
            // Bump the roster key so DMs see the update if they share the page.
            setRosterKey((k) => k + 1);
          }}
        />
      </Box>
    </ProtectedRoute>
  );
}
