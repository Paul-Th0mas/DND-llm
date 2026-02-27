"use client";

import { useState } from "react";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Chip from "@mui/material/Chip";
import IconButton from "@mui/material/IconButton";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import Tooltip from "@mui/material/Tooltip";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import LogoutIcon from "@mui/icons-material/Logout";
import FiberManualRecordIcon from "@mui/icons-material/FiberManualRecord";
import { useRoomStore, selectRoom, selectIsConnected } from "@/domains/room/store/room.store";
import { useAuthStore, selectUser } from "@/shared/store/auth.store";

/** Props for the RoomTopBar component. */
interface RoomTopBarProps {
  /** Called when the user clicks the Leave Room button. */
  readonly onLeave: () => void;
}

/**
 * Top application bar displayed inside the game room.
 * Shows the room name, connection status chip, invite code copy (DM only),
 * and a leave room button.
 */
export function RoomTopBar({ onLeave }: RoomTopBarProps): React.ReactElement {
  const room = useRoomStore(selectRoom);
  const isConnected = useRoomStore(selectIsConnected);
  const user = useAuthStore(selectUser);
  const [copied, setCopied] = useState(false);

  const isDm = user?.role === "dm";

  async function handleCopyInvite(): Promise<void> {
    if (!room) return;
    await navigator.clipboard.writeText(room.invite_code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
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
  );
}
