"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
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
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import { createRoom } from "@/domains/room/services/room.service";
import { useRoomStore } from "@/domains/room/store/room.store";

// Default and bounds for the max-players slider.
const DEFAULT_MAX_PLAYERS = 6;
const MIN_PLAYERS = 2;
const MAX_PLAYERS = 10;

/** Props for the CreateRoomDialog. */
interface CreateRoomDialogProps {
  readonly open: boolean;
  readonly onClose: () => void;
}

/**
 * Modal dialog for Dungeon Masters to create a new game room.
 * On success, shows the invite code with a copy button and an "Enter Room" action.
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

  const setRoom = useRoomStore((s) => s.setRoom);
  const router = useRouter();

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
      const { room, room_token } = await createRoom(name.trim(), maxPlayers, token);
      setRoom(room, room_token);
      // Persist room token for page reload resilience.
      localStorage.setItem(`room_token_${room.id}`, room_token);
      setRoomId(room.id);
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
    // Reset state when the dialog closes.
    setName("");
    setMaxPlayers(DEFAULT_MAX_PLAYERS);
    setError(null);
    setInviteCode(null);
    setRoomId(null);
    setCopied(false);
    onClose();
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
            onClick={handleCreate}
            disabled={isSubmitting}
            sx={{ textTransform: "none", fontWeight: 600, borderRadius: 2 }}
          >
            {isSubmitting ? "Creating…" : "Create"}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
}
