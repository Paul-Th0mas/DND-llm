"use client";

import { useEffect, useState } from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import IconButton from "@mui/material/IconButton";
import CircularProgress from "@mui/material/CircularProgress";
import Alert from "@mui/material/Alert";
import Tooltip from "@mui/material/Tooltip";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import MapIcon from "@mui/icons-material/Map";
import LinkIcon from "@mui/icons-material/Link";
import { getDungeonDetail, listDungeons } from "@/domains/dungeon/services/dungeon.service";
import { useDungeonStore, selectActiveDungeon } from "@/domains/dungeon/store/dungeon.store";
import { GeneratedDungeonView } from "@/domains/dungeon/components/GeneratedDungeonView";
import { getCampaigns } from "@/domains/campaign/services/campaign.service";
import { linkRoomDungeon } from "@/domains/room/services/room.service";
import { useRoomStore } from "@/domains/room/store/room.store";
import type { CampaignSummary } from "@/domains/campaign/types";
import type { DungeonSummary } from "@/domains/dungeon/types";

// Width of the dungeon panel when expanded, in pixels.
const PANEL_WIDTH = 360;

/** Props for the RoomDungeonPanel component. */
export interface RoomDungeonPanelProps {
  /** UUID of the dungeon linked to the current room. Null means no dungeon is set. */
  readonly dungeonId: string | null;
  /** JWT access token for the authenticated user, used to fetch dungeon data. */
  readonly token: string;
  /** UUID of the room. Used by the DM to link a dungeon. */
  readonly roomId: string;
  /** True when the authenticated user is the DM owner of this room. */
  readonly isDm: boolean;
}

/** Step within the link-dungeon dialog flow. */
type DialogStep = "campaign" | "dungeon";

/**
 * Collapsible right-side panel that fetches and renders dungeon detail
 * for a game room that has a linked dungeon session.
 *
 * When no dungeon is linked:
 * - DM users see a "Link Dungeon" button that opens a two-step dialog.
 * - Non-DM users see nothing (returns null).
 *
 * When a dungeon is linked the panel collapses to a narrow toggle strip
 * and expands to show GeneratedDungeonView. Dungeon data is stored in
 * the DungeonStore via setActiveDungeon.
 *
 * @param dungeonId - UUID of the linked dungeon, or null if none.
 * @param token - JWT bearer token for the API request.
 * @param roomId - UUID of the current room.
 * @param isDm - True when the authenticated user is the DM of this room.
 */
export function RoomDungeonPanel({
  dungeonId,
  token,
  roomId,
  isDm,
}: RoomDungeonPanelProps): React.ReactElement | null {
  // Default open on wide viewports; starts closed so the panel does not
  // flash open before data is available.
  const [isOpen, setIsOpen] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Dialog state for the link-dungeon flow.
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogStep, setDialogStep] = useState<DialogStep>("campaign");
  const [dialogLoading, setDialogLoading] = useState(false);
  const [dialogError, setDialogError] = useState<string | null>(null);
  const [campaigns, setCampaigns] = useState<readonly CampaignSummary[]>([]);
  const [selectedCampaignId, setSelectedCampaignId] = useState<string | null>(null);
  const [dungeons, setDungeons] = useState<readonly DungeonSummary[]>([]);

  const setActiveDungeon = useDungeonStore((s) => s.setActiveDungeon);
  const activeDungeon = useDungeonStore(selectActiveDungeon);
  const updateRoom = useRoomStore((s) => s.updateRoom);

  useEffect(() => {
    if (!dungeonId) return;

    setIsLoading(true);
    setFetchError(null);

    getDungeonDetail(dungeonId, token)
      .then((dungeon) => {
        setActiveDungeon(dungeon);
      })
      .catch(() => {
        setFetchError("Failed to load dungeon details. The panel will remain available to retry.");
      })
      .finally(() => {
        setIsLoading(false);
      });
    // Only re-fetch if dungeonId or token changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dungeonId, token]);

  // --- Link Dungeon dialog handlers ---

  /** Opens the dialog and begins loading the campaign list. */
  function handleOpenDialog(): void {
    setDialogOpen(true);
    setDialogStep("campaign");
    setDialogError(null);
    setSelectedCampaignId(null);
    setDungeons([]);
    setDialogLoading(true);

    getCampaigns(token)
      .then((result) => {
        setCampaigns(result);
      })
      .catch(() => {
        setDialogError("Failed to load campaigns. Please try again.");
      })
      .finally(() => {
        setDialogLoading(false);
      });
  }

  /** Resets and closes the dialog. */
  function handleCloseDialog(): void {
    setDialogOpen(false);
    setDialogStep("campaign");
    setDialogError(null);
    setSelectedCampaignId(null);
    setCampaigns([]);
    setDungeons([]);
  }

  /**
   * Handles campaign selection — advances to the dungeon step and fetches
   * the dungeon list for the chosen campaign.
   * @param campaignId - UUID of the campaign the DM selected.
   */
  function handleSelectCampaign(campaignId: string): void {
    setSelectedCampaignId(campaignId);
    setDialogStep("dungeon");
    setDialogError(null);
    setDialogLoading(true);

    listDungeons(campaignId, token)
      .then((result) => {
        setDungeons(result);
      })
      .catch(() => {
        setDialogError("Failed to load dungeons for this campaign. Please try again.");
      })
      .finally(() => {
        setDialogLoading(false);
      });
  }

  /** Returns the dialog to campaign selection step. */
  function handleBackToCampaigns(): void {
    setDialogStep("campaign");
    setDialogError(null);
    setDungeons([]);
    setSelectedCampaignId(null);
  }

  /**
   * Handles dungeon selection — calls the link endpoint and updates the store.
   * @param selectedDungeonId - UUID of the dungeon the DM selected.
   */
  function handleSelectDungeon(selectedDungeonId: string): void {
    if (!selectedCampaignId) return;

    setDialogLoading(true);
    setDialogError(null);

    linkRoomDungeon(roomId, selectedDungeonId, selectedCampaignId, token)
      .then((updatedRoom) => {
        updateRoom(updatedRoom);
        handleCloseDialog();
      })
      .catch(() => {
        setDialogError("Failed to link the dungeon. Please try again.");
        setDialogLoading(false);
      });
  }

  // --- Render: no dungeon linked ---

  if (!dungeonId) {
    // Players do not see anything when no dungeon is linked.
    if (!isDm) return null;

    return (
      <>
        {/* Slim prompt panel for the DM */}
        <Box
          component="aside"
          sx={{
            width: 48,
            flexShrink: 0,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            bgcolor: "#EFE9E3",
            borderLeft: "1px solid #D9CFC7",
            pt: 1.5,
            gap: 1,
          }}
        >
          <Tooltip title="Link a dungeon to this room" placement="left">
            <IconButton
              size="small"
              onClick={handleOpenDialog}
              aria-label="Link a dungeon to this room"
              sx={{ color: "#a07d60" }}
            >
              <LinkIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          {/* Rotated label so the DM understands the icon's purpose */}
          <Typography
            variant="overline"
            sx={{
              fontSize: "0.6rem",
              letterSpacing: "0.12em",
              color: "#C9B59C",
              fontWeight: 600,
              writingMode: "vertical-rl",
              textOrientation: "mixed",
              transform: "rotate(180deg)",
              userSelect: "none",
            }}
          >
            No dungeon
          </Typography>
        </Box>

        {/* Two-step Link Dungeon dialog */}
        <Dialog
          open={dialogOpen}
          onClose={handleCloseDialog}
          maxWidth="xs"
          fullWidth
          PaperProps={{
            sx: {
              bgcolor: "#EFE9E3",
              border: "1px solid #D9CFC7",
            },
          }}
        >
          <DialogTitle
            sx={{
              color: "#1e1410",
              fontWeight: 700,
              borderBottom: "1px solid #D9CFC7",
              display: "flex",
              alignItems: "center",
              gap: 1,
              pb: 1.5,
            }}
          >
            {dialogStep === "dungeon" && (
              <IconButton
                size="small"
                onClick={handleBackToCampaigns}
                aria-label="Back to campaign selection"
                sx={{ color: "#5c4230", mr: 0.5 }}
              >
                <ArrowBackIcon fontSize="small" />
              </IconButton>
            )}
            Link a Dungeon
          </DialogTitle>

          <DialogContent sx={{ pt: 2 }}>
            {dialogError !== null && (
              <Alert
                severity="error"
                sx={{ mb: 2, fontSize: "0.8rem" }}
                onClose={() => setDialogError(null)}
              >
                {dialogError}
              </Alert>
            )}

            {dialogLoading && (
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "center",
                  py: 4,
                }}
              >
                <CircularProgress size={28} sx={{ color: "#a07d60" }} />
              </Box>
            )}

            {/* Step 1: pick campaign */}
            {!dialogLoading && dialogStep === "campaign" && (
              <>
                <Typography
                  variant="body2"
                  sx={{ color: "#5c4230", mb: 1.5, fontStyle: "italic" }}
                >
                  Choose a campaign to browse its dungeons.
                </Typography>

                {campaigns.length === 0 && dialogError === null && (
                  <Typography
                    variant="body2"
                    sx={{ color: "#C9B59C", textAlign: "center", py: 2 }}
                  >
                    No campaigns found.
                  </Typography>
                )}

                <List disablePadding>
                  {campaigns.map((campaign) => (
                    <ListItemButton
                      key={campaign.campaign_id}
                      onClick={() => handleSelectCampaign(campaign.campaign_id)}
                      sx={{
                        borderRadius: 1,
                        mb: 0.5,
                        border: "1px solid #D9CFC7",
                        bgcolor: "#F9F8F6",
                        "&:hover": { bgcolor: "#D9CFC7" },
                      }}
                    >
                      <ListItemText
                        primary={campaign.name}
                        secondary={campaign.world_name ?? "No world linked"}
                        primaryTypographyProps={{
                          fontSize: "0.875rem",
                          fontWeight: 600,
                          color: "#1e1410",
                        }}
                        secondaryTypographyProps={{
                          fontSize: "0.75rem",
                          color: "#C9B59C",
                        }}
                      />
                    </ListItemButton>
                  ))}
                </List>
              </>
            )}

            {/* Step 2: pick dungeon */}
            {!dialogLoading && dialogStep === "dungeon" && (
              <>
                <Typography
                  variant="body2"
                  sx={{ color: "#5c4230", mb: 1.5, fontStyle: "italic" }}
                >
                  Choose a dungeon to link to this room.
                </Typography>

                {dungeons.length === 0 && dialogError === null && (
                  <Typography
                    variant="body2"
                    sx={{ color: "#C9B59C", textAlign: "center", py: 2 }}
                  >
                    No dungeons found for this campaign.
                  </Typography>
                )}

                <List disablePadding>
                  {dungeons.map((dungeon) => (
                    <ListItemButton
                      key={dungeon.dungeon_id}
                      onClick={() => handleSelectDungeon(dungeon.dungeon_id)}
                      sx={{
                        borderRadius: 1,
                        mb: 0.5,
                        border: "1px solid #D9CFC7",
                        bgcolor: "#F9F8F6",
                        "&:hover": { bgcolor: "#D9CFC7" },
                      }}
                    >
                      <ListItemText
                        primary={dungeon.name}
                        secondary={new Date(dungeon.created_at).toLocaleDateString()}
                        primaryTypographyProps={{
                          fontSize: "0.875rem",
                          fontWeight: 600,
                          color: "#1e1410",
                        }}
                        secondaryTypographyProps={{
                          fontSize: "0.75rem",
                          color: "#C9B59C",
                        }}
                      />
                    </ListItemButton>
                  ))}
                </List>
              </>
            )}
          </DialogContent>
        </Dialog>
      </>
    );
  }

  // --- Render: dungeon is linked ---

  return (
    <Box
      component="aside"
      sx={{
        width: isOpen ? PANEL_WIDTH : 48,
        flexShrink: 0,
        display: "flex",
        flexDirection: "column",
        bgcolor: "#EFE9E3",
        borderLeft: "1px solid #D9CFC7",
        overflow: "hidden",
        transition: "width 0.25s ease",
      }}
    >
      {/* Panel header with toggle button */}
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          px: 1,
          py: 1.5,
          borderBottom: "1px solid #D9CFC7",
          minHeight: 52,
          gap: 1,
        }}
      >
        <Tooltip title={isOpen ? "Collapse dungeon panel" : "Expand dungeon panel"}>
          <IconButton
            size="small"
            onClick={() => setIsOpen((prev) => !prev)}
            aria-label={isOpen ? "Collapse dungeon panel" : "Expand dungeon panel"}
            sx={{ color: "#7d5e45", flexShrink: 0 }}
          >
            {isOpen ? (
              <ChevronRightIcon fontSize="small" />
            ) : (
              <ChevronLeftIcon fontSize="small" />
            )}
          </IconButton>
        </Tooltip>

        {isOpen && (
          <>
            <MapIcon sx={{ fontSize: "1rem", color: "#a07d60", flexShrink: 0 }} />
            <Typography
              variant="overline"
              sx={{
                fontSize: "0.65rem",
                letterSpacing: "0.14em",
                color: "#7d5e45",
                fontWeight: 600,
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
              }}
            >
              Dungeon
            </Typography>
          </>
        )}
      </Box>

      {/* Panel body — only rendered when expanded */}
      {isOpen && (
        <Box
          sx={{
            flex: 1,
            overflowY: "auto",
            p: 2,
          }}
        >
          {isLoading && (
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                py: 6,
              }}
            >
              <CircularProgress size={28} sx={{ color: "#a07d60" }} />
            </Box>
          )}

          {fetchError !== null && !isLoading && (
            <Alert
              severity="error"
              sx={{ fontSize: "0.8rem" }}
              onClose={() => setFetchError(null)}
            >
              {fetchError}
            </Alert>
          )}

          {!isLoading && fetchError === null && activeDungeon !== null && (
            <GeneratedDungeonView dungeon={activeDungeon} />
          )}

          {!isLoading && fetchError === null && activeDungeon === null && (
            <Typography
              variant="body2"
              color="text.disabled"
              fontStyle="italic"
              sx={{ textAlign: "center", mt: 4 }}
            >
              No dungeon data available.
            </Typography>
          )}
        </Box>
      )}
    </Box>
  );
}

