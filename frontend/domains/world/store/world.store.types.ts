import type { GeneratedWorldResponse } from "@/domains/world/types";

// State shape for the World domain store.
export interface WorldState {
  /** The most recently generated world, or null if none has been generated this session. */
  readonly generatedWorld: GeneratedWorldResponse | null;
  /** True while a world generation request is in flight. */
  readonly isGenerating: boolean;
  /** Error message from the last failed generation attempt, or null if no error. */
  readonly error: string | null;
}

// Actions available on the World domain store.
export interface WorldActions {
  setGeneratedWorld: (world: GeneratedWorldResponse) => void;
  setGenerating: (isGenerating: boolean) => void;
  setError: (error: string | null) => void;
  clearWorld: () => void;
}
