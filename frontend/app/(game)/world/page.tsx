import type { Metadata } from "next";
import { WorldPageContent } from "./WorldPageContent";

export const metadata: Metadata = {
  title: "Browse Worlds – Dungeons and Droids",
  description: "Browse pre-seeded worlds and begin creating your character.",
};

/**
 * World browse page — lists all pre-seeded worlds so any authenticated user
 * can explore them and navigate to character creation.
 */
export default function WorldPage(): React.ReactElement {
  return <WorldPageContent />;
}
