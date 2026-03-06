import type { Metadata } from "next";
import { CampaignWorldPageContent } from "./CampaignWorldPageContent";

export const metadata: Metadata = {
  title: "Campaign World – DnD Frontend",
  description: "View or generate the world for this campaign.",
};

/**
 * Campaign world view page — shows the generated world for a specific campaign.
 * DM-only: players are blocked at the DmOnlyRoute boundary in CampaignWorldPageContent.
 */
export default function CampaignWorldPage(): React.ReactElement {
  return <CampaignWorldPageContent />;
}
