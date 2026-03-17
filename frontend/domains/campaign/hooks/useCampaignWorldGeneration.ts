"use client";

import { useCallback } from "react";
import { generateCampaignWorld } from "@/domains/campaign/services/campaign.service";
import { useCampaignStore } from "@/domains/campaign/store/campaign.store";
import { ApiError } from "@/lib/api/client";

interface UseCampaignWorldGenerationResult {
  readonly generate: (campaignId: string, token: string) => Promise<void>;
  readonly isGenerating: boolean;
  readonly error: string | null;
}

/**
 * Wraps generateCampaignWorld() and writes the result to the campaign store.
 * Surfaces 400 (invalid campaign) and 404 (campaign not found) distinctly.
 * @returns A generate callback, the current generating flag, and any error message.
 */
export function useCampaignWorldGeneration(): UseCampaignWorldGenerationResult {
  const { setCampaignWorld, setGeneratingWorld, setError, isGeneratingWorld, error } =
    useCampaignStore();

  const generate = useCallback(
    async (campaignId: string, token: string): Promise<void> => {
      setGeneratingWorld(true);
      setError(null);

      try {
        const world = await generateCampaignWorld(campaignId, token);
        setCampaignWorld(world);
      } catch (err) {
        if (err instanceof ApiError) {
          if (err.status === 404) {
            setError("Campaign not found.");
          } else if (err.status === 400) {
            setError(`Invalid request: ${err.detail}`);
          } else {
            setError(`World generation failed: ${err.detail}`);
          }
        } else {
          setError("World generation failed. Please try again.");
        }
      } finally {
        setGeneratingWorld(false);
      }
    },
    [setCampaignWorld, setGeneratingWorld, setError]
  );

  return { generate, isGenerating: isGeneratingWorld, error };
}
