import { create } from "zustand";
import { devtools } from "zustand/middleware";
import type { CampaignActions, CampaignState } from "./campaign.store.types";
import type { CampaignWorldDetailResponse } from "@/domains/campaign/types";

// Combined store type merging state shape and actions.
type CampaignStore = CampaignState & CampaignActions;

/**
 * Zustand store for the Campaign domain.
 * Tracks the active campaign ID, campaign list, active campaign detail,
 * the generated campaign world, and the loading/error state for all requests.
 */
export const useCampaignStore = create<CampaignStore>()(
  devtools(
    (set) => ({
      // Initial state.
      campaignId: null,
      campaigns: [],
      activeCampaign: null,
      campaignWorld: null,
      isCreating: false,
      isLoadingCampaigns: false,
      isGeneratingWorld: false,
      error: null,

      // Actions.
      setCampaignId: (campaignId) =>
        set({ campaignId }, false, "campaign/setCampaignId"),
      setCampaigns: (campaigns) =>
        set({ campaigns, error: null }, false, "campaign/setCampaigns"),
      setActiveCampaign: (activeCampaign) =>
        set({ activeCampaign, error: null }, false, "campaign/setActiveCampaign"),
      setCampaignWorld: (campaignWorld) =>
        set({ campaignWorld, error: null }, false, "campaign/setCampaignWorld"),
      setCreating: (isCreating) =>
        set({ isCreating }, false, "campaign/setCreating"),
      setLoadingCampaigns: (isLoadingCampaigns) =>
        set({ isLoadingCampaigns }, false, "campaign/setLoadingCampaigns"),
      setGeneratingWorld: (isGeneratingWorld) =>
        set({ isGeneratingWorld }, false, "campaign/setGeneratingWorld"),
      setError: (error) =>
        set({ error }, false, "campaign/setError"),
      clearCampaign: () =>
        set(
          {
            campaignId: null,
            campaigns: [],
            activeCampaign: null,
            campaignWorld: null,
            isCreating: false,
            isLoadingCampaigns: false,
            isGeneratingWorld: false,
            error: null,
          },
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
 * Selects the campaigns list from the Campaign store.
 * @param state - The current Campaign store state.
 * @returns The list of campaign summaries.
 */
export const selectCampaigns = (state: CampaignStore): CampaignState["campaigns"] =>
  state.campaigns;

/**
 * Selects the active campaign detail from the Campaign store.
 * @param state - The current Campaign store state.
 * @returns The active campaign detail, or null if not yet loaded.
 */
export const selectActiveCampaign = (state: CampaignStore): CampaignState["activeCampaign"] =>
  state.activeCampaign;

/**
 * Selects the generated campaign world from the Campaign store.
 * @param state - The current Campaign store state.
 * @returns The generated campaign world, or null if not yet generated.
 */
export const selectCampaignWorld = (state: CampaignStore): CampaignWorldDetailResponse | null =>
  state.campaignWorld;

/**
 * Selects the campaigns-loading flag from the Campaign store.
 * @param state - The current Campaign store state.
 * @returns True if a campaigns list request is in flight.
 */
export const selectIsLoadingCampaigns = (state: CampaignStore): CampaignState["isLoadingCampaigns"] =>
  state.isLoadingCampaigns;

/**
 * Selects the world-generating flag from the Campaign store.
 * @param state - The current Campaign store state.
 * @returns True if a campaign world generation request is in flight.
 */
export const selectIsGeneratingWorld = (state: CampaignStore): CampaignState["isGeneratingWorld"] =>
  state.isGeneratingWorld;
