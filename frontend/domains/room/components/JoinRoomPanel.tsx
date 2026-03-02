"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Alert from "@mui/material/Alert";
import LoginIcon from "@mui/icons-material/Login";
import { joinRoom } from "@/domains/room/services/room.service";
import { useRoomStore } from "@/domains/room/store/room.store";

/**
 * Form panel allowing a Player to join an existing game room using an invite code.
 * On success, stores the room token and navigates to the room page.
 */
export function JoinRoomPanel(): React.ReactElement {
  const [inviteCode, setInviteCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const setRoom = useRoomStore((s) => s.setRoom);
  const router = useRouter();

  async function handleSubmit(
    e: React.FormEvent<HTMLFormElement>
  ): Promise<void> {
    e.preventDefault();
    setError(null);

    const code = inviteCode.trim();
    if (!code) {
      setError("Please enter an invite code.");
      return;
    }

    const token = localStorage.getItem("access_token");
    if (!token) {
      setError("You are not authenticated. Please log in again.");
      return;
    }

    setIsSubmitting(true);
    try {
      const { room, room_token } = await joinRoom(code, token);
      setRoom(room, room_token);
      localStorage.setItem(`room_token_${room.id}`, room_token);
      router.push(`/room/${room.id}`);
    } catch {
      setError("Could not join the room. Check the code and try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      noValidate
      sx={{ display: "flex", flexDirection: "column", gap: 2 }}
    >
      {error !== null && (
        <Alert
          severity="error"
          onClose={() => setError(null)}
          sx={{ fontSize: "0.8rem" }}
        >
          {error}
        </Alert>
      )}

      <TextField
        label="Invite Code"
        value={inviteCode}
        onChange={(e) => setInviteCode(e.target.value)}
        fullWidth
        autoComplete="off"
        size="small"
        placeholder="e.g. ABC-123"
        sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2 } }}
      />

      <Button
        type="submit"
        variant="contained"
        fullWidth
        disabled={isSubmitting}
        startIcon={<LoginIcon />}
        sx={{
          textTransform: "none",
          fontWeight: 600,
          fontSize: "0.95rem",
          borderRadius: 2,
          py: 1.25,
        }}
      >
        {isSubmitting ? "Joining…" : "Join Room"}
      </Button>
    </Box>
  );
}
