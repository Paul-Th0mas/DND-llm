"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Step from "@mui/material/Step";
import StepLabel from "@mui/material/StepLabel";
import Stepper from "@mui/material/Stepper";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { generateDungeon } from "@/domains/dungeon/services/dungeon.service";
import { createRoom } from "@/domains/room/services/room.service";
import { useRoomStore } from "@/domains/room/store/room.store";

// Labels for the two wizard steps shown in the MUI Stepper.
const STEP_LABELS = ["Dungeon Settings", "Room Settings"] as const;

/** Props for the StartSessionWizard component. */
export interface StartSessionWizardProps {
  /** Whether the dialog is currently open. */
  readonly open: boolean;
  /** Callback invoked when the dialog should close. */
  readonly onClose: () => void;
  /** UUID of the campaign this session belongs to. */
  readonly campaignId: string;
}

/**
 * Form state for Step 1 — dungeon generation parameters.
 */
interface DungeonFormState {
  room_count: number;
  party_size: number;
  difficulty_override: string;
  dm_notes: string;
}

/**
 * Form state for Step 2 — game room configuration.
 */
interface RoomFormState {
  room_name: string;
  max_players: number;
}

/**
 * Two-step MUI Dialog wizard that generates a dungeon and opens a game room.
 *
 * Step 1: Collect dungeon settings (room count, party size, optional difficulty
 *         override and DM notes). Calls POST /api/v1/campaigns/{id}/dungeons.
 * Step 2: Collect room settings (name, max players). Calls POST /api/v1/rooms/create
 *         with the dungeon_id obtained from step 1.
 *
 * On full success, the new room is stored in the Zustand room store and the
 * user is navigated to /room/[roomId].
 *
 * If dungeon generation fails, an error is shown and the user may retry from
 * step 1. If room creation fails after a successful dungeon, the dungeon_id is
 * preserved so only the room creation call is retried.
 *
 * @param open - Controls dialog visibility.
 * @param onClose - Called when the user cancels or the wizard completes.
 * @param campaignId - UUID of the campaign to generate the dungeon under.
 */
export function StartSessionWizard({
  open,
  onClose,
  campaignId,
}: StartSessionWizardProps): React.ReactElement {
  const router = useRouter();
  const setRoom = useRoomStore((s) => s.setRoom);

  const [activeStep, setActiveStep] = useState(0);

  // Dungeon form — step 1.
  const [dungeonForm, setDungeonForm] = useState<DungeonFormState>({
    room_count: 8,
    party_size: 4,
    difficulty_override: "",
    dm_notes: "",
  });

  // Room form — step 2.
  const [roomForm, setRoomForm] = useState<RoomFormState>({
    room_name: "",
    max_players: 8,
  });

  // Preserved dungeon_id after a successful step 1. Used to skip re-generation
  // when retrying room creation after a step 2 failure.
  const [createdDungeonId, setCreatedDungeonId] = useState<string | null>(null);

  // Loading overlay messages — non-null means a request is in flight.
  const [loadingMessage, setLoadingMessage] = useState<string | null>(null);

  // Error state — separate messages for each failure scenario.
  const [dungeonError, setDungeonError] = useState<string | null>(null);
  const [roomError, setRoomError] = useState<string | null>(null);

  // Validation error for the room name field.
  const [roomNameError, setRoomNameError] = useState<string | null>(null);

  /**
   * Resets all wizard state and closes the dialog.
   */
  function handleClose(): void {
    setActiveStep(0);
    setDungeonForm({ room_count: 8, party_size: 4, difficulty_override: "", dm_notes: "" });
    setRoomForm({ room_name: "", max_players: 8 });
    setCreatedDungeonId(null);
    setLoadingMessage(null);
    setDungeonError(null);
    setRoomError(null);
    setRoomNameError(null);
    onClose();
  }

  /**
   * Handles the "Next" action on step 1.
   * Calls the dungeon generation endpoint and advances to step 2 on success.
   */
  async function handleGenerateDungeon(): Promise<void> {
    const token = localStorage.getItem("access_token") ?? "";
    setDungeonError(null);
    setLoadingMessage("Generating dungeon content...");

    try {
      const result = await generateDungeon(
        campaignId,
        {
          room_count: dungeonForm.room_count,
          party_size: dungeonForm.party_size,
          difficulty_override: dungeonForm.difficulty_override.trim() || null,
          dm_notes: dungeonForm.dm_notes.trim() || null,
        },
        token
      );
      setCreatedDungeonId(result.dungeon_id);
      setActiveStep(1);
    } catch {
      setDungeonError("Dungeon generation failed. Please check your settings and try again.");
    } finally {
      setLoadingMessage(null);
    }
  }

  /**
   * Validates the room form.
   * @returns True if the form is valid and submission should proceed.
   */
  function validateRoomForm(): boolean {
    if (roomForm.room_name.trim().length === 0) {
      setRoomNameError("Room name is required.");
      return false;
    }
    setRoomNameError(null);
    return true;
  }

  /**
   * Handles the final submit on step 2.
   * Calls the room creation endpoint using the dungeon_id from step 1.
   * On success, stores the room in the Zustand store and navigates to the room page.
   */
  async function handleCreateRoom(): Promise<void> {
    if (!validateRoomForm()) return;
    if (createdDungeonId === null) return;

    const token = localStorage.getItem("access_token") ?? "";
    setRoomError(null);
    setLoadingMessage("Opening room...");

    try {
      const response = await createRoom(
        roomForm.room_name.trim(),
        roomForm.max_players,
        token,
        createdDungeonId,
        campaignId
      );
      // Persist room token in localStorage so the room page can recover it on refresh.
      localStorage.setItem(`room_token_${response.room.id}`, response.room_token);
      setRoom(response.room, response.room_token);
      handleClose();
      router.push(`/room/${response.room.id}`);
    } catch {
      setRoomError(
        "Your dungeon was created. The room could not be opened. You can retry below."
      );
    } finally {
      setLoadingMessage(null);
    }
  }

  /**
   * Updates a single field in the dungeon form state.
   * @param field - The form field key to update.
   * @param value - The new value for that field.
   */
  function updateDungeonField<K extends keyof DungeonFormState>(
    field: K,
    value: DungeonFormState[K]
  ): void {
    setDungeonForm((prev) => ({ ...prev, [field]: value }));
  }

  /**
   * Updates a single field in the room form state.
   * @param field - The form field key to update.
   * @param value - The new value for that field.
   */
  function updateRoomField<K extends keyof RoomFormState>(
    field: K,
    value: RoomFormState[K]
  ): void {
    setRoomForm((prev) => ({ ...prev, [field]: value }));
  }

  const isLoading = loadingMessage !== null;

  return (
    <Dialog open={open} onClose={isLoading ? undefined : handleClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ fontWeight: 700, color: "#1e1410" }}>
        Start a Session
      </DialogTitle>

      <DialogContent dividers>
        {/* Loading overlay */}
        {isLoading && (
          <Box
            sx={{
              position: "absolute",
              inset: 0,
              bgcolor: "rgba(249, 248, 246, 0.85)",
              zIndex: 10,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: 2,
            }}
          >
            <CircularProgress sx={{ color: "#a07d60" }} />
            <Typography variant="body2" sx={{ color: "#5c4230", fontWeight: 600 }}>
              {loadingMessage}
            </Typography>
          </Box>
        )}

        {/* Stepper */}
        <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
          {STEP_LABELS.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {/* Step 1 — Dungeon Settings */}
        {activeStep === 0 && (
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2.5 }}>
            {dungeonError !== null && (
              <Alert severity="error" onClose={() => setDungeonError(null)}>
                {dungeonError}
              </Alert>
            )}

            <TextField
              label="Room Count"
              type="number"
              value={dungeonForm.room_count}
              onChange={(e) =>
                updateDungeonField("room_count", Number(e.target.value))
              }
              inputProps={{ min: 5, max: 15 }}
              helperText="Number of rooms to generate (5 – 15)"
              fullWidth
            />

            <TextField
              label="Party Size"
              type="number"
              value={dungeonForm.party_size}
              onChange={(e) =>
                updateDungeonField("party_size", Number(e.target.value))
              }
              inputProps={{ min: 1, max: 8 }}
              helperText="Number of players in the party (1 – 8)"
              fullWidth
            />

            <TextField
              label="Difficulty Override"
              value={dungeonForm.difficulty_override}
              onChange={(e) =>
                updateDungeonField("difficulty_override", e.target.value)
              }
              placeholder="e.g. Hard"
              helperText="Optional. Leave blank to use campaign defaults."
              fullWidth
            />

            <TextField
              label="DM Notes"
              value={dungeonForm.dm_notes}
              onChange={(e) => updateDungeonField("dm_notes", e.target.value)}
              placeholder="Hints for the LLM, story beats, custom flavour..."
              multiline
              minRows={3}
              helperText="Optional. Appended to the generation prompt."
              fullWidth
            />
          </Box>
        )}

        {/* Step 2 — Room Settings */}
        {activeStep === 1 && (
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2.5 }}>
            {roomError !== null && (
              <Alert severity="error">
                {roomError}
              </Alert>
            )}

            <TextField
              label="Room Name"
              value={roomForm.room_name}
              onChange={(e) => {
                updateRoomField("room_name", e.target.value);
                if (roomNameError !== null) setRoomNameError(null);
              }}
              error={roomNameError !== null}
              helperText={roomNameError ?? "A display name for the game room."}
              fullWidth
              required
            />

            <TextField
              label="Max Players"
              type="number"
              value={roomForm.max_players}
              onChange={(e) =>
                updateRoomField("max_players", Number(e.target.value))
              }
              inputProps={{ min: 1, max: 50 }}
              helperText="Maximum number of players allowed (1 – 50)"
              fullWidth
            />
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2, gap: 1 }}>
        <Button
          onClick={handleClose}
          disabled={isLoading}
          sx={{ textTransform: "none", color: "#5c4230" }}
        >
          Cancel
        </Button>

        {/* Back button — only shown on step 2 when no room error is present */}
        {activeStep === 1 && roomError === null && (
          <Button
            onClick={() => {
              setActiveStep(0);
              setRoomError(null);
            }}
            disabled={isLoading}
            sx={{ textTransform: "none", color: "#5c4230" }}
          >
            Back
          </Button>
        )}

        {/* Primary action */}
        {activeStep === 0 && (
          <Button
            variant="contained"
            onClick={() => void handleGenerateDungeon()}
            disabled={isLoading}
            sx={{
              textTransform: "none",
              fontWeight: 600,
              bgcolor: "#7d5e45",
              "&:hover": { bgcolor: "#5c4230" },
            }}
          >
            Generate Dungeon
          </Button>
        )}

        {activeStep === 1 && roomError === null && (
          <Button
            variant="contained"
            onClick={() => void handleCreateRoom()}
            disabled={isLoading}
            sx={{
              textTransform: "none",
              fontWeight: 600,
              bgcolor: "#7d5e45",
              "&:hover": { bgcolor: "#5c4230" },
            }}
          >
            Open Room
          </Button>
        )}

        {/* Retry room creation after a step 2 failure — dungeon already exists */}
        {activeStep === 1 && roomError !== null && (
          <Button
            variant="contained"
            onClick={() => void handleCreateRoom()}
            disabled={isLoading}
            sx={{
              textTransform: "none",
              fontWeight: 600,
              bgcolor: "#7d5e45",
              "&:hover": { bgcolor: "#5c4230" },
            }}
          >
            Retry Room Creation
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
}
