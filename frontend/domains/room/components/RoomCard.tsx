"use client";

import { useRouter } from "next/navigation";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Typography from "@mui/material/Typography";
import PeopleIcon from "@mui/icons-material/People";
import { AppCard } from "@/shared/components/AppCard";
import type { Room } from "@/domains/room/types";

/** Props for the RoomCard component. */
interface RoomCardProps {
  readonly room: Room;
}

/**
 * Displays a summary card for a game room with name, status chip, invite code,
 * player count, and an "Enter Room" button. Uses AppCard for consistent theming.
 * Used in the DM dashboard for active rooms.
 */
export function RoomCard({ room }: RoomCardProps): React.ReactElement {
  const router = useRouter();

  return (
    <AppCard
      title={room.name}
      chips={[
        <Chip
          key="status"
          label={room.is_active ? "Active" : "Inactive"}
          size="small"
          color={room.is_active ? "success" : "default"}
          variant="outlined"
          sx={{ fontSize: "0.72rem" }}
        />,
      ]}
      actions={
        <Button
          size="small"
          variant="contained"
          onClick={() => router.push(`/room/${room.id}`)}
          sx={{ textTransform: "none", fontWeight: 600, borderRadius: 2 }}
        >
          Enter Room
        </Button>
      }
    >
      {/* Player count */}
      <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
        <PeopleIcon sx={{ fontSize: "0.95rem", color: "text.disabled" }} />
        <Typography variant="caption" color="text.secondary">
          {room.player_ids.length} / {room.max_players}
        </Typography>
      </Box>

      {/* Invite code */}
      <Typography variant="caption" color="text.disabled">
        Code:{" "}
        <Box
          component="span"
          sx={{
            fontFamily: "monospace",
            fontWeight: 700,
            letterSpacing: "0.08em",
            color: "primary.main",
          }}
        >
          {room.invite_code}
        </Box>
      </Typography>
    </AppCard>
  );
}
