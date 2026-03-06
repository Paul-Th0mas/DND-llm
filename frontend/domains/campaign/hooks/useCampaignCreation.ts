"use client";

import { useCallback } from "react";
import { createCampaign } from "@/domains/campaign/services/campaign.service";
import { useCampaignStore } from "@/domains/campaign/store/campaign.store";
import { ApiError } from "@/lib/api/client";
import type { CreateCampaignRequest } from "@/domains/campaign/types";

interface UseCampaignCreationResult {
  readonly create: (request: CreateCampaignRequest, token: string) => Promise<void>;
  readonly isCreating: boolean;
  readonly error: string | null;
}

/**
 * Wraps createCampaign() and writes the returned campaign ID to the campaign store.
 * Surfaces 400 (invalid campaign data) distinctly from generic network failures.
 * @returns A create callback, the current creating flag, and any error message.
 */
export function useCampaignCreation(): UseCampaignCreationResult {
  const { setCampaignId, setCreating, setError, isCreating, error } =
    useCampaignStore();

  const create = useCallback(
    async (request: CreateCampaignRequest, token: string): Promise<void> => {
      setCreating(true);
      setError(null);

      try {
        const response = await createCampaign(request, token);
        setCampaignId(response.campaign_id);
      } catch (err) {
        if (err instanceof ApiError && err.status === 400) {
          setError(`Invalid campaign data: ${err.detail}`);
        } else {
          setError("Campaign creation failed. Please try again.");
        }
      } finally {
        setCreating(false);
      }
    },
    [setCampaignId, setCreating, setError]
  );

  return { create, isCreating, error };
}
