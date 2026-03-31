"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import Step from "@mui/material/Step";
import StepLabel from "@mui/material/StepLabel";
import Stepper from "@mui/material/Stepper";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { AbilityScoreStep } from "./AbilityScoreStep";
import { ClassSelectionGrid } from "./ClassSelectionGrid";
import { SpeciesSelectionGrid } from "./SpeciesSelectionGrid";
import { createCharacter } from "@/domains/character/services/character.service";
import {
  useCharacterStore,
  selectWizard,
} from "@/domains/character/store/character.store";
import { ApiError } from "@/lib/api/client";
import type { AbilityScores } from "@/domains/character/types";

const STEP_LABELS = [
  "Name & Background",
  "Choose Class",
  "Choose Species",
  "Ability Scores",
] as const;

/** Props for CreateCharacterWizard. */
export interface CreateCharacterWizardProps {
  /** The UUID of the world this character will belong to. */
  readonly worldId: string;
  /** The world theme string used to filter class/species options. */
  readonly worldTheme: string;
  /** The JWT access token of the authenticated user. */
  readonly token: string;
}

/**
 * Multi-step character creation wizard implementing US-028.
 * Steps: 0 = Name + Background, 1 = Class, 2 = Species, 3 = Ability Scores.
 * Wizard state is stored in the character Zustand store so navigating back
 * between steps does not clear entered data.
 * On success, navigates to the character sheet at /world/{worldId}/character/{id}.
 */
export function CreateCharacterWizard({
  worldId,
  worldTheme,
  token,
}: CreateCharacterWizardProps): React.ReactElement {
  const router = useRouter();
  const wizard = useCharacterStore(selectWizard);
  const {
    setWizardStep,
    setWizardName,
    setWizardBackground,
    setWizardClassId,
    setWizardSpeciesId,
    setWizardAbilityScores,
    setWizardScoreMethod,
    resetWizard,
  } = useCharacterStore();

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // ---------------------------------------------------------------------------
  // Navigation helpers
  // ---------------------------------------------------------------------------

  function goBack(): void {
    if (wizard.step > 0) setWizardStep(wizard.step - 1);
  }

  function goNext(): void {
    if (wizard.step < STEP_LABELS.length - 1) setWizardStep(wizard.step + 1);
  }

  // ---------------------------------------------------------------------------
  // Per-step validation
  // ---------------------------------------------------------------------------

  function isStepValid(): boolean {
    switch (wizard.step) {
      case 0:
        return wizard.name.trim().length > 0 && wizard.name.trim().length <= 100;
      case 1:
        return wizard.selectedClassId !== null;
      case 2:
        return wizard.selectedSpeciesId !== null;
      case 3:
        return wizard.abilityScores !== null;
      default:
        return false;
    }
  }

  // ---------------------------------------------------------------------------
  // Submit
  // ---------------------------------------------------------------------------

  async function handleSubmit(): Promise<void> {
    if (
      wizard.selectedClassId === null ||
      wizard.selectedSpeciesId === null ||
      wizard.abilityScores === null
    ) {
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const created = await createCharacter(
        {
          name: wizard.name.trim(),
          class_id: wizard.selectedClassId,
          species_id: wizard.selectedSpeciesId,
          world_id: worldId,
          ability_scores: wizard.abilityScores,
          background: wizard.background.trim(),
        },
        token
      );
      // Reset wizard state on success so a fresh wizard starts clean next time.
      resetWizard();
      router.push(`/world/${worldId}/character/${created.id}`);
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        if (err.status === 422) {
          setSubmitError(`Validation error: ${err.detail}`);
        } else if (err.status === 500) {
          setSubmitError(
            "A server error occurred. Your progress has been saved — please try again."
          );
        } else {
          setSubmitError(`Failed to create character: ${err.detail}`);
        }
      } else {
        setSubmitError("Failed to create character. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  const isLastStep = wizard.step === STEP_LABELS.length - 1;

  return (
    <Box sx={{ maxWidth: 720, mx: "auto" }}>
      {/* Stepper */}
      <Stepper activeStep={wizard.step} sx={{ mb: 4 }}>
        {STEP_LABELS.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {/* Step content */}
      <Box sx={{ mb: 4 }}>
        {wizard.step === 0 && (
          <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
            <Typography variant="h6" fontWeight={700} sx={{ color: "#1e1410" }}>
              Name your character
            </Typography>
            <TextField
              label="Character Name"
              value={wizard.name}
              onChange={(e) => setWizardName(e.target.value)}
              inputProps={{ maxLength: 100 }}
              fullWidth
              required
              helperText={`${wizard.name.length}/100`}
              error={wizard.name.trim().length === 0 && wizard.name.length > 0}
            />
            <TextField
              label="Background"
              value={wizard.background}
              onChange={(e) => setWizardBackground(e.target.value)}
              inputProps={{ maxLength: 500 }}
              fullWidth
              multiline
              minRows={4}
              helperText={`${wizard.background.length}/500 characters (optional)`}
            />
          </Box>
        )}

        {wizard.step === 1 && (
          <Box>
            <Typography variant="h6" fontWeight={700} sx={{ color: "#1e1410", mb: 2 }}>
              Choose your class
            </Typography>
            <ClassSelectionGrid
              worldTheme={worldTheme}
              selectedClassId={wizard.selectedClassId}
              onSelect={setWizardClassId}
            />
          </Box>
        )}

        {wizard.step === 2 && (
          <Box>
            <Typography variant="h6" fontWeight={700} sx={{ color: "#1e1410", mb: 2 }}>
              Choose your species
            </Typography>
            <SpeciesSelectionGrid
              worldTheme={worldTheme}
              selectedSpeciesId={wizard.selectedSpeciesId}
              onSelect={setWizardSpeciesId}
            />
          </Box>
        )}

        {wizard.step === 3 && (
          <Box>
            <Typography variant="h6" fontWeight={700} sx={{ color: "#1e1410", mb: 2 }}>
              Assign ability scores
            </Typography>
            <AbilityScoreStep
              scoreMethod={wizard.scoreMethod}
              abilityScores={wizard.abilityScores}
              onMethodChange={setWizardScoreMethod}
              onScoresChange={(scores: AbilityScores | null) =>
                setWizardAbilityScores(scores)
              }
            />
          </Box>
        )}
      </Box>

      {/* Submit error banner — preserved across retries (AC6) */}
      {submitError !== null && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {submitError}
        </Alert>
      )}

      {/* Navigation buttons */}
      <Box sx={{ display: "flex", justifyContent: "space-between" }}>
        <Button
          variant="outlined"
          onClick={goBack}
          disabled={wizard.step === 0 || isSubmitting}
          sx={{ textTransform: "none" }}
        >
          Back
        </Button>

        {isLastStep ? (
          <Button
            variant="contained"
            onClick={() => void handleSubmit()}
            disabled={!isStepValid() || isSubmitting}
            sx={{
              textTransform: "none",
              bgcolor: "#7d5e45",
              "&:hover": { bgcolor: "#5c4230" },
            }}
          >
            {isSubmitting ? (
              <CircularProgress size={20} sx={{ color: "#F9F8F6" }} />
            ) : (
              "Finish"
            )}
          </Button>
        ) : (
          <Button
            variant="contained"
            onClick={goNext}
            disabled={!isStepValid()}
            sx={{
              textTransform: "none",
              bgcolor: "#a07d60",
              "&:hover": { bgcolor: "#7d5e45" },
            }}
          >
            Next
          </Button>
        )}
      </Box>
    </Box>
  );
}
