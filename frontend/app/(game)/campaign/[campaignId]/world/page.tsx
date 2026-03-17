import type { Metadata } from "next";
import { CampaignWorldPageContent } from "./CampaignWorldPageContent";

export const metadata: Metadata = {
  title: "Campaign World – DnD Frontend",
  description: "View the world for this campaign.",
};

/** Route params provided by Next.js for the [campaignId] dynamic segment. */
interface CampaignWorldPageProps {
  readonly params: Promise<{ campaignId: string }>;
}

/**
 * Campaign world view page — shows the world detail for a specific campaign.
 * DM-only: players are blocked at the DmOnlyRoute boundary in CampaignWorldPageContent.
 */
export default async function CampaignWorldPage({
  params,
}: CampaignWorldPageProps): Promise<React.ReactElement> {
  const { campaignId } = await params;
  return <CampaignWorldPageContent campaignId={campaignId} />;
}
