import type { Metadata } from "next";
import { CharacterCreatePageContent } from "./CharacterCreatePageContent";

/** Metadata for the world-scoped character creation page. */
export const metadata: Metadata = {
  title: "Create Character",
};

/** Props for the character creation page — receives worldId from the URL. */
interface CharacterCreatePageProps {
  readonly params: Promise<{ worldId: string }>;
}

/**
 * Server component shell for the world-scoped character creation page.
 * Reads the worldId from the URL params and delegates to the client component.
 */
export default async function CharacterCreatePage({
  params,
}: CharacterCreatePageProps): Promise<React.ReactElement> {
  const { worldId } = await params;
  return <CharacterCreatePageContent worldId={worldId} />;
}
