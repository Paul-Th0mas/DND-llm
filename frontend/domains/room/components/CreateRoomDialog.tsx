"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import Slider from "@mui/material/Slider";
import Button from "@mui/material/Button";
import Alert from "@mui/material/Alert";
import Typography from "@mui/material/Typography";
import IconButton from "@mui/material/IconButton";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import { createRoom, linkRoomDungeon } from "@/domains/room/services/room.service";
import { useRoomStore } from "@/domains/room/store/room.store";
import { getCampaigns } from "@/domains/campaign/services/campaign.service";
import { listDungeons } from "@/domains/dungeon/services/dungeon.service";
import type { CampaignSummary } from "@/domains/campaign/types";
import type { DungeonSummary } from "@/domains/dungeon/types";

// Default and bounds for the max-players slider.
const DEFAULT_MAX_PLAYERS = 6;
const MIN_PLAYERS = 2;
const MAX_PLAYERS = 10;

/** Props for the CreateRoomDialog. */
export interface CreateRoomDialogProps {
  readonly open: boolean;
  readonly onClose: () => void;
}

/**
 * Modal dialog for Dungeon Masters to create a new game room.
 * Includes an optional inline dungeon picker so the DM can link a dungeon
 * at creation time. On success, shows the invite code with a copy button
 * and an "Enter Room" action.
 */
export function CreateRoomDialog({
  open,
  onClose,
}: CreateRoomDialogProps): React.ReactElement {
  const [name, setName] = useState("");
  const [maxPlayers, setMaxPlayers] = useState(DEFAULT_MAX_PLAYERS);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [inviteCode, setInviteCode] = useState<string | null>(null);
  const [roomId, setRoomId] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  // Dungeon picker state.
  const [campaignList, setCampaignList] = useState<CampaignSummary[]>([]);
  const [dungeonList, setDungeonList] = useState<DungeonSummary[]>([]);
  const [selectedCampaignId, setSelectedCampaignId] = useState<string | null>(null);
  const [selectedCampaignName, setSelectedCampaignName] = useState<string | null>(null);
  const [selectedDungeonId, setSelectedDungeonId] = useState<string | null>(null);
  const [selectedDungeonName, setSelectedDungeonName] = useState<string | null>(null);
  const [dungeonPickerStep, setDungeonPickerStep] = useState<
    "closed" | "campaigns" | "dungeons"
  >("closed");
  const [dungeonPickerLoading, setDungeonPickerLoading] = useState(false);
  const [dungeonPickerError, setDungeonPickerError] = useState<string | null>(null);

  const setRoom = useRoomStore((s) => s.setRoom);
  const router = useRouter();
  const searchParams = useSearchParams();

  // Read dungeon_id from the URL query string once on mount.
  // Stored in state so it survives re-renders without re-reading the URL.
  const [urlDungeonId] = useState<string | null>(
    () => searchParams.get("dungeon_id")
  );

  /**
   * Opens the campaign list step of the dungeon picker.
   * Fetches the DM's campaigns and transitions to the "campaigns" sub-step.
   */
  async function handleOpenDungeonPicker(): Promise<void> {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setDungeonPickerError("You are not authenticated. Please log in again.");
      return;
    }

    setDungeonPickerLoading(true);
    setDungeonPickerError(null);

    try {
      const campaigns = await getCampaigns(token);
      setCampaignList(campaigns);
      setDungeonPickerStep("campaigns");
    } catch {
      setDungeonPickerError("Failed to load campaigns. Please try again.");
    } finally {
      setDungeonPickerLoading(false);
    }
  }

  /**
   * Handles campaign selection — fetches the dungeons for that campaign.
   * @param campaignId - UUID of the selected campaign.
   * @param campaignName - Display name of the selected campaign.
   */
  async function handleSelectCampaign(
    campaignId: string,
    campaignName: string
  ): Promise<void> {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setDungeonPickerError("You are not authenticated. Please log in again.");
      return;
    }

    setDungeonPickerLoading(true);
    setDungeonPickerError(null);
    setSelectedCampaignId(campaignId);
    setSelectedCampaignName(campaignName);

    try {
      const dungeons = await listDungeons(campaignId, token);
      setDungeonList(dungeons);
      setDungeonPickerStep("dungeons");
    } catch {
      setDungeonPickerError("Failed to load dungeons. Please try again.");
      // Stay on campaigns step so user can try another campaign.
      setSelectedCampaignId(null);
      setSelectedCampaignName(null);
    } finally {
      setDungeonPickerLoading(false);
    }
  }

  /**
   * Confirms the selected dungeon and closes the picker sub-steps.
   * @param dungeonId - UUID of the chosen dungeon.
   * @param dungeonName - Display name of the chosen dungeon.
   */
  function handleSelectDungeon(dungeonId: string, dungeonName: string): void {
    setSelectedDungeonId(dungeonId);
    setSelectedDungeonName(dungeonName);
    setDungeonPickerStep("closed");
    setDungeonPickerError(null);
  }

  /** Clears the dungeon selection and resets the picker to its closed state. */
  function handleClearDungeonSelection(): void {
    setSelectedDungeonId(null);
    setSelectedDungeonName(null);
    setSelectedCampaignId(null);
    setSelectedCampaignName(null);
    setCampaignList([]);
    setDungeonList([]);
    setDungeonPickerStep("closed");
    setDungeonPickerError(null);
  }

  /** Returns to the campaign list from the dungeon list sub-step. */
  function handleBackToCampaigns(): void {
    setDungeonPickerStep("campaigns");
    setDungeonList([]);
    setSelectedCampaignId(null);
    setSelectedCampaignName(null);
    setDungeonPickerError(null);
  }

  async function handleCreate(): Promise<void> {
    if (!name.trim()) {
      setError("Please enter a room name.");
      return;
    }

    const token = localStorage.getItem("access_token");
    if (!token) {
      setError("You are not authenticated. Please log in again.");
      return;
    }

    setError(null);
    setIsSubmitting(true);
    try {
      // Create the room without a dungeon_id initially; linking happens after.
      const { room, room_token } = await createRoom(
        name.trim(),
        maxPlayers,
        token,
        urlDungeonId
      );
      setRoom(room, room_token);
      // Persist room token for page reload resilience.
      localStorage.setItem(`room_token_${room.id}`, room_token);
      setRoomId(room.id);

      // If a dungeon was picked via the picker, link it now.
      if (selectedDungeonId !== null && selectedCampaignId !== null) {
        const updatedRoom = await linkRoomDungeon(
          room.id,
          selectedDungeonId,
          selectedCampaignId,
          token
        );
        setRoom(updatedRoom, room_token);
      }

      setInviteCode(room.invite_code);
    } catch {
      setError("Failed to create the room. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleCopy(): Promise<void> {
    if (!inviteCode) return;
    await navigator.clipboard.writeText(inviteCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function handleEnterRoom(): void {
    if (roomId) {
      router.push(`/room/${roomId}`);
    }
    handleClose();
  }

  function handleClose(): void {
    // Reset all state when the dialog closes.
    setName("");
    setMaxPlayers(DEFAULT_MAX_PLAYERS);
    setError(null);
    setInviteCode(null);
    setRoomId(null);
    setCopied(false);

    // Reset dungeon picker state.
    setCampaignList([]);
    setDungeonList([]);
    setSelectedCampaignId(null);
    setSelectedCampaignName(null);
    setSelectedDungeonId(null);
    setSelectedDungeonName(null);
    setDungeonPickerStep("closed");
    setDungeonPickerLoading(false);
    setDungeonPickerError(null);

    onClose();
  }

  /**
   * Renders the inline dungeon picker section below the slider.
   * Conditionally shows: the open button, campaign list, dungeon list,
   * or the selected dungeon chip depending on current picker step.
   */
  function renderDungeonPicker(): React.ReactElement {
    // A dungeon has been confirmed — show the chip with a clear button.
    if (selectedDungeonName !== null && dungeonPickerStep === "closed") {
      return (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 0.5 }}>
          <Typography variant="caption" color="text.secondary">
            Linked Dungeon
          </Typography>
          <Chip
            label={selectedDungeonName}
            onDelete={handleClearDungeonSelection}
            size="small"
            sx={{
              alignSelf: "flex-start",
              bgcolor: "primary.main",
              color: "primary.contrastText",
              "& .MuiChip-deleteIcon": { color: "primary.contrastText" },
            }}
          />
        </Box>
      );
    }

    // Picker is closed and nothing is selected — show the trigger button.
    if (dungeonPickerStep === "closed") {
      return (
        <Box>
          <Button
            variant="outlined"
            size="small"
            onClick={() => { void handleOpenDungeonPicker(); }}
            disabled={dungeonPickerLoading}
            sx={{ textTransform: "none", borderRadius: 2 }}
          >
            {dungeonPickerLoading ? (
              <CircularProgress size={14} sx={{ mr: 1 }} />
            ) : null}
            Select Dungeon (optional)
          </Button>
          {dungeonPickerError !== null && (
            <Typography variant="caption" color="error" sx={{ display: "block", mt: 0.5 }}>
              {dungeonPickerError}
            </Typography>
          )}
        </Box>
      );
    }

    // Campaign list step.
    if (dungeonPickerStep === "campaigns") {
      return (
        <Box
          sx={{
            border: "1px solid",
            borderColor: "divider",
            borderRadius: 2,
            overflow: "hidden",
          }}
        >
          <Box
            sx={{
              px: 1.5,
              py: 1,
              bgcolor: "background.default",
              borderBottom: "1px solid",
              borderColor: "divider",
            }}
          >
            <Typography variant="caption" color="text.secondary">
              Select a campaign
            </Typography>
          </Box>
          {dungeonPickerError !== null && (
            <Alert
              severity="error"
              sx={{ borderRadius: 0, fontSize: "0.75rem" }}
            >
              {dungeonPickerError}
            </Alert>
          )}
          {dungeonPickerLoading ? (
            <Box sx={{ display: "flex", justifyContent: "center", p: 2 }}>
              <CircularProgress size={20} />
            </Box>
          ) : campaignList.length === 0 ? (
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ p: 1.5 }}
            >
              No campaigns found. Create a campaign first.
            </Typography>
          ) : (
            <List dense disablePadding>
              {campaignList.map((campaign) => (
                <ListItemButton
                  key={campaign.campaign_id}
                  onClick={() => {
                    void handleSelectCampaign(campaign.campaign_id, campaign.name);
                  }}
                  sx={{ borderBottom: "1px solid", borderColor: "divider" }}
                >
                  <ListItemText
                    primary={campaign.name}
                    secondary={`${campaign.dungeon_count} dungeon${campaign.dungeon_count === 1 ? "" : "s"}`}
                    primaryTypographyProps={{ variant: "body2", fontWeight: 500 }}
                    secondaryTypographyProps={{ variant: "caption" }}
                  />
                </ListItemButton>
              ))}
            </List>
          )}
        </Box>
      );
    }

    // Dungeon list step.
    return (
      <Box
        sx={{
          border: "1px solid",
          borderColor: "divider",
          borderRadius: 2,
          overflow: "hidden",
        }}
      >
        <Box
          sx={{
            px: 1.5,
            py: 1,
            bgcolor: "background.default",
            borderBottom: "1px solid",
            borderColor: "divider",
            display: "flex",
            alignItems: "center",
            gap: 1,
          }}
        >
          <Button
            size="small"
            onClick={handleBackToCampaigns}
            sx={{ textTransform: "none", p: 0, minWidth: "auto", fontSize: "0.75rem" }}
          >
            Back
          </Button>
          <Typography variant="caption" color="text.secondary">
            {selectedCampaignName ?? "Select a dungeon"}
          </Typography>
        </Box>
        {dungeonPickerError !== null && (
          <Alert
            severity="error"
            sx={{ borderRadius: 0, fontSize: "0.75rem" }}
          >
            {dungeonPickerError}
          </Alert>
        )}
        {dungeonPickerLoading ? (
          <Box sx={{ display: "flex", justifyContent: "center", p: 2 }}>
            <CircularProgress size={20} />
          </Box>
        ) : dungeonList.length === 0 ? (
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ p: 1.5 }}
          >
            No dungeons found for this campaign. Generate a dungeon first.
          </Typography>
        ) : (
          <List dense disablePadding>
            {dungeonList.map((dungeon) => (
              <ListItemButton
                key={dungeon.dungeon_id}
                onClick={() => handleSelectDungeon(dungeon.dungeon_id, dungeon.name)}
                sx={{ borderBottom: "1px solid", borderColor: "divider" }}
              >
                <ListItemText
                  primary={dungeon.name}
                  secondary={new Date(dungeon.created_at).toLocaleDateString()}
                  primaryTypographyProps={{ variant: "body2", fontWeight: 500 }}
                  secondaryTypographyProps={{ variant: "caption" }}
                />
              </ListItemButton>
            ))}
          </List>
        )}
      </Box>
    );
  }

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="xs" fullWidth>
      <DialogTitle sx={{ fontWeight: 700, pb: 1 }}>
        {inviteCode ? "Room Created!" : "Create a Room"}
      </DialogTitle>

      <DialogContent>
        {inviteCode ? (
          // Success state — show invite code
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Share this code with your players so they can join.
            </Typography>
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                gap: 1,
                p: 1.5,
                bgcolor: "background.default",
                border: "1px solid",
                borderColor: "divider",
                borderRadius: 2,
              }}
            >
              <Typography
                sx={{
                  flex: 1,
                  fontFamily: "monospace",
                  fontSize: "1.2rem",
                  fontWeight: 700,
                  letterSpacing: "0.12em",
                  color: "primary.main",
                }}
              >
                {inviteCode}
              </Typography>
              <IconButton
                size="small"
                onClick={handleCopy}
                aria-label="Copy invite code"
              >
                <ContentCopyIcon fontSize="small" />
              </IconButton>
            </Box>
            {copied && (
              <Typography variant="caption" color="success.main">
                Copied to clipboard!
              </Typography>
            )}
          </Box>
        ) : (
          // Creation form
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2.5, pt: 1 }}>
            {error !== null && (
              <Alert severity="error" onClose={() => setError(null)} sx={{ fontSize: "0.8rem" }}>
                {error}
              </Alert>
            )}

            <TextField
              label="Room Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              fullWidth
              size="small"
              autoFocus
              sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2 } }}
            />

            <Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Max Players: {maxPlayers}
              </Typography>
              <Slider
                value={maxPlayers}
                onChange={(_, val) => setMaxPlayers(val as number)}
                min={MIN_PLAYERS}
                max={MAX_PLAYERS}
                step={1}
                marks
                valueLabelDisplay="auto"
                sx={{ color: "primary.main" }}
              />
            </Box>

            {renderDungeonPicker()}
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2.5, gap: 1 }}>
        <Button
          onClick={handleClose}
          sx={{ textTransform: "none", color: "text.secondary" }}
        >
          {inviteCode ? "Close" : "Cancel"}
        </Button>
        {inviteCode ? (
          <Button
            variant="contained"
            onClick={handleEnterRoom}
            sx={{ textTransform: "none", fontWeight: 600, borderRadius: 2 }}
          >
            Enter Room
          </Button>
        ) : (
          <Button
            variant="contained"
            onClick={() => { void handleCreate(); }}
            disabled={isSubmitting}
            sx={{ textTransform: "none", fontWeight: 600, borderRadius: 2 }}
          >
            {isSubmitting ? "Creating..." : "Create"}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
}
