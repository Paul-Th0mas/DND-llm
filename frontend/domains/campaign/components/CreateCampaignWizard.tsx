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
  CAMPAIGN_SESSION_COUNT_MAX,
  CAMPAIGN_SESSION_COUNT_MIN,
} from "@/shared/constants";
import type { CampaignTone, CreateCampaignRequest, SettingPreference } from "@/domains/campaign/types";

const STEPS = ["Basics", "Logistics", "Themes & Rules", "Safety", "Review"] as const;

const TONES: readonly CampaignTone[] = [
  "dark_fantasy",
  "high_fantasy",
  "horror",
  "political_intrigue",
  "swashbuckling",
];

const SETTINGS: readonly SettingPreference[] = [
  "homebrew",
  "forgotten_realms",
  "eberron",
  "ravenloft",
  "greyhawk",
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

// Internal form state accumulated across the five wizard steps.
interface WizardFormData {
  // Step 1 — Basics
  campaignName: string;
  edition: string;
  tone: CampaignTone | "";
  settingPreference: SettingPreference | "";
  // Step 2 — Logistics
  playerCount: number;
  levelStart: number;
  levelEnd: number;
  sessionCountEstimate: number;
  // Step 3 — Themes & Rules
  themes: readonly string[];
  themeInput: string;
  homebrewRules: readonly string[];
  homebrewInput: string;
  inspirations: string;
  // Step 4 — Safety (Lines & Veils)
  lines: readonly string[];
  lineInput: string;
  veils: readonly string[];
  veilInput: string;
}

const INITIAL_FORM: WizardFormData = {
  campaignName: "",
  edition: "5e",
  tone: "",
  settingPreference: "",
  playerCount: 4,
  levelStart: 1,
  levelEnd: 10,
  sessionCountEstimate: 20,
  themes: [],
  themeInput: "",
  homebrewRules: [],
  homebrewInput: "",
  inspirations: "",
  lines: [],
  lineInput: "",
  veils: [],
  veilInput: "",
};

/** Props for the CreateCampaignWizard dialog. */
interface CreateCampaignWizardProps {
  readonly open: boolean;
  readonly onClose: () => void;
  /** Called when a campaign has been created successfully. Receives the new campaign ID. */
  readonly onCreated: (campaignId: string) => void;
}

/**
 * Multi-step dialog wizard for DMs to define and create a new campaign.
 * Steps: Basics → Logistics → Themes & Rules → Safety → Review.
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

  const { create, isCreating, error: creationError } = useCampaignCreation();

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
   * Validates the fields required for the given step.
   * Returns an error string, or null if all required fields are filled.
   */
  function validateStep(step: number): string | null {
    if (step === 0) {
      if (!formData.campaignName.trim()) return "Campaign name is required.";
      if (!formData.tone) return "Please select a tone.";
      if (!formData.settingPreference) return "Please select a setting preference.";
    }
    if (step === 1) {
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
      // Safe to cast — validateStep confirmed they are non-empty at step 0.
      tone: formData.tone as CampaignTone,
      setting_preference: formData.settingPreference as SettingPreference,
      player_count: formData.playerCount,
      level_range: { start: formData.levelStart, end: formData.levelEnd },
      session_count_estimate: formData.sessionCountEstimate,
      themes: formData.themes,
      homebrew_rules: formData.homebrewRules,
      inspirations: formData.inspirations.trim() || null,
      content_boundaries: { lines: formData.lines, veils: formData.veils },
    };

    await create(request, token);
    // The hook writes to the store; read the ID from the store via the callback.
    // We use the hook's isCreating flag to detect completion; on success creationError is null.
    // The parent is notified via onCreated once the store has the ID.
    // Since useCampaignCreation calls setCampaignId synchronously after the API call,
    // we can read it from the store after awaiting. Import the store selector here
    // to avoid prop-drilling the ID back up.
    const { useCampaignStore } = await import("@/domains/campaign/store/campaign.store");
    const campaignId = useCampaignStore.getState().campaignId;
    if (campaignId !== null) {
      handleClose();
      onCreated(campaignId);
    }
  }

  // Helper to add a tag to a list field and clear the input.
  function addTag(
    listKey: "themes" | "homebrewRules" | "lines" | "veils",
    inputKey: "themeInput" | "homebrewInput" | "lineInput" | "veilInput"
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
    listKey: "themes" | "homebrewRules" | "lines" | "veils",
    index: number
  ): void {
    setFormData((prev) => ({
      ...prev,
      [listKey]: (prev[listKey] as string[]).filter((_, i) => i !== index),
    }));
  }

  // ---- Step renderers ----

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

        <FormControl fullWidth size="small">
          <InputLabel id="setting-label">Setting Preference</InputLabel>
          <Select
            labelId="setting-label"
            label="Setting Preference"
            value={formData.settingPreference}
            onChange={(e) =>
              setFormData((prev) => ({ ...prev, settingPreference: e.target.value as SettingPreference }))
            }
            inputProps={{ "aria-label": "Setting Preference" }}
            sx={{ borderRadius: 2 }}
          >
            {SETTINGS.map((s) => (
              <MenuItem key={s} value={s}>{toLabel(s)}</MenuItem>
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

        <Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Estimated Sessions: {formData.sessionCountEstimate}
          </Typography>
          <Slider
            value={formData.sessionCountEstimate}
            onChange={(_, v) =>
              setFormData((prev) => ({ ...prev, sessionCountEstimate: v as number }))
            }
            min={CAMPAIGN_SESSION_COUNT_MIN}
            max={CAMPAIGN_SESSION_COUNT_MAX}
            step={1}
            valueLabelDisplay="auto"
            aria-label="Session Count Estimate"
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

        {/* Homebrew rules tag input */}
        <Box>
          <Typography variant="body2" gutterBottom>Homebrew Rules</Typography>
          <Box sx={{ display: "flex", gap: 1 }}>
            <TextField
              size="small"
              fullWidth
              placeholder="e.g. flanking rules, variant encumbrance"
              value={formData.homebrewInput}
              onChange={(e) => setFormData((prev) => ({ ...prev, homebrewInput: e.target.value }))}
              onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addTag("homebrewRules", "homebrewInput"); } }}
              inputProps={{ "aria-label": "Homebrew rule input" }}
              sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2 } }}
            />
            <Button variant="outlined" onClick={() => addTag("homebrewRules", "homebrewInput")} sx={{ borderRadius: 2, textTransform: "none" }}>
              Add
            </Button>
          </Box>
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, mt: 1 }}>
            {formData.homebrewRules.map((r, i) => (
              <Chip key={i} label={r} size="small" onDelete={() => removeTag("homebrewRules", i)} />
            ))}
          </Box>
        </Box>

        <TextField
          label="Inspirations (optional)"
          value={formData.inspirations}
          onChange={(e) => setFormData((prev) => ({ ...prev, inspirations: e.target.value }))}
          fullWidth
          size="small"
          multiline
          rows={2}
          placeholder="Books, films, or games that inspired the campaign..."
          inputProps={{ "aria-label": "Inspirations" }}
          sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2 } }}
        />
      </Box>
    );
  }

  function renderStep4(): React.ReactElement {
    return (
      <Box sx={{ display: "flex", flexDirection: "column", gap: 2.5, pt: 1 }}>
        <Typography variant="body2" color="text.secondary">
          Lines &amp; Veils is a safety tool for collaborative storytelling.
          <Tooltip
            title={
              <Box sx={{ p: 0.5, maxWidth: 260 }}>
                <Typography variant="caption">
                  <strong>Lines</strong> — content that will never appear in the game, even off-screen (hard limits).
                  <br /><br />
                  <strong>Veils</strong> — content that may happen but is not described in detail; it fades to black (soft limits).
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

        {/* Veils */}
        <Box>
          <Typography variant="body2" fontWeight={600} gutterBottom>Veils (fade to black)</Typography>
          <Box sx={{ display: "flex", gap: 1 }}>
            <TextField
              size="small"
              fullWidth
              placeholder="e.g. graphic torture, detailed gore"
              value={formData.veilInput}
              onChange={(e) => setFormData((prev) => ({ ...prev, veilInput: e.target.value }))}
              onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addTag("veils", "veilInput"); } }}
              inputProps={{ "aria-label": "Veil input" }}
              sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2 } }}
            />
            <Button variant="outlined" onClick={() => addTag("veils", "veilInput")} sx={{ borderRadius: 2, textTransform: "none" }}>
              Add
            </Button>
          </Box>
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, mt: 1 }}>
            {formData.veils.map((v, i) => (
              <Chip key={i} label={v} size="small" color="warning" onDelete={() => removeTag("veils", i)} />
            ))}
          </Box>
        </Box>
      </Box>
    );
  }

  function renderReview(): React.ReactElement {
    return (
      <Box sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 1 }}>
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
          <Chip label={`Name: ${formData.campaignName || "—"}`} size="small" />
          <Chip label={`Edition: ${formData.edition}`} size="small" />
          <Chip label={`Tone: ${formData.tone ? toLabel(formData.tone) : "—"}`} size="small" />
          <Chip label={`Setting: ${formData.settingPreference ? toLabel(formData.settingPreference) : "—"}`} size="small" />
          <Chip label={`Players: ${formData.playerCount}`} size="small" />
          <Chip label={`Levels: ${formData.levelStart}–${formData.levelEnd}`} size="small" />
          <Chip label={`Sessions: ~${formData.sessionCountEstimate}`} size="small" />
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
        {formData.veils.length > 0 && (
          <Box>
            <Typography variant="caption" color="text.secondary">Veils</Typography>
            <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, mt: 0.5 }}>
              {formData.veils.map((v, i) => <Chip key={i} label={v} size="small" color="warning" variant="outlined" />)}
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
      case 0: return renderStep1();
      case 1: return renderStep2();
      case 2: return renderStep3();
      case 3: return renderStep4();
      case 4: return renderReview();
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
