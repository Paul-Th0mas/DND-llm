import type { Metadata } from "next";
import { WorldDetailPageContent } from "./WorldDetailPageContent";

export const metadata: Metadata = {
  title: "World Detail – Dungeons and Droids",
  description: "Explore a world's lore, factions, and bosses before creating your character.",
};

/** Props for the world detail page — receives worldId from the URL segment. */
interface WorldDetailPageProps {
  readonly params: Promise<{ readonly worldId: string }>;
}

/**
 * Server component shell for the world detail page.
 * Reads the worldId from URL params and delegates rendering to the client component.
 */
export default async function WorldDetailPage({
  params,
}: WorldDetailPageProps): Promise<React.ReactElement> {
  const { worldId } = await params;
  return <WorldDetailPageContent worldId={worldId} />;
}
