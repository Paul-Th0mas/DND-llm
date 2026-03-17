import { create } from "zustand";
import { devtools } from "zustand/middleware";
import type { DungeonActions, DungeonState } from "./dungeon.store.types";
import type { DungeonDetail } from "../types";

// Combined store type merging state shape and actions.
type DungeonStore = DungeonState & DungeonActions;

/**
 * Zustand store for the Dungeon domain.
 * Holds the currently viewed dungeon detail and the loading/error state
 * for fetch and generation operations.
 */
export const useDungeonStore = create<DungeonStore>()(
  devtools(
    (set) => ({
      // Initial state.
      activeDungeon: null,
      isLoadingDungeon: false,
      isGenerating: false,
      error: null,

      // Actions.
      setActiveDungeon: (dungeon: DungeonDetail) =>
        set(
          { activeDungeon: dungeon, error: null },
          false,
          "dungeon/setActiveDungeon"
        ),

      setLoadingDungeon: (loading: boolean) =>
        set({ isLoadingDungeon: loading }, false, "dungeon/setLoadingDungeon"),

      setGenerating: (generating: boolean) =>
        set({ isGenerating: generating }, false, "dungeon/setGenerating"),

      setError: (error: string | null) =>
        set({ error }, false, "dungeon/setError"),

      clearDungeon: () =>
        set(
          {
            activeDungeon: null,
            isLoadingDungeon: false,
            isGenerating: false,
            error: null,
          },
          false,
          "dungeon/clearDungeon"
        ),
    }),
    { name: "DungeonStore" }
  )
);

/**
 * Selects the active dungeon detail from the Dungeon store.
 * @param state - The current Dungeon store state.
 * @returns The active dungeon detail, or null if not yet loaded.
 */
export const selectActiveDungeon = (
  state: DungeonStore
): DungeonState["activeDungeon"] => state.activeDungeon;

/**
 * Selects the dungeon loading flag from the Dungeon store.
 * @param state - The current Dungeon store state.
 * @returns True if a dungeon detail fetch is in flight.
 */
export const selectIsLoadingDungeon = (
  state: DungeonStore
): DungeonState["isLoadingDungeon"] => state.isLoadingDungeon;

/**
 * Selects the generating flag from the Dungeon store.
 * @param state - The current Dungeon store state.
 * @returns True if a dungeon generation request is in flight.
 */
export const selectIsGenerating = (
  state: DungeonStore
): DungeonState["isGenerating"] => state.isGenerating;
