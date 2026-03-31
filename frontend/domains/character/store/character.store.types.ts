import type {
  CharacterSummary,
  CharacterWizardState,
} from "@/domains/character/types";

/**
 * State shape for the Character domain store.
 * Holds the player's character list and the in-progress wizard state.
 */
export interface CharacterState {
  /**
   * Characters owned by the authenticated user.
   * Populated by the "My Characters" dashboard tab (US-047).
   * Null means the data has not been fetched yet (distinct from an empty array).
   */
  readonly myCharacters: readonly CharacterSummary[] | null;

  /** Wizard state persisted across step navigation (US-028). */
  readonly wizard: CharacterWizardState;
}

/**
 * Actions available on the Character domain store.
 */
export interface CharacterActions {
  /** Sets the list of the authenticated user's characters. */
  setMyCharacters: (characters: readonly CharacterSummary[]) => void;
  /** Clears the cached character list (e.g. on logout). */
  clearMyCharacters: () => void;

  // Wizard actions — each updates a single field without clearing others
  // so navigating back between steps preserves entered data.
  setWizardStep: (step: number) => void;
  setWizardName: (name: string) => void;
  setWizardBackground: (background: string) => void;
  setWizardClassId: (classId: string | null) => void;
  setWizardSpeciesId: (speciesId: string | null) => void;
  setWizardAbilityScores: (
    scores: CharacterWizardState["abilityScores"]
  ) => void;
  setWizardScoreMethod: (method: CharacterWizardState["scoreMethod"]) => void;
  /** Resets the entire wizard to its initial state. */
  resetWizard: () => void;
}
