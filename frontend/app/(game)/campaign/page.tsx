import { redirect } from "next/navigation";

/**
 * Campaigns are now displayed inline on the dashboard Campaigns tab.
 * Redirect any direct visits to /campaign back to the dashboard.
 */
export default function CampaignPage(): never {
  redirect("/dashboard");
}
