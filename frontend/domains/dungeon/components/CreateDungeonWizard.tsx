"use client";

import { useState } from "react";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useDungeonGeneration } from "../hooks/useDungeonGeneration";

// Static bounds for the dungeon generation form fields.
const ROOM_COUNT_MIN = 5 as const;
const ROOM_COUNT_MAX = 15 as const;
const ROOM_COUNT_DEFAULT = 8 as const;
const PARTY_SIZE_MIN = 1 as const;
const PARTY_SIZE_MAX = 8 as const;
const PARTY_SIZE_DEFAULT = 4 as const;

/** Props for the CreateDungeonWizard component. */
export interface CreateDungeonWizardProps {
  /** The UUID of the campaign to generate a dungeon for. */
  readonly campaignId: string;
  /** Called with the new dungeon ID when generation succeeds. */
  readonly onGenerated: (dungeonId: string) => void;
  /** Called when the user cancels without generating. */
  readonly onCancel: () => void;
}

// Internal form state for the dungeon generation form.
interface FormData {
  room_count: number;
  party_size: number;
  difficulty_override: string;
  dm_notes: string;
}

const INITIAL_FORM: FormData = {
  room_count: ROOM_COUNT_DEFAULT,
  party_size: PARTY_SIZE_DEFAULT,
  difficulty_override: "",
  dm_notes: "",
};

/**
 * Inline form for DMs to configure and trigger dungeon generation for a campaign.
 * Fields: room count, party size, optional difficulty override, optional DM notes.
 * On success, calls onGenerated with the newly created dungeon ID.
 */
export function CreateDungeonWizard({
  campaignId,
  onGenerated,
  onCancel,
}: CreateDungeonWizardProps): React.ReactElement {
  const [formData, setFormData] = useState<FormData>(INITIAL_FORM);
  const [validationError, setValidationError] = useState<string | null>(null);
  const { generate, isGenerating, error: generationError } = useDungeonGeneration();

  /**
   * Validates the form fields.
   * @returns An error message string, or null if all fields are valid.
   */
  function validate(): string | null {
    if (
      formData.room_count < ROOM_COUNT_MIN ||
      formData.room_count > ROOM_COUNT_MAX
    ) {
      return `Room count must be between ${ROOM_COUNT_MIN} and ${ROOM_COUNT_MAX}.`;
    }
    if (
      formData.party_size < PARTY_SIZE_MIN ||
      formData.party_size > PARTY_SIZE_MAX
    ) {
      return `Party size must be between ${PARTY_SIZE_MIN} and ${PARTY_SIZE_MAX}.`;
    }
    return null;
  }

  async function handleSubmit(): Promise<void> {
    const err = validate();
    if (err) {
      setValidationError(err);
      return;
    }
    setValidationError(null);

    const token = localStorage.getItem("access_token") ?? "";
    if (!token) {
      setValidationError("You are not authenticated. Please log in again.");
      return;
    }

    const result = await generate(
      campaignId,
      {
        room_count: formData.room_count,
        party_size: formData.party_size,
        difficulty_override: formData.difficulty_override.trim() || null,
        dm_notes: formData.dm_notes.trim() || null,
      },
      token
    );

    if (result !== null) {
      onGenerated(result.dungeon_id);
    }
  }

  const displayError = validationError ?? generationError;

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      <Typography variant="h6" fontWeight={700}>
        Generate Dungeon
      </Typography>

      {displayError !== null && (
        <Alert
          severity="error"
          onClose={() => setValidationError(null)}
          sx={{ fontSize: "0.8rem" }}
        >
          {displayError}
        </Alert>
      )}

      {isGenerating ? (
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 2,
            py: 5,
          }}
        >
          <CircularProgress size={40} sx={{ color: "primary.main" }} />
          <Typography variant="body2" color="text.secondary">
            Generating your dungeon — this may take a few seconds...
          </Typography>
        </Box>
      ) : (
        <>
          <Box className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <TextField
              label="Room Count"
              type="number"
              value={formData.room_count}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  room_count: parseInt(e.target.value, 10) || ROOM_COUNT_DEFAULT,
                }))
              }
              inputProps={{ min: ROOM_COUNT_MIN, max: ROOM_COUNT_MAX }}
              helperText={`${ROOM_COUNT_MIN}–${ROOM_COUNT_MAX} rooms`}
              size="small"
              fullWidth
              sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2 } }}
            />

            <TextField
              label="Party Size"
              type="number"
              value={formData.party_size}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  party_size: parseInt(e.target.value, 10) || PARTY_SIZE_DEFAULT,
                }))
              }
              inputProps={{ min: PARTY_SIZE_MIN, max: PARTY_SIZE_MAX }}
              helperText={`${PARTY_SIZE_MIN}–${PARTY_SIZE_MAX} players`}
              size="small"
              fullWidth
              sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2 } }}
            />
          </Box>

          <TextField
            label="Difficulty Override (optional)"
            value={formData.difficulty_override}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                difficulty_override: e.target.value,
              }))
            }
            placeholder="e.g. Hard, Deadly"
            size="small"
            fullWidth
            sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2 } }}
          />

          <TextField
            label="DM Notes (optional)"
            value={formData.dm_notes}
            onChange={(e) =>
              setFormData((prev) => ({ ...prev, dm_notes: e.target.value }))
            }
            multiline
            rows={3}
            placeholder="Extra hints or narrative seeds for the dungeon generator..."
            size="small"
            fullWidth
            sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2 } }}
          />

          <Box sx={{ display: "flex", justifyContent: "flex-end", gap: 1.5, pt: 1 }}>
            <Button
              onClick={onCancel}
              sx={{ textTransform: "none", color: "text.secondary" }}
            >
              Cancel
            </Button>
            <Button
              variant="contained"
              onClick={() => void handleSubmit()}
              disabled={isGenerating}
              sx={{
                textTransform: "none",
                fontWeight: 600,
                borderRadius: 2,
                bgcolor: "#a07d60",
                "&:hover": { bgcolor: "#7d5e45" },
              }}
            >
              Generate Dungeon
            </Button>
          </Box>
        </>
      )}
    </Box>
  );
}
