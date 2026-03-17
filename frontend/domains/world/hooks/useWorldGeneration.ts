"use client";

import { useCallback, useState } from "react";
import { getWorldById } from "@/domains/world/services/world.service";
import { useWorldStore } from "@/domains/world/store/world.store";

interface UseWorldGenerationResult {
  readonly selectWorld: (worldId: string) => Promise<void>;
  readonly isLoading: boolean;
  readonly error: string | null;
}

/**
 * Loads the full detail of a world by ID and writes it to the world store.
 * Replaces the old LLM generation hook — worlds are now admin-seeded and fetched by ID.
 * @returns A selectWorld callback, a loading flag, and any error message.
 */
export function useWorldGeneration(): UseWorldGenerationResult {
  const { setSelectedWorld, setLoading, setError } = useWorldStore();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setLocalError] = useState<string | null>(null);

  const selectWorld = useCallback(
    async (worldId: string): Promise<void> => {
      setIsLoading(true);
      setLocalError(null);
      setLoading(true);
      setError(null);

      try {
        const world = await getWorldById(worldId);
        setSelectedWorld(world);
      } catch {
        const msg = "Failed to load world details. Please try again.";
        setLocalError(msg);
        setError(msg);
      } finally {
        setIsLoading(false);
        setLoading(false);
      }
    },
    [setSelectedWorld, setLoading, setError]
  );

  return { selectWorld, isLoading, error };
}
