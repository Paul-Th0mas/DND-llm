"use client";

import { useEffect, useState } from "react";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import Slider from "@mui/material/Slider";
import Step from "@mui/material/Step";
import StepLabel from "@mui/material/StepLabel";
import Stepper from "@mui/material/Stepper";
import TextField from "@mui/material/TextField";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import { useCampaignCreation } from "@/domains/campaign/hooks/useCampaignCreation";
import {
  CAMPAIGN_LEVEL_MAX,
  CAMPAIGN_LEVEL_MIN,
  CAMPAIGN_PLAYER_COUNT_MAX,
  CAMPAIGN_PLAYER_COUNT_MIN,
} from "@/shared/constants";
import type { CampaignTone, CreateCampaignRequest } from "@/domains/campaign/types";
import { getWorlds } from "@/domains/world/services/world.service";
import type { WorldSummary } from "@/domains/world/types";

const STEPS = ["World", "Basics", "Logistics", "Themes", "Safety", "Review"] as const;

const TONES: readonly CampaignTone[] = [
  "dark_fantasy",
  "high_fantasy",
  "horror",
  "political_intrigue",
  "swashbuckling",
];

const EDITIONS = ["5e", "5.5e", "Pathfinder 2e", "OSE"] as const;

/**
 * Converts an underscore-separated string to Title Case for display.
 * @param value - The raw string (e.g. "dark_fantasy").
 * @returns A human-readable label (e.g. "Dark Fantasy").
 */
function toLabel(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

// Internal form state accumulated across the wizard steps.
interface WizardFormData {
  // Step 0 — World
  worldId: string;
  // Step 1 — Basics
  campaignName: string;
  edition: string;
  tone: CampaignTone | "";
  // Step 2 — Logistics
  playerCount: number;
  levelStart: number;
  levelEnd: number;
  // Step 3 — Themes
  themes: readonly string[];
  themeInput: string;
  // Step 4 — Safety (Lines)
  lines: readonly string[];
  lineInput: string;
}

const INITIAL_FORM: WizardFormData = {
  worldId: "",
  campaignName: "",
  edition: "5e",
  tone: "",
  playerCount: 4,
  levelStart: 1,
  levelEnd: 10,
  themes: [],
  themeInput: "",
  lines: [],
  lineInput: "",
};

/** Props for the CreateCampaignWizard dialog. */
export interface CreateCampaignWizardProps {
  readonly open: boolean;
  readonly onClose: () => void;
  /** Called when a campaign has been created successfully. Receives the new campaign ID. */
  readonly onCreated: (campaignId: string) => void;
}

/**
 * Multi-step dialog wizard for DMs to define and create a new campaign.
 * Steps: World -> Basics -> Logistics -> Themes & Rules -> Safety -> Review.
 * The first step lets the DM pick from a list of pre-seeded worlds.
 * On submit calls createCampaign() and writes the campaign ID to the campaign store.
 */
export function CreateCampaignWizard({
  open,
  onClose,
  onCreated,
}: CreateCampaignWizardProps): React.ReactElement {
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState<WizardFormData>(INITIAL_FORM);
  const [validationError, setValidationError] = useState<string | null>(null);

  // World picker state — loaded lazily when the dialog opens on step 0.
  const [worlds, setWorlds] = useState<WorldSummary[]>([]);
  const [isLoadingWorlds, setIsLoadingWorlds] = useState(false);
  const [worldsError, setWorldsError] = useState<string | null>(null);

  const { create, isCreating, error: creationError } = useCampaignCreation();

  // Load worlds when the dialog opens and we are on the world step.
  useEffect(() => {
    if (!open || activeStep !== 0) return;

    let cancelled = false;
    setIsLoadingWorlds(true);
    setWorldsError(null);

    getWorlds()
      .then((result) => {
        if (!cancelled) setWorlds(result);
      })
      .catch(() => {
        if (!cancelled) setWorldsError("Failed to load worlds. Please close and try again.");
      })
      .finally(() => {
        if (!cancelled) setIsLoadingWorlds(false);
      });

    return () => {
      cancelled = true;
    };
  }, [open, activeStep]);

  function handleClose(): void {
    setActiveStep(0);
    setFormData(INITIAL_FORM);
    setValidationError(null);
    setWorlds([]);
    setWorldsError(null);
    onClose();
  }

  function handleBack(): void {
    setValidationError(null);
    setActiveStep((prev) => prev - 1);
  }

  /**
   * Validates the fields required for the given step.
   * Returns an error string, or null if all required fields are filled.
   */
  function validateStep(step: number): string | null {
    if (step === 0) {
      if (!formData.worldId) return "Please select a world.";
    }
    if (step === 1) {
      if (!formData.campaignName.trim()) return "Campaign name is required.";
      if (!formData.tone) return "Please select a tone.";
    }
    if (step === 2) {
      if (formData.levelStart > formData.levelEnd) {
        return "Level range start cannot be greater than end.";
      }
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

  async function handleSubmit(): Promise<void> {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setValidationError("You are not authenticated. Please log in again.");
      return;
    }
    setValidationError(null);

    const request: CreateCampaignRequest = {
      campaign_name: formData.campaignName.trim(),
      edition: formData.edition,
      // Safe to cast — validateStep confirmed they are non-empty at step 1.
      tone: formData.tone as CampaignTone,
      world_id: formData.worldId,
      player_count: formData.playerCount,
      level_range: { start: formData.levelStart, end: formData.levelEnd },
      themes: formData.themes,
      content_boundaries: { lines: formData.lines },
    };

    await create(request, token);
    // The hook writes to the store; read the ID from the store via the callback.
    // Since useCampaignCreation calls setCampaignId synchronously after the API call,
    // we can read it from the store after awaiting.
    const { useCampaignStore } = await import("@/domains/campaign/store/campaign.store");
    const campaignId = useCampaignStore.getState().campaignId;
    if (campaignId !== null) {
      handleClose();
      onCreated(campaignId);
    }
  }

  // Helper to add a tag to a list field and clear the input.
  function addTag(
    listKey: "themes" | "lines",
    inputKey: "themeInput" | "lineInput"
  ): void {
    const value = formData[inputKey].trim();
    if (!value) return;
    setFormData((prev) => ({
      ...prev,
      [listKey]: [...prev[listKey], value],
      [inputKey]: "",
    }));
  }

  function removeTag(
    listKey: "themes" | "lines",
    index: number
  ): void {
    setFormData((prev) => ({
      ...prev,
      [listKey]: (prev[listKey] as string[]).filter((_, i) => i !== index),
    }));
  }

  // ---- Step renderers ----

  function renderStep0(): React.ReactElement {
    if (isLoadingWorlds) {
      return (
        <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 2, py: 5 }}>
          <CircularProgress size={36} />
          <Typography variant="body2" color="text.secondary">Loading worlds...</Typography>
        </Box>
      );
    }

    if (worldsError !== null) {
      return (
        <Alert severity="error" sx={{ mt: 1 }}>{worldsError}</Alert>
      );
    }

    return (
      <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5, pt: 1 }}>
        <Typography variant="body2" color="text.secondary">
          Select the world your campaign will be set in.
        </Typography>
        {worlds.map((world) => (
          <Card
            key={world.world_id}
            variant="outlined"
            onClick={() => setFormData((prev) => ({ ...prev, worldId: world.world_id }))}
            sx={{
              cursor: "pointer",
              borderColor: formData.worldId === world.world_id ? "#a07d60" : "divider",
              borderWidth: formData.worldId === world.world_id ? 2 : 1,
              transition: "border-color 0.15s, border-width 0.15s",
              "&:hover": { borderColor: "#a07d60" },
            }}
          >
            <CardContent sx={{ py: 1.5, "&:last-child": { pb: 1.5 } }}>
              <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 0.5 }}>
                <Typography variant="subtitle2" fontWeight={700}>
                  {world.name}
                </Typography>
                <Chip label={toLabel(world.theme)} size="small" variant="outlined" />
              </Box>
              <Typography variant="body2" color="text.secondary">
                {world.description}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>
    );
  }

  function renderStep1(): React.ReactElement {
    return (
      <Box sx={{ display: "flex", flexDirection: "column", gap: 2.5, pt: 1 }}>
        <TextField
          label="Campaign Name"
          value={formData.campaignName}
          onChange={(e) => setFormData((prev) => ({ ...prev, campaignName: e.target.value }))}
          fullWidth
          size="small"
          required
          inputProps={{ "aria-label": "Campaign Name" }}
          sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2 } }}
        />

        <FormControl fullWidth size="small">
          <InputLabel id="edition-label">Edition</InputLabel>
          <Select
            labelId="edition-label"
            label="Edition"
            value={formData.edition}
            onChange={(e) => setFormData((prev) => ({ ...prev, edition: e.target.value }))}
            inputProps={{ "aria-label": "Edition" }}
            sx={{ borderRadius: 2 }}
          >
            {EDITIONS.map((ed) => (
              <MenuItem key={ed} value={ed}>{ed}</MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl fullWidth size="small">
          <InputLabel id="tone-label">Tone</InputLabel>
          <Select
            labelId="tone-label"
            label="Tone"
            value={formData.tone}
            onChange={(e) => setFormData((prev) => ({ ...prev, tone: e.target.value as CampaignTone }))}
            inputProps={{ "aria-label": "Tone" }}
            sx={{ borderRadius: 2 }}
          >
            {TONES.map((t) => (
              <MenuItem key={t} value={t}>{toLabel(t)}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>
    );
  }

  function renderStep2(): React.ReactElement {
    return (
      <Box sx={{ display: "flex", flexDirection: "column", gap: 3, pt: 1 }}>
        <Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Player Count: {formData.playerCount}
          </Typography>
          <Slider
            value={formData.playerCount}
            onChange={(_, v) => setFormData((prev) => ({ ...prev, playerCount: v as number }))}
            min={CAMPAIGN_PLAYER_COUNT_MIN}
            max={CAMPAIGN_PLAYER_COUNT_MAX}
            step={1}
            marks
            valueLabelDisplay="auto"
            aria-label="Player Count"
          />
        </Box>

        <Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Level Range: {formData.levelStart}–{formData.levelEnd}
          </Typography>
          <Slider
            value={[formData.levelStart, formData.levelEnd]}
            onChange={(_, v) => {
              const [start, end] = v as [number, number];
              setFormData((prev) => ({ ...prev, levelStart: start, levelEnd: end }));
            }}
            min={CAMPAIGN_LEVEL_MIN}
            max={CAMPAIGN_LEVEL_MAX}
            step={1}
            marks
            valueLabelDisplay="auto"
            aria-label="Level Range"
          />
        </Box>
      </Box>
    );
  }

  function renderStep3(): React.ReactElement {
    return (
      <Box sx={{ display: "flex", flexDirection: "column", gap: 2.5, pt: 1 }}>
        {/* Themes tag input */}
        <Box>
          <Typography variant="body2" gutterBottom>Themes</Typography>
          <Box sx={{ display: "flex", gap: 1 }}>
            <TextField
              size="small"
              fullWidth
              placeholder="e.g. redemption, betrayal"
              value={formData.themeInput}
              onChange={(e) => setFormData((prev) => ({ ...prev, themeInput: e.target.value }))}
              onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addTag("themes", "themeInput"); } }}
              inputProps={{ "aria-label": "Theme input" }}
              sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2 } }}
            />
            <Button variant="outlined" onClick={() => addTag("themes", "themeInput")} sx={{ borderRadius: 2, textTransform: "none" }}>
              Add
            </Button>
          </Box>
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, mt: 1 }}>
            {formData.themes.map((t, i) => (
              <Chip key={i} label={t} size="small" onDelete={() => removeTag("themes", i)} />
            ))}
          </Box>
        </Box>
      </Box>
    );
  }

  function renderStep4(): React.ReactElement {
    return (
      <Box sx={{ display: "flex", flexDirection: "column", gap: 2.5, pt: 1 }}>
        <Typography variant="body2" color="text.secondary">
          Lines are a safety tool for collaborative storytelling.
          <Tooltip
            title={
              <Box sx={{ p: 0.5, maxWidth: 260 }}>
                <Typography variant="caption">
                  <strong>Lines</strong> — content that will never appear in the game, even off-screen (hard limits).
                </Typography>
              </Box>
            }
            placement="right"
          >
            <Box component="span" sx={{ ml: 0.5, cursor: "help", textDecoration: "underline dotted" }}>
              What are these?
            </Box>
          </Tooltip>
        </Typography>

        {/* Lines */}
        <Box>
          <Typography variant="body2" fontWeight={600} gutterBottom>Lines (hard limits)</Typography>
          <Box sx={{ display: "flex", gap: 1 }}>
            <TextField
              size="small"
              fullWidth
              placeholder="e.g. child harm, sexual violence"
              value={formData.lineInput}
              onChange={(e) => setFormData((prev) => ({ ...prev, lineInput: e.target.value }))}
              onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addTag("lines", "lineInput"); } }}
              inputProps={{ "aria-label": "Line input" }}
              sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2 } }}
            />
            <Button variant="outlined" onClick={() => addTag("lines", "lineInput")} sx={{ borderRadius: 2, textTransform: "none" }}>
              Add
            </Button>
          </Box>
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, mt: 1 }}>
            {formData.lines.map((l, i) => (
              <Chip key={i} label={l} size="small" color="error" onDelete={() => removeTag("lines", i)} />
            ))}
          </Box>
        </Box>
      </Box>
    );
  }

  function renderReview(): React.ReactElement {
    const selectedWorld = worlds.find((w) => w.world_id === formData.worldId);
    return (
      <Box sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 1 }}>
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
          <Chip label={`World: ${selectedWorld?.name ?? "—"}`} size="small" />
          <Chip label={`Name: ${formData.campaignName || "—"}`} size="small" />
          <Chip label={`Edition: ${formData.edition}`} size="small" />
          <Chip label={`Tone: ${formData.tone ? toLabel(formData.tone) : "—"}`} size="small" />
          <Chip label={`Players: ${formData.playerCount}`} size="small" />
          <Chip label={`Levels: ${formData.levelStart}–${formData.levelEnd}`} size="small" />
        </Box>
        {formData.themes.length > 0 && (
          <Box>
            <Typography variant="caption" color="text.secondary">Themes</Typography>
            <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, mt: 0.5 }}>
              {formData.themes.map((t, i) => <Chip key={i} label={t} size="small" variant="outlined" />)}
            </Box>
          </Box>
        )}
        {formData.lines.length > 0 && (
          <Box>
            <Typography variant="caption" color="text.secondary">Lines</Typography>
            <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, mt: 0.5 }}>
              {formData.lines.map((l, i) => <Chip key={i} label={l} size="small" color="error" variant="outlined" />)}
            </Box>
          </Box>
        )}
      </Box>
    );
  }

  function renderContent(): React.ReactElement {
    if (isCreating) {
      return (
        <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 2, py: 5 }}>
          <CircularProgress size={40} />
          <Typography variant="body2" color="text.secondary">
            Creating campaign...
          </Typography>
        </Box>
      );
    }

    switch (activeStep) {
      case 0: return renderStep0();
      case 1: return renderStep1();
      case 2: return renderStep2();
      case 3: return renderStep3();
      case 4: return renderStep4();
      case 5: return renderReview();
      default: return <></>;
    }
  }

  const displayError = validationError ?? creationError;

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ fontWeight: 700, pb: 1 }}>Create Campaign</DialogTitle>

      {!isCreating && (
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
          <Alert severity="error" onClose={() => setValidationError(null)} sx={{ mb: 2, fontSize: "0.8rem" }}>
            {displayError}
          </Alert>
        )}
        {renderContent()}
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2.5, gap: 1 }}>
        <Button
          onClick={activeStep === 0 ? handleClose : handleBack}
          disabled={isCreating}
          sx={{ textTransform: "none", color: "text.secondary" }}
        >
          {activeStep === 0 ? "Cancel" : "Back"}
        </Button>

        {activeStep < STEPS.length - 1 ? (
          <Button
            variant="contained"
            onClick={handleNext}
            disabled={isCreating}
            sx={{ textTransform: "none", fontWeight: 600, borderRadius: 2 }}
          >
            Next
          </Button>
        ) : (
          <Button
            variant="contained"
            onClick={() => void handleSubmit()}
            disabled={isCreating}
            sx={{ textTransform: "none", fontWeight: 600, borderRadius: 2 }}
          >
            Create Campaign
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
}
