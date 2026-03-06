"use client";

import { useState } from "react";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Divider from "@mui/material/Divider";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import Slider from "@mui/material/Slider";
import Step from "@mui/material/Step";
import StepLabel from "@mui/material/StepLabel";
import Stepper from "@mui/material/Stepper";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useWorldOptions } from "@/domains/world/hooks/useWorldOptions";
import { useWorldGeneration } from "@/domains/world/hooks/useWorldGeneration";
import { selectGeneratedWorld, useWorldStore } from "@/domains/world/store/world.store";
import type {
  Difficulty,
  GeneratedWorldResponse,
  QuestFocus,
  Theme,
  WorldOptionsResponse,
} from "@/domains/world/types";

// Labels shown above each step in the MUI Stepper.
const STEPS = ["World Setup", "Quest Settings", "Review & Generate"] as const;

/**
 * Converts a SCREAMING_SNAKE_CASE enum value to Title Case for display.
 * Used for all option labels since the API returns raw enum string values.
 * @param value - The enum string to format (e.g. "MEDIEVAL_FANTASY").
 * @returns A human-readable label (e.g. "Medieval Fantasy").
 */
function toLabel(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

// Internal form state accumulated across the three wizard steps.
interface WizardFormData {
  theme: Theme | "";
  difficulty: Difficulty | "";
  questFocus: QuestFocus | "";
  roomCount: number;
  partySize: number;
  dmNotes: string;
}

const INITIAL_FORM: WizardFormData = {
  theme: "",
  difficulty: "",
  questFocus: "",
  roomCount: 10,
  partySize: 1,
  dmNotes: "",
};

/** Props for the CreateWorldWizard dialog. */
interface CreateWorldWizardProps {
  readonly open: boolean;
  readonly onClose: () => void;
  /**
   * Called when the DM has generated a world and clicks "Create Room".
   * The parent is responsible for opening the room-creation flow.
   */
  readonly onProceedToCreateRoom: () => void;
}

/**
 * Multi-step wizard dialog for DMs to configure and generate a world.
 * Steps: World Setup → Quest Settings → Review & Generate → Success preview.
 * On success the DM can proceed to room creation or simply close the wizard.
 *
 * Options (themes, difficulties, quest focuses, slider bounds) are fetched once
 * from GET /api/v1/worlds/options on first open and cached for the lifetime of
 * the component. All step-2 filtering is done client-side from that single response.
 */
export function CreateWorldWizard({
  open,
  onClose,
  onProceedToCreateRoom,
}: CreateWorldWizardProps): React.ReactElement {
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState<WizardFormData>(INITIAL_FORM);
  // Local error for validation messages; generation errors come from the hook.
  const [validationError, setValidationError] = useState<string | null>(null);

  // Hooks that delegate to the world store.
  const { options, isLoading: optionsLoading, error: optionsError } = useWorldOptions();
  const { generate, isGenerating, error: generationError } = useWorldGeneration();
  const generatedWorld = useWorldStore(selectGeneratedWorld);

  /** Resets transient wizard state (form, step, validation errors). */
  function handleClose(): void {
    setActiveStep(0);
    setFormData(INITIAL_FORM);
    setValidationError(null);
    onClose();
  }

  function handleBack(): void {
    setValidationError(null);
    setActiveStep((prev) => prev - 1);
  }

  /**
   * Validates the fields that are required on the given step.
   * Returns an error message string, or null if all required fields are filled.
   */
  function validateStep(step: number): string | null {
    if (step === 0) {
      if (!formData.theme) return "Please select a theme.";
      if (!formData.difficulty) return "Please select a difficulty.";
    }
    if (step === 1) {
      if (!formData.questFocus) return "Please select a quest focus.";
    }
    return null;
  }

  function handleNext(): void {
    const err = validateStep(activeStep);
    if (err) {
      setValidationError(err);
      return;
    }
    setValidationError(null);
    setActiveStep((prev) => prev + 1);
  }

  async function handleGenerate(): Promise<void> {
    const err = validateStep(activeStep);
    if (err) {
      setValidationError(err);
      return;
    }

    const token = localStorage.getItem("access_token");
    if (!token) {
      setValidationError("You are not authenticated. Please log in again.");
      return;
    }

    setValidationError(null);
    await generate(
      {
        // These are safe to cast: validateStep confirmed they are non-empty.
        theme: formData.theme as Theme,
        difficulty: formData.difficulty as Difficulty,
        quest_focus: formData.questFocus as QuestFocus,
        room_count: formData.roomCount,
        party_size: formData.partySize,
        dm_notes: formData.dmNotes.trim() || null,
      },
      token
    );
  }

  function handleProceedToRoom(): void {
    handleClose();
    onProceedToCreateRoom();
  }

  // ---- Step renderers ----
  // opts is guaranteed non-null at the call site (guarded in renderContent).

  function renderStep1(opts: WorldOptionsResponse): React.ReactElement {
    return (
      <Box sx={{ display: "flex", flexDirection: "column", gap: 3, pt: 1 }}>
        <FormControl fullWidth size="small">
          <InputLabel id="theme-label">Theme</InputLabel>
          <Select
            labelId="theme-label"
            label="Theme"
            value={formData.theme}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                // e.target.value is string from MUI Select; cast to the union type.
                theme: e.target.value as Theme,
              }))
            }
            inputProps={{ "aria-label": "Theme" }}
            sx={{ borderRadius: 2 }}
          >
            {opts.themes.map((value) => (
              <MenuItem key={value} value={value}>
                {toLabel(value)}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl fullWidth size="small">
          <InputLabel id="difficulty-label">Difficulty</InputLabel>
          <Select
            labelId="difficulty-label"
            label="Difficulty"
            value={formData.difficulty}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                difficulty: e.target.value as Difficulty,
              }))
            }
            inputProps={{ "aria-label": "Difficulty" }}
            sx={{ borderRadius: 2 }}
          >
            {opts.difficulties.map((value) => (
              <MenuItem key={value} value={value}>
                {toLabel(value)}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>
    );
  }

  function renderStep2(opts: WorldOptionsResponse): React.ReactElement {
    return (
      <Box sx={{ display: "flex", flexDirection: "column", gap: 3, pt: 1 }}>
        <FormControl fullWidth size="small">
          <InputLabel id="quest-focus-label">Quest Focus</InputLabel>
          <Select
            labelId="quest-focus-label"
            label="Quest Focus"
            value={formData.questFocus}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                questFocus: e.target.value as QuestFocus,
              }))
            }
            inputProps={{ "aria-label": "Quest Focus" }}
            sx={{ borderRadius: 2 }}
          >
            {opts.quest_focuses.map((value) => (
              <MenuItem key={value} value={value}>
                {toLabel(value)}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Room Count: {formData.roomCount}
          </Typography>
          <Slider
            value={formData.roomCount}
            onChange={(_, val) =>
              setFormData((prev) => ({ ...prev, roomCount: val as number }))
            }
            min={opts.room_count_min}
            max={opts.room_count_max}
            step={1}
            marks
            valueLabelDisplay="auto"
            sx={{ color: "primary.main" }}
          />
        </Box>

        <Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Party Size: {formData.partySize}
          </Typography>
          <Slider
            value={formData.partySize}
            onChange={(_, val) =>
              setFormData((prev) => ({ ...prev, partySize: val as number }))
            }
            min={1}
            max={6}
            step={1}
            marks
            valueLabelDisplay="auto"
            sx={{ color: "primary.main" }}
          />
        </Box>
      </Box>
    );
  }

  function renderStep3(): React.ReactElement {
    return (
      <Box sx={{ display: "flex", flexDirection: "column", gap: 3, pt: 1 }}>
        {/* Summary of choices made in the previous two steps. */}
        <Box
          sx={{
            p: 2,
            bgcolor: "background.default",
            border: "1px solid",
            borderColor: "divider",
            borderRadius: 2,
          }}
        >
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Summary
          </Typography>
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
            <Chip
              label={`Theme: ${formData.theme ? toLabel(formData.theme) : "—"}`}
              size="small"
            />
            <Chip
              label={`Difficulty: ${formData.difficulty ? toLabel(formData.difficulty) : "—"}`}
              size="small"
            />
            <Chip
              label={`Quest: ${formData.questFocus ? toLabel(formData.questFocus) : "—"}`}
              size="small"
            />
            <Chip label={`Rooms: ${formData.roomCount}`} size="small" />
            <Chip label={`Party: ${formData.partySize}`} size="small" />
          </Box>
        </Box>

        <TextField
          label="DM Notes (optional)"
          value={formData.dmNotes}
          onChange={(e) =>
            setFormData((prev) => ({ ...prev, dmNotes: e.target.value }))
          }
          multiline
          rows={3}
          fullWidth
          size="small"
          placeholder="Extra hints or narrative seeds for the world generator..."
          sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2 } }}
        />
      </Box>
    );
  }

  function renderSuccessState(world: GeneratedWorldResponse): React.ReactElement {
    return (
      <Box sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 1 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, flexWrap: "wrap" }}>
          <Typography variant="h6" fontWeight={700}>
            {world.world_name}
          </Typography>
          <Chip label={toLabel(world.theme)} size="small" color="primary" />
        </Box>

        <Typography variant="body2" color="text.secondary">
          {world.world_description}
        </Typography>

        <Typography variant="caption" color="text.secondary" sx={{ fontStyle: "italic" }}>
          {world.atmosphere}
        </Typography>

        <Divider />

        <Box>
          <Typography variant="subtitle2" fontWeight={600} gutterBottom>
            Main Quest: {world.main_quest.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {world.main_quest.description}
          </Typography>
        </Box>

        <Box sx={{ display: "flex", gap: 3, flexWrap: "wrap" }}>
          <Typography variant="caption" color="text.secondary">
            {world.rooms.length} rooms generated
          </Typography>
          {world.active_factions.length > 0 && (
            <Typography variant="caption" color="text.secondary">
              Factions: {world.active_factions.join(", ")}
            </Typography>
          )}
        </Box>
      </Box>
    );
  }

  function renderContent(): React.ReactElement {
    if (isGenerating) {
      return (
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 2,
            py: 5,
          }}
        >
          <CircularProgress size={40} />
          <Typography variant="body2" color="text.secondary">
            Generating your world — this may take a few seconds...
          </Typography>
        </Box>
      );
    }

    if (generatedWorld) {
      return renderSuccessState(generatedWorld);
    }

    // Show a loading spinner until the options API responds.
    if (optionsLoading) {
      return (
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 2,
            py: 5,
          }}
        >
          <CircularProgress size={32} />
          <Typography variant="body2" color="text.secondary">
            Loading options...
          </Typography>
        </Box>
      );
    }

    // options is non-null here; pass it explicitly so inner renderers are type-safe.
    if (!options) return <></>;

    switch (activeStep) {
      case 0:
        return renderStep1(options);
      case 1:
        return renderStep2(options);
      case 2:
        return renderStep3();
      default:
        return <></>;
    }
  }

  // The combined error to display — validation takes priority over generation errors.
  const displayError = validationError ?? optionsError ?? generationError;
  const isSuccess = generatedWorld !== null;

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ fontWeight: 700, pb: 1 }}>
        {isSuccess ? "World Created" : "Create Your World"}
      </DialogTitle>

      {/* Only show the stepper while the form is active, not on the success or loading screens. */}
      {!isSuccess && !isGenerating && !optionsLoading && options !== null && (
        <Box sx={{ px: 3, pb: 1 }}>
          <Stepper activeStep={activeStep} alternativeLabel>
            {STEPS.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
        </Box>
      )}

      <DialogContent>
        {displayError !== null && (
          <Alert
            severity="error"
            onClose={() => setValidationError(null)}
            sx={{ mb: 2, fontSize: "0.8rem" }}
          >
            {displayError}
          </Alert>
        )}
        {renderContent()}
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2.5, gap: 1 }}>
        {isSuccess ? (
          <>
            <Button
              onClick={handleClose}
              sx={{ textTransform: "none", color: "text.secondary" }}
            >
              Close
            </Button>
            <Button
              variant="contained"
              onClick={handleProceedToRoom}
              sx={{ textTransform: "none", fontWeight: 600, borderRadius: 2 }}
            >
              Create Room
            </Button>
          </>
        ) : (
          <>
            <Button
              onClick={activeStep === 0 ? handleClose : handleBack}
              disabled={isGenerating || optionsLoading}
              sx={{ textTransform: "none", color: "text.secondary" }}
            >
              {activeStep === 0 ? "Cancel" : "Back"}
            </Button>

            {activeStep < STEPS.length - 1 ? (
              <Button
                variant="contained"
                onClick={handleNext}
                disabled={isGenerating || optionsLoading}
                sx={{ textTransform: "none", fontWeight: 600, borderRadius: 2 }}
              >
                Next
              </Button>
            ) : (
              <Button
                variant="contained"
                onClick={() => void handleGenerate()}
                disabled={isGenerating || optionsLoading}
                sx={{ textTransform: "none", fontWeight: 600, borderRadius: 2 }}
              >
                Generate World
              </Button>
            )}
          </>
        )}
      </DialogActions>
    </Dialog>
  );
}
