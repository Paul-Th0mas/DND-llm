import { create } from "zustand";
import { devtools } from "zustand/middleware";
import type { WorldActions, WorldState } from "./world.store.types";

// Combined store type merging state shape and actions.
type WorldStore = WorldState & WorldActions;

/**
 * Zustand store for the World domain.
 * Holds the most recently generated world and the loading/error state
 * for the generation request. Persists for the lifetime of the browser session.
 */
export const useWorldStore = create<WorldStore>()(
  devtools(
    (set) => ({
      // Initial state.
      generatedWorld: null,
      isGenerating: false,
      error: null,

      // Actions.
      setGeneratedWorld: (world) =>
        set({ generatedWorld: world, error: null }, false, "world/setGeneratedWorld"),
      setGenerating: (isGenerating) =>
        set({ isGenerating }, false, "world/setGenerating"),
      setError: (error) =>
        set({ error }, false, "world/setError"),
      clearWorld: () =>
        set({ generatedWorld: null, error: null, isGenerating: false }, false, "world/clearWorld"),
    }),
    { name: "WorldStore" }
  )
);

/**
 * Selects the generated world from the World store.
 * @param state - The current World store state.
 * @returns The generated world, or null if none has been generated.
 */
export const selectGeneratedWorld = (state: WorldStore): WorldState["generatedWorld"] =>
  state.generatedWorld;

/**
 * Selects the generating flag from the World store.
 * @param state - The current World store state.
 * @returns True if a generation request is in flight.
 */
export const selectIsGenerating = (state: WorldStore): WorldState["isGenerating"] =>
  state.isGenerating;
