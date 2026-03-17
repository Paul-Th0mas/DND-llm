import { create } from "zustand";
import { devtools } from "zustand/middleware";
import type { WorldActions, WorldState } from "./world.store.types";
import type { GeneratedWorldResponse } from "@/domains/world/types";

// Combined store type merging state shape and actions.
type WorldStore = WorldState & WorldActions;

/**
 * Zustand store for the World domain.
 * Holds the list of pre-seeded worlds, the currently selected world detail,
 * the most recently generated world, and the loading/error state for API requests.
 */
export const useWorldStore = create<WorldStore>()(
  devtools(
    (set) => ({
      // Initial state.
      worlds: [],
      selectedWorld: null,
      generatedWorld: null,
      isLoading: false,
      isGenerating: false,
      error: null,

      // Actions.
      setWorlds: (worlds) =>
        set({ worlds }, false, "world/setWorlds"),
      setSelectedWorld: (world) =>
        set({ selectedWorld: world }, false, "world/setSelectedWorld"),
      setGeneratedWorld: (world) =>
        set({ generatedWorld: world }, false, "world/setGeneratedWorld"),
      setGenerating: (isGenerating) =>
        set({ isGenerating }, false, "world/setGenerating"),
      setLoading: (isLoading) =>
        set({ isLoading }, false, "world/setLoading"),
      setError: (error) =>
        set({ error }, false, "world/setError"),
      clearWorld: () =>
        set(
          {
            worlds: [],
            selectedWorld: null,
            generatedWorld: null,
            isLoading: false,
            isGenerating: false,
            error: null,
          },
          false,
          "world/clearWorld"
        ),
    }),
    { name: "WorldStore" }
  )
);

/**
 * Selects the worlds list from the World store.
 * @param state - The current World store state.
 * @returns The array of world summaries.
 */
export const selectWorlds = (state: WorldStore): WorldState["worlds"] =>
  state.worlds;

/**
 * Selects the currently selected world detail from the World store.
 * @param state - The current World store state.
 * @returns The selected world detail, or null if none is selected.
 */
export const selectSelectedWorld = (state: WorldStore): WorldState["selectedWorld"] =>
  state.selectedWorld;

/**
 * Selects the most recently generated world from the World store.
 * @param state - The current World store state.
 * @returns The generated world, or null if none exists.
 */
export const selectGeneratedWorld = (state: WorldStore): GeneratedWorldResponse | null =>
  state.generatedWorld;

/**
 * Selects the loading flag from the World store.
 * @param state - The current World store state.
 * @returns True if a world request is in flight.
 */
export const selectWorldIsLoading = (state: WorldStore): WorldState["isLoading"] =>
  state.isLoading;

/**
 * Selects the generating flag from the World store.
 * @param state - The current World store state.
 * @returns True if an LLM world generation request is in flight.
 */
export const selectIsGenerating = (state: WorldStore): WorldState["isGenerating"] =>
  state.isGenerating;
