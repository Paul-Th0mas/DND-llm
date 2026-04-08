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
import LockOpenIcon from "@mui/icons-material/LockOpen";
import { listLobbies } from "@/domains/room/services/room.service";
import { JoinRoomDialog } from "./JoinRoomDialog";
import type { LobbyRoom } from "@/domains/room/types";

/** Props for the LobbyTable component. */
export interface LobbyTableProps {
  /** JWT access token of the authenticated user. */
  readonly token: string;
}

// Toast messages keyed by HTTP status code returned from the join endpoint.
const JOIN_ERROR_MESSAGES: Readonly<Record<number, string>> = {
  404: "This room no longer exists.",
  409: "This room is now full.",
  410: "This room is no longer accepting players.",
} as const;

// Status badge config — maps backend status values to display labels and colors.
const STATUS_CONFIG: Readonly<
  Record<string, { label: string; bg: string; color: string }>
> = {
  open: { label: "In Lobby", bg: "#fbd495", color: "#624816" },
  in_progress: { label: "In Combat", bg: "#fedcbe", color: "#654d37" },
  closed: { label: "Closed", bg: "#bfb193", color: "#3a311b" },
} as const;

/**
 * Determines whether a room is full based on player count.
 * Full rooms get a special "Full" badge and a disabled Join button.
 * @param room - The lobby room to check.
 * @returns True if the room has no available player slots.
 */
function isRoomFull(room: LobbyRoom): boolean {
  return room.player_count >= room.max_players;
}

/**
 * Displays the open game lobbies table styled as a Modern Scriptorium registry.
 * Fetches GET /api/v1/rooms?status=open on mount, sorted newest first.
 *
 * Visual design:
 *   - surface-container-low container, no border lines.
 *   - Table header in surface-container-high with uppercase tracking-widest labels.
 *   - Alternating row tints; hover lifts row to surface-container-highest.
 *   - Status badges: "In Lobby" (amber), "In Combat" (parchment), "Full" (muted).
 *   - Lock icon in primary for password rooms; open-lock in outline-variant otherwise.
 *   - Join button: gradient from primary to primary-dim. Disabled when room is full.
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
        <Box sx={{ mb: 3, display: "flex", flexDirection: "column", gap: 1.5 }}>
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

      {/* Loading skeleton — mirrors table row height */}
      {isLoading && (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton
              key={i}
              variant="rectangular"
              height={60}
              sx={{ borderRadius: "0.5rem", bgcolor: "#fdf2df" }}
            />
          ))}
        </Box>
      )}

      {/* Empty state */}
      {!isLoading && error === null && rooms.length === 0 && (
        <Typography
          sx={{
            fontFamily: "var(--font-work-sans), sans-serif",
            color: "#695e45",
            py: 6,
            textAlign: "center",
            fontSize: "0.875rem",
          }}
        >
          No open lobbies at the moment. Check back soon.
        </Typography>
      )}

      {/* Lobby table — surface-container-low container, no border lines */}
      {!isLoading && error === null && rooms.length > 0 && (
        <TableContainer
          sx={{
            bgcolor: "#fdf2df",
            borderRadius: "0.75rem",
            overflow: "hidden",
          }}
        >
          <Table aria-label="Open lobbies">
            <TableHead>
              <TableRow sx={{ bgcolor: "#f5e7cb" }}>
                {(
                  ["Room Name", "Players", "Status", "Password", ""] as const
                ).map((label, i) => (
                  <TableCell
                    key={i}
                    align={i === 4 ? "right" : "left"}
                    sx={{
                      fontFamily: "var(--font-work-sans), sans-serif",
                      fontSize: "0.7rem",
                      fontWeight: 600,
                      textTransform: "uppercase",
                      letterSpacing: "0.1em",
                      color: "#695e45",
                      border: "none",
                      py: 2,
                      px: 4,
                    }}
                  >
                    {label}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {rooms.map((room, index) => {
                const full = isRoomFull(room);
                // Alternate subtle background on every other row.
                const rowBg =
                  index % 2 === 1 ? "rgba(249,236,213,0.5)" : "transparent";

                return (
                  <TableRow
                    key={room.id}
                    sx={{
                      bgcolor: rowBg,
                      "&:hover": { bgcolor: "#f1e1c1" },
                      transition: "background-color 150ms ease",
                      // Remove MUI default bottom border.
                      "& td": { border: "none" },
                    }}
                  >
                    {/* Room name — serif typeface for editorial feel */}
                    <TableCell
                      sx={{
                        fontFamily: "var(--font-newsreader), serif",
                        fontSize: "1.1rem",
                        fontWeight: 500,
                        color: "#3a311b",
                        py: 2.5,
                        px: 4,
                      }}
                    >
                      {room.name}
                    </TableCell>

                    {/* Player count */}
                    <TableCell
                      sx={{
                        fontFamily: "var(--font-work-sans), sans-serif",
                        color: "#695e45",
                        fontSize: "0.875rem",
                        py: 2.5,
                        px: 4,
                      }}
                    >
                      {room.player_count} / {room.max_players}
                    </TableCell>

                    {/* Status badge */}
                    <TableCell sx={{ py: 2.5, px: 4 }}>
                      {full ? (
                        <Chip
                          label="Full"
                          size="small"
                          sx={{
                            bgcolor: "#bfb193",
                            color: "#3a311b",
                            fontFamily: "var(--font-work-sans), sans-serif",
                            fontSize: "0.7rem",
                            fontWeight: 500,
                            height: "1.25rem",
                            borderRadius: "9999px",
                          }}
                        />
                      ) : (
                        (() => {
                          const cfg = STATUS_CONFIG[room.status] ?? {
                            label: room.status,
                            bg: "#f1e1c1",
                            color: "#3a311b",
                          };
                          return (
                            <Chip
                              label={cfg.label}
                              size="small"
                              sx={{
                                bgcolor: cfg.bg,
                                color: cfg.color,
                                fontFamily: "var(--font-work-sans), sans-serif",
                                fontSize: "0.7rem",
                                fontWeight: 500,
                                height: "1.25rem",
                                borderRadius: "9999px",
                              }}
                            />
                          );
                        })()
                      )}
                    </TableCell>

                    {/* Password indicator */}
                    <TableCell sx={{ py: 2.5, px: 4 }}>
                      {room.has_password ? (
                        <LockIcon
                          sx={{ fontSize: 16, color: "#725a42" }}
                        />
                      ) : (
                        <LockOpenIcon
                          sx={{ fontSize: 16, color: "#bfb193" }}
                        />
                      )}
                    </TableCell>

                    {/* Join action */}
                    <TableCell align="right" sx={{ py: 2.5, px: 4 }}>
                      <Button
                        size="small"
                        disabled={full}
                        onClick={() => !full && setJoiningRoom(room)}
                        sx={{
                          textTransform: "none",
                          fontFamily: "var(--font-work-sans), sans-serif",
                          fontSize: "0.8rem",
                          fontWeight: 500,
                          px: 2.5,
                          py: 0.75,
                          borderRadius: "0.375rem",
                          // Gradient "foil-stamped" primary button.
                          background: full
                            ? "#bfb193"
                            : "linear-gradient(135deg, #725a42, #654e37)",
                          color: full ? "#3a311b" : "#fff6f1",
                          opacity: full ? 0.5 : 1,
                          cursor: full ? "not-allowed" : "pointer",
                          "&:hover": {
                            background: full
                              ? "#bfb193"
                              : "linear-gradient(135deg, #7d6249, #725a42)",
                            filter: full ? "none" : "brightness(1.08)",
                          },
                          "&.Mui-disabled": {
                            background: "#bfb193",
                            color: "#3a311b",
                            opacity: 0.5,
                          },
                        }}
                      >
                        Join
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })}
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
