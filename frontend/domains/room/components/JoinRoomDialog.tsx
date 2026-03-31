"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { joinRoomById } from "@/domains/room/services/room.service";
import { ApiError } from "@/lib/api/client";

/** Props for the JoinRoomDialog component. */
export interface JoinRoomDialogProps {
  /** UUID of the room to join. */
  readonly roomId: string;
  /** Display name of the room, shown in the dialog title. */
  readonly roomName: string;
  /** True when the room requires a password. */
  readonly hasPassword: boolean;
  /** JWT access token of the authenticated player. */
  readonly token: string;
  /** Called when the dialog should be closed (cancel or ESC). */
  readonly onClose: () => void;
  /**
   * Called when a non-password API error occurs (404, 409, 410).
   * The parent receives the HTTP status so it can display the correct
   * toast message and refresh the lobby table.
   * @param errorStatus - The HTTP status code from the failed request.
   */
  readonly onError: (errorStatus: number) => void;
}

/**
 * Modal dialog that prompts a player for a room password and submits
 * the join request to POST /api/v1/rooms/{roomId}/join.
 *
 * Handles all error cases from US-033:
 *   403 — wrong password: keeps modal open, clears field, shows inline error.
 *   404 / 409 / 410 — room gone/full/closed: calls onError(status) so the
 *                     parent can close the dialog and show the right toast.
 */
export function JoinRoomDialog({
  roomId,
  roomName,
  hasPassword,
  token,
  onClose,
  onError,
}: JoinRoomDialogProps): React.ReactElement {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [fieldError, setFieldError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault();

    // Client-side validation: password is required when the room has one.
    if (hasPassword && password.trim() === "") {
      setFieldError("Password is required.");
      return;
    }

    setIsSubmitting(true);
    setFieldError(null);

    try {
      const result = await joinRoomById(roomId, password, token);
      // Success: close modal and navigate to the room.
      onClose();
      router.push(`/room/${result.room.id}`);
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        if (err.status === 403) {
          // Wrong password: stay open, clear field, show inline error.
          setPassword("");
          setFieldError("Incorrect password.");
        } else {
          // 404 / 409 / 410: delegate to the parent for toast + refresh.
          onError(err.status);
        }
      } else {
        setFieldError("Something went wrong. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Dialog
      open
      onClose={onClose}
      maxWidth="xs"
      fullWidth
      aria-labelledby="join-room-dialog-title"
    >
      <Box component="form" onSubmit={(e) => void handleSubmit(e)}>
        <DialogTitle id="join-room-dialog-title">
          Join &ldquo;{roomName}&rdquo;
        </DialogTitle>

        <DialogContent>
          {hasPassword ? (
            <Box sx={{ display: "flex", flexDirection: "column", gap: 1, pt: 1 }}>
              <TextField
                autoFocus
                label="Room Password"
                type="password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (fieldError !== null) setFieldError(null);
                }}
                error={fieldError !== null}
                helperText={fieldError ?? " "}
                fullWidth
                size="small"
                disabled={isSubmitting}
                inputProps={{ "aria-label": "Room password" }}
              />
            </Box>
          ) : (
            <Typography variant="body2" sx={{ color: "text.secondary", pt: 1 }}>
              Click Join to enter the room.
            </Typography>
          )}
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button
            onClick={onClose}
            disabled={isSubmitting}
            sx={{ textTransform: "none", color: "text.secondary" }}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={isSubmitting}
            sx={{
              textTransform: "none",
              fontWeight: 600,
              bgcolor: "#7d5e45",
              "&:hover": { bgcolor: "#5c4230" },
              minWidth: 90,
            }}
          >
            {isSubmitting ? (
              <CircularProgress size={18} sx={{ color: "#F9F8F6" }} />
            ) : (
              "Join"
            )}
          </Button>
        </DialogActions>
      </Box>
    </Dialog>
  );
}
