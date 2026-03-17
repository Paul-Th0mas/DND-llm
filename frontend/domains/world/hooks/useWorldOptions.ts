"use client";

import { useEffect, useState } from "react";
import { getWorlds } from "@/domains/world/services/world.service";
import type { WorldSummary } from "@/domains/world/types";

interface UseWorldOptionsResult {
  readonly worlds: readonly WorldSummary[];
  readonly isLoading: boolean;
  readonly error: string | null;
}

/**
 * Fetches and caches the list of available worlds from GET /api/v1/worlds.
 * Worlds are fetched once on mount and held for the lifetime of the component.
 * Replaces the old getWorldOptions() hook — worlds are now admin-seeded, not generated.
 * @returns The worlds array, a loading flag, and an error string if the request failed.
 */
export function useWorldOptions(): UseWorldOptionsResult {
  const [worlds, setWorlds] = useState<readonly WorldSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchWorlds(): Promise<void> {
      try {
        const data = await getWorlds();
        if (!cancelled) {
          setWorlds(data);
        }
      } catch {
        if (!cancelled) {
          setError("Failed to load worlds. Please try again.");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void fetchWorlds();
    return () => {
      cancelled = true;
    };
  }, []);

  return { worlds, isLoading, error };
}
