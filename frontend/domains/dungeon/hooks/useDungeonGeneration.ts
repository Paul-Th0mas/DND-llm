"use client";

import { useCallback } from "react";
import { generateDungeon } from "../services/dungeon.service";
import { useDungeonStore } from "../store/dungeon.store";
import { ApiError } from "@/lib/api/client";
import type { GenerateDungeonRequest, DungeonCreatedResponse } from "../types";

// HTTP 429 from Gemini surfaces as a 400 with a recognisable message.
// Treat any quota-related message distinctly so the UI can show actionable feedback.
const QUOTA_PHRASES = ["quota", "rate limit", "resource exhausted"] as const;

function isQuotaError(detail: string): boolean {
  const lower = detail.toLowerCase();
  return QUOTA_PHRASES.some((phrase) => lower.includes(phrase));
}

interface UseDungeonGenerationResult {
  readonly generate: (
    campaignId: string,
    request: GenerateDungeonRequest,
    token: string
  ) => Promise<DungeonCreatedResponse | null>;
  readonly isGenerating: boolean;
  readonly error: string | null;
}

/**
 * Wraps generateDungeon() for a campaign-scoped dungeon generation request.
 * Manages the isGenerating and error flags in the dungeon store.
 * Returns the DungeonCreatedResponse on success so the caller can redirect.
 * @returns A generate callback, the current generating flag, and any error message.
 */
export function useDungeonGeneration(): UseDungeonGenerationResult {
  const { setGenerating, setError, isGenerating, error } = useDungeonStore();

  const generate = useCallback(
    async (
      campaignId: string,
      request: GenerateDungeonRequest,
      token: string
    ): Promise<DungeonCreatedResponse | null> => {
      setGenerating(true);
      setError(null);

      try {
        const result = await generateDungeon(campaignId, request, token);
        return result;
      } catch (err) {
        if (err instanceof ApiError) {
          if (isQuotaError(err.detail)) {
            setError(
              "The AI narrator is temporarily unavailable due to quota limits. Please wait a few minutes and try again."
            );
          } else if (err.status === 400) {
            setError(`Dungeon generation failed: ${err.detail}`);
          } else {
            setError("Dungeon generation failed. Please try again.");
          }
        } else {
          setError("Dungeon generation failed. Please try again.");
        }
        return null;
      } finally {
        setGenerating(false);
      }
    },
    [setGenerating, setError]
  );

  return { generate, isGenerating, error };
}
