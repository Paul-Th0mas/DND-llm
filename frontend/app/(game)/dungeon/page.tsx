import type { Metadata } from "next";
import { DungeonPageContent } from "./DungeonPageContent";

export const metadata: Metadata = {
  title: "Dungeon | DnD",
  description: "Generate a dungeon for your campaign.",
};

/**
 * Dungeon view page — displays the generated dungeon for the current DM session.
 * DM-only: players are blocked at the DmOnlyRoute boundary in DungeonPageContent.
 * Content is rendered client-side from the dungeon store (no server data fetching needed).
 */
export default function DungeonPage() {
  return <DungeonPageContent />;
}
