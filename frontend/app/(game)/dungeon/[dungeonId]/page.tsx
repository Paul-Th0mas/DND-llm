import type { Metadata } from "next";
import { DungeonDetailPageContent } from "./DungeonDetailPageContent";

export const metadata: Metadata = {
  title: "Dungeon Detail | DnD",
  description: "View the full details of a generated dungeon.",
};

/** Props for the DungeonDetailPage route. */
interface DungeonDetailPageProps {
  readonly params: Promise<{ readonly dungeonId: string }>;
}

/**
 * Dynamic route page for a single dungeon detail view.
 * Passes the dungeonId param to DungeonDetailPageContent for data fetching.
 */
export default async function DungeonDetailPage({
  params,
}: DungeonDetailPageProps): Promise<React.ReactElement> {
  const { dungeonId } = await params;
  return <DungeonDetailPageContent dungeonId={dungeonId} />;
}
