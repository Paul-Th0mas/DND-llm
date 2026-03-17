"use client";

import { useCallback, useEffect, useState } from "react";
import { getCampaigns } from "@/domains/campaign/services/campaign.service";
import {
  selectCampaigns,
  useCampaignStore,
} from "@/domains/campaign/store/campaign.store";
import type { CampaignSummary } from "@/domains/campaign/types";
import { ApiError } from "@/lib/api/client";

interface UseCampaignListResult {
  readonly campaigns: readonly CampaignSummary[];
  readonly isLoading: boolean;
  readonly error: string | null;
  readonly reload: () => void;
}

/**
 * Fetches the campaign list for the authenticated DM and writes it to the campaign store.
 * Re-fetches whenever reload() is called.
 * @param token - The JWT access token of the authenticated DM.
 * @returns The campaigns array from the store, a loading flag, an error string, and a reload callback.
 */
export function useCampaignList(token: string): UseCampaignListResult {
  const { setCampaigns, setLoadingCampaigns } = useCampaignStore();
  const campaigns = useCampaignStore(selectCampaigns);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reloadCounter, setReloadCounter] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function fetchCampaigns(): Promise<void> {
      if (!token) return;

      setIsLoading(true);
      setLoadingCampaigns(true);
      setError(null);

      try {
        const result = await getCampaigns(token);
        if (!cancelled) {
          setCampaigns(result);
        }
      } catch (err) {
        if (!cancelled) {
          if (err instanceof ApiError) {
            setError(`Failed to load campaigns: ${err.detail}`);
          } else {
            setError("Failed to load campaigns. Please try again.");
          }
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
          setLoadingCampaigns(false);
        }
      }
    }

    void fetchCampaigns();

    return () => {
      cancelled = true;
    };
  }, [token, reloadCounter, setCampaigns, setLoadingCampaigns]);

  const reload = useCallback(() => {
    setReloadCounter((prev) => prev + 1);
  }, []);

  return { campaigns, isLoading, error, reload };
}
