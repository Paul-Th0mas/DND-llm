"use client";

import { useCallback } from "react";
import { generateWorld } from "@/domains/world/services/world.service";
import { useWorldStore } from "@/domains/world/store/world.store";
import { ApiError } from "@/lib/api/client";
import type { WorldSettingsRequest } from "@/domains/world/types";

// HTTP 429 from Gemini surfaces as a 400 with a recognisable message.
// Treat any quota-related message distinctly so the UI can show actionable feedback.
const QUOTA_PHRASES = ["quota", "rate limit", "resource exhausted"] as const;

function isQuotaError(detail: string): boolean {
  const lower = detail.toLowerCase();
  return QUOTA_PHRASES.some((phrase) => lower.includes(phrase));
}

interface UseWorldGenerationResult {
  readonly generate: (settings: WorldSettingsRequest, token: string) => Promise<void>;
  readonly isGenerating: boolean;
  readonly error: string | null;
}

/**
 * Wraps generateWorld() and writes the result directly to the world store.
 * Distinguishes quota exhaustion errors from generic failures so the UI can
 * display an actionable message rather than a generic "try again" prompt.
 * @returns A generate callback, the current generating flag, and any error message.
 */
export function useWorldGeneration(): UseWorldGenerationResult {
  const { setGeneratedWorld, setGenerating, setError, isGenerating, error } =
    useWorldStore();

  const generate = useCallback(
    async (settings: WorldSettingsRequest, token: string): Promise<void> => {
      setGenerating(true);
      setError(null);

      try {
        const world = await generateWorld(settings, token);
        setGeneratedWorld(world);
      } catch (err) {
        if (err instanceof ApiError) {
          if (isQuotaError(err.detail)) {
            setError(
              "The AI narrator is temporarily unavailable due to quota limits. Please wait a few minutes and try again."
            );
          } else if (err.status === 400) {
            setError(`World generation failed: ${err.detail}`);
          } else {
            setError("World generation failed. Please try again.");
          }
        } else {
          setError("World generation failed. Please try again.");
        }
      } finally {
        setGenerating(false);
      }
    },
    [setGeneratedWorld, setGenerating, setError]
  );

  return { generate, isGenerating, error };
}
