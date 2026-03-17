import type { GeneratedWorldResponse, WorldDetail, WorldSummary } from "@/domains/world/types";

// State shape for the World domain store.
export interface WorldState {
  /** All pre-seeded worlds fetched from GET /api/v1/worlds. */
  readonly worlds: readonly WorldSummary[];
  /** The fully loaded world detail for the currently viewed world, or null. */
  readonly selectedWorld: WorldDetail | null;
  /** The most recently LLM-generated world, or null if none has been generated. */
  readonly generatedWorld: GeneratedWorldResponse | null;
  /** True while a world list or detail request is in flight. */
  readonly isLoading: boolean;
  /** True while an LLM world generation request is in flight. */
  readonly isGenerating: boolean;
  /** Error message from the last failed request, or null if no error. */
  readonly error: string | null;
}

// Actions available on the World domain store.
export interface WorldActions {
  setWorlds: (worlds: readonly WorldSummary[]) => void;
  setSelectedWorld: (world: WorldDetail | null) => void;
  setGeneratedWorld: (world: GeneratedWorldResponse) => void;
  setGenerating: (isGenerating: boolean) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  clearWorld: () => void;
}
