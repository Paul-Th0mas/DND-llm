import type { DungeonDetail } from "../types";

// State shape for the Dungeon domain store.
export interface DungeonState {
  /** The currently viewed dungeon detail, or null if none has been loaded. */
  readonly activeDungeon: DungeonDetail | null;
  /** True while a dungeon detail fetch request is in flight. */
  readonly isLoadingDungeon: boolean;
  /** True while a dungeon generation request is in flight. */
  readonly isGenerating: boolean;
  /** Error message from the last failed operation, or null if no error. */
  readonly error: string | null;
}

// Actions available on the Dungeon domain store.
export interface DungeonActions {
  /**
   * Sets the active dungeon detail after a successful fetch.
   * @param dungeon - The full dungeon detail to store.
   */
  setActiveDungeon: (dungeon: DungeonDetail) => void;
  /**
   * Updates the dungeon detail loading flag.
   * @param loading - True when a fetch is in flight.
   */
  setLoadingDungeon: (loading: boolean) => void;
  /**
   * Updates the dungeon generation in-flight flag.
   * @param generating - True when generation is in progress.
   */
  setGenerating: (generating: boolean) => void;
  /**
   * Sets the error message for the last failed operation.
   * @param error - The error string, or null to clear.
   */
  setError: (error: string | null) => void;
  /** Clears all dungeon state (active dungeon, loading, error). */
  clearDungeon: () => void;
  /**
   * Updates the current_room_index on the active dungeon (US-069).
   * Called when a room_advanced WebSocket event is received.
   * @param index - The new room index.
   */
  setCurrentRoomIndex: (index: number) => void;
  /**
   * Appends a completed stage index to the active dungeon (US-069).
   * Called when a quest_stage_advanced WebSocket event is received.
   * @param stageIndex - The index of the completed quest stage.
   */
  markQuestStageComplete: (stageIndex: number) => void;
}
