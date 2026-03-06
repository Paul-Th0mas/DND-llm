import type { Metadata } from "next";
import { CampaignPageContent } from "./CampaignPageContent";

export const metadata: Metadata = {
  title: "Create Campaign – DnD Frontend",
  description: "Create a new DnD campaign.",
};

/**
 * Campaign creation page — entry point for the DM to create a new campaign.
 * DM-only: players are blocked at the DmOnlyRoute boundary in CampaignPageContent.
 */
export default function CampaignPage(): React.ReactElement {
  return <CampaignPageContent />;
}
