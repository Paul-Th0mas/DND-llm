"use client";

import { useEffect, useState } from "react";
import { getWorldOptions } from "@/domains/world/services/world.service";
import type { WorldOptionsResponse } from "@/domains/world/types";

interface UseWorldOptionsResult {
  readonly options: WorldOptionsResponse | null;
  readonly isLoading: boolean;
  readonly error: string | null;
}

/**
 * Fetches and caches world generation options from GET /api/v1/worlds/options.
 * Options are fetched once on mount and held for the lifetime of the component.
 * @returns The options response, a loading flag, and an error string if the request failed.
 */
export function useWorldOptions(): UseWorldOptionsResult {
  const [options, setOptions] = useState<WorldOptionsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetch(): Promise<void> {
      try {
        const data = await getWorldOptions();
        if (!cancelled) {
          setOptions(data);
        }
      } catch {
        if (!cancelled) {
          setError("Failed to load world options. Please try again.");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void fetch();
    return () => {
      cancelled = true;
    };
  }, []);

  return { options, isLoading, error };
}
