import { CharacterSheetPageContent } from "./CharacterSheetPageContent";

/** Props for the character sheet page — receives worldId and characterId from the URL. */
interface CharacterSheetPageProps {
  readonly params: Promise<{ worldId: string; characterId: string }>;
}

/**
 * Server component shell for the world-scoped character sheet page.
 * Delegates rendering to the client-side CharacterSheetPageContent.
 */
export default async function CharacterSheetPage({
  params,
}: CharacterSheetPageProps): Promise<React.ReactElement> {
  const { worldId, characterId } = await params;
  return (
    <CharacterSheetPageContent
      worldId={worldId}
      characterId={characterId}
    />
  );
}
