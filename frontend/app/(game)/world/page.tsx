import type { Metadata } from "next";
import { WorldPageContent } from "./WorldPageContent";

export const metadata: Metadata = {
  title: "Generated World – DnD Frontend",
  description: "View the generated world for your campaign.",
};

/**
 * World view page — displays the generated world for the current DM session.
 * DM-only: players are blocked at the DmOnlyRoute boundary in WorldPageContent.
 * Content is rendered client-side from the world store (no server data fetching needed).
 */
export default function WorldPage(): React.ReactElement {
  return <WorldPageContent />;
}
