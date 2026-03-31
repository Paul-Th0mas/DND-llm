import { create } from "zustand";
import { devtools } from "zustand/middleware";
import type { CharacterActions, CharacterState } from "./character.store.types";
import type { CharacterSummary, CharacterWizardState } from "@/domains/character/types";

// Combined store type merging state shape and actions.
type CharacterStore = CharacterState & CharacterActions;

/** Initial wizard state — all fields blank, starting at step 0. */
const INITIAL_WIZARD: CharacterWizardState = {
  step: 0,
  name: "",
  background: "",
  selectedClassId: null,
  selectedSpeciesId: null,
  abilityScores: null,
  scoreMethod: "standard_array",
};

/**
 * Zustand store for the Character domain.
 * Manages the authenticated user's character list and the character creation
 * wizard state so navigating between wizard steps does not clear entered data.
 */
export const useCharacterStore = create<CharacterStore>()(
  devtools(
    (set) => ({
      // Initial state.
      myCharacters: null,
      wizard: INITIAL_WIZARD,

      // -----------------------------------------------------------------------
      // Character list actions
      // -----------------------------------------------------------------------

      setMyCharacters: (characters: readonly CharacterSummary[]) =>
        set({ myCharacters: characters }, false, "character/setMyCharacters"),

      clearMyCharacters: () =>
        set({ myCharacters: null }, false, "character/clearMyCharacters"),

      // -----------------------------------------------------------------------
      // Wizard actions
      // -----------------------------------------------------------------------

      setWizardStep: (step) =>
        set(
          (state) => ({ wizard: { ...state.wizard, step } }),
          false,
          "character/setWizardStep"
        ),

      setWizardName: (name) =>
        set(
          (state) => ({ wizard: { ...state.wizard, name } }),
          false,
          "character/setWizardName"
        ),

      setWizardBackground: (background) =>
        set(
          (state) => ({ wizard: { ...state.wizard, background } }),
          false,
          "character/setWizardBackground"
        ),

      setWizardClassId: (selectedClassId) =>
        set(
          (state) => ({ wizard: { ...state.wizard, selectedClassId } }),
          false,
          "character/setWizardClassId"
        ),

      setWizardSpeciesId: (selectedSpeciesId) =>
        set(
          (state) => ({ wizard: { ...state.wizard, selectedSpeciesId } }),
          false,
          "character/setWizardSpeciesId"
        ),

      setWizardAbilityScores: (abilityScores) =>
        set(
          (state) => ({ wizard: { ...state.wizard, abilityScores } }),
          false,
          "character/setWizardAbilityScores"
        ),

      setWizardScoreMethod: (scoreMethod) =>
        set(
          (state) => ({ wizard: { ...state.wizard, scoreMethod } }),
          false,
          "character/setWizardScoreMethod"
        ),

      resetWizard: () =>
        set({ wizard: INITIAL_WIZARD }, false, "character/resetWizard"),
    }),
    { name: "CharacterStore" }
  )
);

// ---------------------------------------------------------------------------
// Selectors
// ---------------------------------------------------------------------------

/**
 * Selects the authenticated user's character list.
 * @param state - The current Character store state.
 * @returns The characters array, or null if not yet fetched.
 */
export const selectMyCharacters = (
  state: CharacterStore
): CharacterState["myCharacters"] => state.myCharacters;

/**
 * Selects the wizard state from the Character store.
 * @param state - The current Character store state.
 * @returns The wizard state object.
 */
export const selectWizard = (
  state: CharacterStore
): CharacterState["wizard"] => state.wizard;
