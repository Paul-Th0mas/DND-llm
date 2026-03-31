"use client";

import { useCallback, useEffect, useState } from "react";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Skeleton from "@mui/material/Skeleton";
import Snackbar from "@mui/material/Snackbar";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";
import LockIcon from "@mui/icons-material/Lock";
import { listLobbies } from "@/domains/room/services/room.service";
import { JoinRoomDialog } from "./JoinRoomDialog";
import type { LobbyRoom } from "@/domains/room/types";

/** Props for the LobbyTable component. */
export interface LobbyTableProps {
  /** JWT access token of the authenticated user. */
  readonly token: string;
}

// Human-readable labels for each room status value.
const STATUS_LABELS: Readonly<Record<string, string>> = {
  open: "Open",
  in_progress: "In Progress",
  closed: "Closed",
} as const;

// Toast messages keyed by HTTP status code returned from the join endpoint.
const JOIN_ERROR_MESSAGES: Readonly<Record<number, string>> = {
  404: "This room no longer exists.",
  409: "This room is now full.",
  410: "This room is no longer accepting players.",
} as const;

/**
 * Displays a table of open game lobbies fetched from GET /api/v1/rooms.
 * Players click "Join" on a row to open the JoinRoomDialog.
 *
 * Implements US-032 acceptance criteria:
 *   - Fetches GET /api/v1/rooms?status=open on mount, sorted newest first.
 *   - Loading skeleton while fetching.
 *   - Empty state when no open lobbies exist.
 *   - Error banner with retry on API failure.
 *   - Toast notifications for 404 / 409 / 410 outcomes from JoinRoomDialog.
 */
export function LobbyTable({ token }: LobbyTableProps): React.ReactElement {
  const [rooms, setRooms] = useState<readonly LobbyRoom[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // The room currently being joined — controls whether JoinRoomDialog is shown.
  const [joiningRoom, setJoiningRoom] = useState<LobbyRoom | null>(null);
  // Toast message for 404 / 409 / 410 outcomes.
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const fetchLobbies = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await listLobbies(token);
      setRooms(data);
    } catch {
      setError("Could not load lobbies. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    void fetchLobbies();
  }, [fetchLobbies]);

  /**
   * Handles non-password join errors (404/409/410) from JoinRoomDialog.
   * Closes the dialog, shows the appropriate toast, and refreshes the list.
   * @param errorStatus - The HTTP status code that caused the failure.
   */
  function handleJoinError(errorStatus: number): void {
    setJoiningRoom(null);
    const message =
      JOIN_ERROR_MESSAGES[errorStatus] ??
      "This room is no longer accepting players.";
    setToastMessage(message);
    void fetchLobbies();
  }

  return (
    <Box>
      {/* Error banner with retry button */}
      {!isLoading && error !== null && (
        <Box sx={{ mb: 2, display: "flex", flexDirection: "column", gap: 1 }}>
          <Alert severity="error">{error}</Alert>
          <Button
            size="small"
            variant="outlined"
            onClick={() => void fetchLobbies()}
            sx={{
              alignSelf: "flex-start",
              textTransform: "none",
              borderColor: "#a07d60",
              color: "#a07d60",
            }}
          >
            Retry
          </Button>
        </Box>
      )}

      {/* Loading skeleton — mirrors the table row structure */}
      {isLoading && (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton
              key={i}
              variant="rectangular"
              height={52}
              sx={{ borderRadius: 1 }}
            />
          ))}
        </Box>
      )}

      {/* Empty state */}
      {!isLoading && error === null && rooms.length === 0 && (
        <Typography
          variant="body2"
          sx={{ color: "#C9B59C", py: 4, textAlign: "center" }}
        >
          No open lobbies at the moment. Check back soon.
        </Typography>
      )}

      {/* Lobby table */}
      {!isLoading && error === null && rooms.length > 0 && (
        <TableContainer
          sx={{
            border: "1px solid",
            borderColor: "#D9CFC7",
            borderRadius: 2,
            bgcolor: "#EFE9E3",
          }}
        >
          <Table size="small" aria-label="Open lobbies">
            <TableHead>
              <TableRow sx={{ bgcolor: "#D9CFC7" }}>
                <TableCell sx={{ fontWeight: 700, color: "#1e1410" }}>
                  Room Name
                </TableCell>
                <TableCell
                  sx={{ fontWeight: 700, color: "#1e1410" }}
                  align="center"
                >
                  Players
                </TableCell>
                <TableCell
                  sx={{ fontWeight: 700, color: "#1e1410" }}
                  align="center"
                >
                  Status
                </TableCell>
                <TableCell
                  sx={{ fontWeight: 700, color: "#1e1410" }}
                  align="center"
                >
                  Password
                </TableCell>
                <TableCell
                  sx={{ fontWeight: 700, color: "#1e1410" }}
                  align="right"
                />
              </TableRow>
            </TableHead>
            <TableBody>
              {rooms.map((room) => (
                <TableRow
                  key={room.id}
                  sx={{
                    "&:last-child td": { border: 0 },
                    "&:hover": { bgcolor: "#D9CFC7" },
                  }}
                >
                  <TableCell sx={{ color: "#1e1410", fontWeight: 500 }}>
                    {room.name}
                  </TableCell>
                  <TableCell align="center" sx={{ color: "#5c4230" }}>
                    {room.player_count}/{room.max_players}
                  </TableCell>
                  <TableCell align="center">
                    <Chip
                      label={STATUS_LABELS[room.status] ?? room.status}
                      size="small"
                      sx={{
                        bgcolor: room.status === "open" ? "#a07d60" : "#C9B59C",
                        color:
                          room.status === "open" ? "#F9F8F6" : "#3a2820",
                        fontWeight: 600,
                        fontSize: "0.7rem",
                      }}
                    />
                  </TableCell>
                  <TableCell align="center">
                    {room.has_password && (
                      <LockIcon sx={{ fontSize: 16, color: "#7d5e45" }} />
                    )}
                  </TableCell>
                  <TableCell align="right">
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => setJoiningRoom(room)}
                      sx={{
                        textTransform: "none",
                        borderRadius: 2,
                        borderColor: "#7d5e45",
                        color: "#7d5e45",
                        "&:hover": { borderColor: "#5c4230", color: "#5c4230" },
                      }}
                    >
                      Join
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Password dialog — shown when a row's Join button is clicked */}
      {joiningRoom !== null && (
        <JoinRoomDialog
          roomId={joiningRoom.id}
          roomName={joiningRoom.name}
          hasPassword={joiningRoom.has_password}
          token={token}
          onClose={() => setJoiningRoom(null)}
          onError={handleJoinError}
        />
      )}

      {/* Toast for 404 / 409 / 410 join outcomes */}
      <Snackbar
        open={toastMessage !== null}
        autoHideDuration={4000}
        onClose={() => setToastMessage(null)}
        message={toastMessage}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      />
    </Box>
  );
}
