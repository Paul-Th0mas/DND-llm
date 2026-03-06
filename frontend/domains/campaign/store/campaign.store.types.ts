import type { CampaignWorldDetailResponse } from "@/domains/campaign/types";

// State shape for the Campaign domain store.
export interface CampaignState {
  /** The ID of the most recently created campaign, or null if none exists. */
  readonly campaignId: string | null;
  /** The fully generated campaign world detail, or null if not yet generated. */
  readonly campaignWorld: CampaignWorldDetailResponse | null;
  /** True while a campaign creation request is in flight. */
  readonly isCreating: boolean;
  /** True while a campaign world generation request is in flight. */
  readonly isGeneratingWorld: boolean;
  /** Error message from the last failed request, or null if no error. */
  readonly error: string | null;
}

// Actions available on the Campaign domain store.
export interface CampaignActions {
  setCampaignId: (campaignId: string) => void;
  setCampaignWorld: (world: CampaignWorldDetailResponse) => void;
  setCreating: (isCreating: boolean) => void;
  setGeneratingWorld: (isGeneratingWorld: boolean) => void;
  setError: (error: string | null) => void;
  clearCampaign: () => void;
}
