import type { Metadata } from "next";
import { CampaignDetailPageContent } from "./CampaignDetailPageContent";

export const metadata: Metadata = {
  title: "Campaign Detail | DnD",
  description: "View and manage your campaign.",
};

/** Props for the CampaignDetailPage route. */
interface CampaignDetailPageProps {
  readonly params: Promise<{ readonly campaignId: string }>;
}

/**
 * Dynamic route page for a single campaign detail view.
 * Passes the campaignId param to CampaignDetailPageContent for data fetching.
 */
export default async function CampaignDetailPage({
  params,
}: CampaignDetailPageProps): Promise<React.ReactElement> {
  const { campaignId } = await params;
  return <CampaignDetailPageContent campaignId={campaignId} />;
}
