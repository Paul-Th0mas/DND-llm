import type { Metadata } from "next";
import { CharacterDetailPageContent } from "./CharacterDetailPageContent";

/** Route params for the character detail page. */
interface CharacterPageParams {
  campaignId: string;
  characterId: string;
}

/**
 * Generates SEO metadata for the character sheet page.
 * @param props - Object containing route params.
 * @returns Metadata with a descriptive title.
 */
export async function generateMetadata({
  params,
}: {
  params: Promise<CharacterPageParams>;
}): Promise<Metadata> {
  const { characterId } = await params;
  return {
    title: `Character ${characterId} - DnD`,
  };
}

/**
 * Server component shell for the character sheet page (US-030).
 * Extracts route params and delegates rendering to CharacterDetailPageContent.
 */
export default async function CharacterDetailPage({
  params,
}: {
  params: Promise<CharacterPageParams>;
}): Promise<React.ReactElement> {
  const { campaignId, characterId } = await params;

  return (
    <CharacterDetailPageContent
      campaignId={campaignId}
      characterId={characterId}
    />
  );
}
