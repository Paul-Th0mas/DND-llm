import type {
  CampaignDetail,
  CampaignSummary,
  CampaignWorldDetailResponse,
} from "@/domains/campaign/types";

// State shape for the Campaign domain store.
export interface CampaignState {
  /** The ID of the most recently created campaign, or null if none exists. */
  readonly campaignId: string | null;
  /** The list of campaigns fetched from the API. */
  readonly campaigns: readonly CampaignSummary[];
  /** The fully loaded campaign detail, or null if not yet fetched. */
  readonly activeCampaign: CampaignDetail | null;
  /** The LLM-generated campaign world detail, or null if not yet generated. */
  readonly campaignWorld: CampaignWorldDetailResponse | null;
  /** True while a campaign creation request is in flight. */
  readonly isCreating: boolean;
  /** True while the campaigns list is being fetched. */
  readonly isLoadingCampaigns: boolean;
  /** True while a campaign world generation request is in flight. */
  readonly isGeneratingWorld: boolean;
  /** Error message from the last failed request, or null if no error. */
  readonly error: string | null;
}

// Actions available on the Campaign domain store.
export interface CampaignActions {
  setCampaignId: (campaignId: string) => void;
  setCampaigns: (campaigns: readonly CampaignSummary[]) => void;
  setActiveCampaign: (campaign: CampaignDetail | null) => void;
  setCampaignWorld: (world: CampaignWorldDetailResponse) => void;
  setCreating: (isCreating: boolean) => void;
  setLoadingCampaigns: (isLoading: boolean) => void;
  setGeneratingWorld: (isGenerating: boolean) => void;
  setError: (error: string | null) => void;
  clearCampaign: () => void;
}
