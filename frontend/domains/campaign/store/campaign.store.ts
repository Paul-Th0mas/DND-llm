import { create } from "zustand";
import { devtools } from "zustand/middleware";
import type { CampaignActions, CampaignState } from "./campaign.store.types";
import type { CampaignWorldDetailResponse } from "@/domains/campaign/types";

// Combined store type merging state shape and actions.
type CampaignStore = CampaignState & CampaignActions;

/**
 * Zustand store for the Campaign domain.
 * Tracks the active campaign ID, its generated world detail, and the
 * loading/error state for creation and world generation requests.
 */
export const useCampaignStore = create<CampaignStore>()(
  devtools(
    (set) => ({
      // Initial state.
      campaignId: null,
      campaignWorld: null,
      isCreating: false,
      isGeneratingWorld: false,
      error: null,

      // Actions.
      setCampaignId: (campaignId) =>
        set({ campaignId }, false, "campaign/setCampaignId"),
      setCampaignWorld: (world: CampaignWorldDetailResponse) =>
        set({ campaignWorld: world, error: null }, false, "campaign/setCampaignWorld"),
      setCreating: (isCreating) =>
        set({ isCreating }, false, "campaign/setCreating"),
      setGeneratingWorld: (isGeneratingWorld) =>
        set({ isGeneratingWorld }, false, "campaign/setGeneratingWorld"),
      setError: (error) =>
        set({ error }, false, "campaign/setError"),
      clearCampaign: () =>
        set(
          { campaignId: null, campaignWorld: null, isCreating: false, isGeneratingWorld: false, error: null },
          false,
          "campaign/clearCampaign"
        ),
    }),
    { name: "CampaignStore" }
  )
);

/**
 * Selects the campaign ID from the Campaign store.
 * @param state - The current Campaign store state.
 * @returns The active campaign ID, or null if none has been created.
 */
export const selectCampaignId = (state: CampaignStore): CampaignState["campaignId"] =>
  state.campaignId;

/**
 * Selects the campaign world detail from the Campaign store.
 * @param state - The current Campaign store state.
 * @returns The generated world detail, or null if not yet generated.
 */
export const selectCampaignWorld = (state: CampaignStore): CampaignState["campaignWorld"] =>
  state.campaignWorld;

/**
 * Selects the world-generating flag from the Campaign store.
 * @param state - The current Campaign store state.
 * @returns True if a world generation request is in flight.
 */
export const selectIsGeneratingWorld = (state: CampaignStore): CampaignState["isGeneratingWorld"] =>
  state.isGeneratingWorld;
