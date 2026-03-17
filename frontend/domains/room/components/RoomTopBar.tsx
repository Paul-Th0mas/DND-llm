"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Chip from "@mui/material/Chip";
import IconButton from "@mui/material/IconButton";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import Tooltip from "@mui/material/Tooltip";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Alert from "@mui/material/Alert";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import LogoutIcon from "@mui/icons-material/Logout";
import FiberManualRecordIcon from "@mui/icons-material/FiberManualRecord";
import StopCircleIcon from "@mui/icons-material/StopCircle";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import { useRoomStore, selectRoom, selectIsConnected } from "@/domains/room/store/room.store";
import { useAuthStore, selectUser } from "@/shared/store/auth.store";
import { deleteRoom } from "@/domains/room/services/room.service";

/** Props for the RoomTopBar component. */
export interface RoomTopBarProps {
  /** Called when the user clicks the Leave Room button. */
  readonly onLeave: () => void;
  /**
   * Sends a typed message over the active WebSocket connection.
   * Used by the Start Session button to dispatch { type: "start_session" }.
   */
  readonly send: (message: Record<string, unknown>) => void;
}

/**
 * Top application bar displayed inside the game room.
 * Shows the room name, connection status chip, invite code copy (DM only),
 * a leave room button, and — for the owning DM — a Start Session button
 * (visible only when a dungeon is linked) and an End Session button that
 * calls DELETE /api/v1/rooms/{roomId} after confirmation.
 */
export function RoomTopBar({ onLeave, send }: RoomTopBarProps): React.ReactElement {
  const room = useRoomStore(selectRoom);
  const isConnected = useRoomStore(selectIsConnected);
  const clearRoom = useRoomStore((s) => s.clearRoom);
  const user = useAuthStore(selectUser);
  const token = useAuthStore((s) => s.token);
  const router = useRouter();

  const [copied, setCopied] = useState(false);

  // End Session dialog state.
  const [endDialogOpen, setEndDialogOpen] = useState(false);
  const [isEnding, setIsEnding] = useState(false);
  const [endError, setEndError] = useState<string | null>(null);

  // True when the current user has the dm role (for invite code copy).
  const isDm = user?.role === "dm";

  // Show the End Session button only for the DM who owns this room.
  const isOwningDm =
    user?.role === "dm" && room !== null && user.id === room.dm_id;

  async function handleCopyInvite(): Promise<void> {
    if (!room) return;
    await navigator.clipboard.writeText(room.invite_code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  /** Opens the End Session confirmation dialog. */
  function handleOpenEndDialog(): void {
    setEndError(null);
    setEndDialogOpen(true);
  }

  /** Closes the End Session dialog and resets its internal state. */
  function handleCloseEndDialog(): void {
    if (isEnding) return;
    setEndDialogOpen(false);
    setEndError(null);
  }

  /**
   * Confirms the End Session action.
   * Calls DELETE /api/v1/rooms/{roomId}, clears room store, and navigates away.
   * On failure, shows an inline error inside the dialog without closing it.
   */
  async function handleConfirmEnd(): Promise<void> {
    if (!room) return;

    const authToken = token ?? localStorage.getItem("access_token");
    if (!authToken) {
      setEndError("Authentication token not found. Please log in again.");
      return;
    }

    setIsEnding(true);
    setEndError(null);

    try {
      await deleteRoom(room.id, authToken);
      // Clear room state and navigate to the campaign list.
      clearRoom();
      router.push("/campaign");
    } catch {
      setEndError("Failed to close the room. Please try again.");
    } finally {
      setIsEnding(false);
    }
  }

  return (
    <>
    <AppBar
      position="static"
      elevation={0}
      sx={{
        bgcolor: "#1e1410",
        borderBottom: "1px solid rgba(255,255,255,0.08)",
      }}
    >
      <Toolbar sx={{ gap: 2, minHeight: 56 }}>
        {/* Room name */}
        <Typography
          variant="h6"
          fontWeight={700}
          sx={{ color: "#F9F8F6", letterSpacing: "-0.01em", mr: 1 }}
        >
          {room?.name ?? "Room"}
        </Typography>

        {/* Connection status */}
        <Chip
          icon={
            <FiberManualRecordIcon
              sx={{
                fontSize: "0.6rem !important",
                color: isConnected ? "#4caf50 !important" : "#f44336 !important",
              }}
            />
          }
          label={isConnected ? "Connected" : "Reconnecting…"}
          size="small"
          variant="outlined"
          sx={{
            color: isConnected ? "#4caf50" : "#f44336",
            borderColor: isConnected ? "#4caf50" : "#f44336",
            fontSize: "0.72rem",
          }}
        />

        <Box sx={{ flex: 1 }} />

        {/* DM-only invite code copy */}
        {isDm && room && (
          <Tooltip title={copied ? "Copied!" : `Code: ${room.invite_code}`}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
              <Typography
                sx={{
                  fontFamily: "monospace",
                  fontSize: "0.85rem",
                  fontWeight: 700,
                  letterSpacing: "0.1em",
                  color: "#a07d60",
                }}
              >
                {room.invite_code}
              </Typography>
              <IconButton
                size="small"
                onClick={handleCopyInvite}
                aria-label="Copy invite code"
                sx={{ color: "#a07d60" }}
              >
                <ContentCopyIcon fontSize="small" />
              </IconButton>
            </Box>
          </Tooltip>
        )}

        {/* Current user name */}
        {user && (
          <Typography
            variant="body2"
            sx={{
              color: "#C9B59C",
              fontSize: "0.8rem",
              maxWidth: 160,
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {user.name}
          </Typography>
        )}

        {/* DM-only Start Session button */}
        {isOwningDm && (
          <Button
            size="small"
            variant="contained"
            startIcon={<PlayArrowIcon fontSize="small" />}
            onClick={() => send({ type: "start_session" })}
            sx={{
              textTransform: "none",
              fontWeight: 600,
              bgcolor: "#5c4230",
              color: "#F9F8F6",
              "&:hover": { bgcolor: "#7d5e45" },
            }}
          >
            Start Session
          </Button>
        )}

        {/* DM-only End Session button */}
        {isOwningDm && (
          <Button
            size="small"
            variant="outlined"
            color="error"
            startIcon={<StopCircleIcon fontSize="small" />}
            onClick={handleOpenEndDialog}
            sx={{
              textTransform: "none",
              borderColor: "rgba(211,47,47,0.4)",
              color: "#ef9a9a",
              "&:hover": {
                borderColor: "#ef5350",
                bgcolor: "rgba(211,47,47,0.08)",
              },
            }}
          >
            End Session
          </Button>
        )}

        {/* Leave button */}
        <Button
          size="small"
          variant="outlined"
          startIcon={<LogoutIcon fontSize="small" />}
          onClick={onLeave}
          sx={{
            textTransform: "none",
            color: "#C9B59C",
            borderColor: "rgba(201,181,156,0.3)",
            "&:hover": {
              borderColor: "#C9B59C",
              bgcolor: "rgba(201,181,156,0.08)",
            },
          }}
        >
          Leave
        </Button>
      </Toolbar>
    </AppBar>

    {/* End Session confirmation dialog */}
    <Dialog
      open={endDialogOpen}
      onClose={handleCloseEndDialog}
      maxWidth="xs"
      fullWidth
    >
      <DialogTitle sx={{ fontWeight: 700 }}>End Session</DialogTitle>
      <DialogContent>
        <Typography variant="body2" sx={{ mb: endError !== null ? 2 : 0 }}>
          Are you sure you want to close this room? All players will be
          disconnected.
        </Typography>
        {endError !== null && (
          <Alert severity="error" sx={{ fontSize: "0.8rem" }}>
            {endError}
          </Alert>
        )}
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2.5, gap: 1 }}>
        <Button
          onClick={handleCloseEndDialog}
          disabled={isEnding}
          sx={{ textTransform: "none", color: "text.secondary" }}
        >
          Cancel
        </Button>
        <Button
          variant="contained"
          color="error"
          onClick={handleConfirmEnd}
          disabled={isEnding}
          sx={{ textTransform: "none", fontWeight: 600, borderRadius: 2 }}
        >
          {isEnding ? "Closing…" : "Confirm"}
        </Button>
      </DialogActions>
    </Dialog>
    </>
  );
}
