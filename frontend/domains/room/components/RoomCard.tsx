"use client";

import { useRouter } from "next/navigation";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardActions from "@mui/material/CardActions";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import PeopleIcon from "@mui/icons-material/People";
import type { Room } from "@/domains/room/types";

/** Props for the RoomCard component. */
interface RoomCardProps {
  readonly room: Room;
}

/**
 * Displays a summary card for a game room with name, invite code, player count,
 * and an "Enter Room" button. Used in the DM dashboard for active rooms.
 */
export function RoomCard({ room }: RoomCardProps): React.ReactElement {
  const router = useRouter();

  return (
    <Card
      variant="outlined"
      sx={{
        bgcolor: "background.paper",
        borderColor: "divider",
        borderRadius: 2.5,
        transition: "box-shadow 0.2s",
        "&:hover": { boxShadow: "0 4px 16px rgba(0,0,0,0.1)" },
      }}
    >
      <CardContent sx={{ pb: 1 }}>
        <Typography
          variant="h6"
          fontWeight={700}
          sx={{ color: "text.primary", mb: 1 }}
        >
          {room.name}
        </Typography>

        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, mb: 1 }}>
          <Chip
            label={room.is_active ? "Active" : "Inactive"}
            size="small"
            color={room.is_active ? "success" : "default"}
            variant="outlined"
            sx={{ fontSize: "0.72rem" }}
          />
          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
            <PeopleIcon sx={{ fontSize: "0.95rem", color: "text.disabled" }} />
            <Typography variant="caption" color="text.secondary">
              {room.player_ids.length} / {room.max_players}
            </Typography>
          </Box>
        </Box>

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
      </CardContent>

      <CardActions sx={{ px: 2, pb: 2 }}>
        <Button
          size="small"
          variant="contained"
          onClick={() => router.push(`/room/${room.id}`)}
          sx={{ textTransform: "none", fontWeight: 600, borderRadius: 2 }}
        >
          Enter Room
        </Button>
      </CardActions>
    </Card>
  );
}
