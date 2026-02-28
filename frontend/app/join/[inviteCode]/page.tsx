"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import Alert from "@mui/material/Alert";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import { joinRoom } from "@/domains/room/services/room.service";
import { useRoomStore } from "@/domains/room/store/room.store";

/**
 * Deep-link join page for entering a room directly via invite code in the URL.
 * Automatically attempts to join the room on mount and redirects to /room/{id}.
 * Handles error states (full room, invalid code, already joined) gracefully.
 */
export default function JoinPage(): React.ReactElement {
  const params = useParams<{ inviteCode: string }>();
  const inviteCode = params.inviteCode;
  const router = useRouter();
  const setRoom = useRoomStore((s) => s.setRoom);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function attemptJoin(): Promise<void> {
      const token = localStorage.getItem("access_token");
      if (!token) {
        router.replace("/login");
        return;
      }

      try {
        const { room, room_token } = await joinRoom(inviteCode, token);
        setRoom(room, room_token);
        localStorage.setItem(`room_token_${room.id}`, room_token);
        router.replace(`/room/${room.id}`);
      } catch (err: unknown) {
        const message =
          err instanceof Error ? err.message : "Unknown error";
        if (message.includes("403")) {
          setError("This room is full or you are not authorized to join.");
        } else if (message.includes("404")) {
          setError("The invite code is invalid or has expired.");
        } else {
          setError("Failed to join the room. Please try again.");
        }
      }
    }

    void attemptJoin();
    // Run once on mount — inviteCode is stable from URL params.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [inviteCode]);

  if (error !== null) {
    return (
      <Box
        sx={{
          minHeight: "100vh",
          bgcolor: "background.default",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 3,
          px: 4,
        }}
      >
        <Alert severity="error" sx={{ maxWidth: 420, width: "100%" }}>
          {error}
        </Alert>
        <Typography variant="body2" color="text.secondary">
          Invite code:{" "}
          <Box
            component="span"
            sx={{ fontFamily: "monospace", fontWeight: 700 }}
          >
            {inviteCode}
          </Box>
        </Typography>
        <Button
          component={Link}
          href="/dashboard"
          variant="contained"
          sx={{ textTransform: "none", fontWeight: 600, borderRadius: 2 }}
        >
          Back to Dashboard
        </Button>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        bgcolor: "background.default",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 2,
      }}
    >
      <CircularProgress sx={{ color: "primary.main" }} />
      <Typography variant="body2" color="text.secondary">
        Joining room…
      </Typography>
    </Box>
  );
}
