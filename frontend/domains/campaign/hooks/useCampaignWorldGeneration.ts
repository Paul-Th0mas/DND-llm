"use client";

import { useCallback } from "react";
import { generateCampaignWorld } from "@/domains/campaign/services/campaign.service";
import { useCampaignStore } from "@/domains/campaign/store/campaign.store";
import { ApiError } from "@/lib/api/client";

interface UseCampaignWorldGenerationResult {
  readonly generateWorld: (campaignId: string, token: string) => Promise<void>;
  readonly isGeneratingWorld: boolean;
  readonly error: string | null;
}

/**
 * Wraps generateCampaignWorld() and writes the result to the campaign store.
 * Surfaces 404 (campaign not found) and 400 (invalid state) distinctly.
 * @returns A generateWorld callback, the current generating flag, and any error message.
 */
export function useCampaignWorldGeneration(): UseCampaignWorldGenerationResult {
  const { setCampaignWorld, setGeneratingWorld, setError, isGeneratingWorld, error } =
    useCampaignStore();

  const generateWorld = useCallback(
    async (campaignId: string, token: string): Promise<void> => {
      setGeneratingWorld(true);
      setError(null);

      try {
        // The API returns GenerateCampaignWorldResponse (summary), but the store
        // holds CampaignWorldDetailResponse. This hook will need to be updated once
        // a GET /campaigns/{id}/world endpoint returning full detail exists.
        // For now, cast the summary to the detail type until the endpoint is available.
        const response = await generateCampaignWorld(campaignId, token);
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        setCampaignWorld(response as any);
      } catch (err) {
        if (err instanceof ApiError) {
          if (err.status === 404) {
            setError("Campaign not found. It may have been deleted.");
          } else if (err.status === 400) {
            setError(`Cannot generate world: ${err.detail}`);
          } else {
            setError("World generation failed. Please try again.");
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

  return { generateWorld, isGeneratingWorld, error };
}
