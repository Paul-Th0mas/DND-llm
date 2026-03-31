import { apiGet, apiPost, apiDelete } from "@/lib/api/client";
import type {
  CharacterClassListResponse,
  CharacterCreatedResponse,
  CharacterSheet,
  CharacterSpeciesListResponse,
  CampaignRosterResponse,
  CreateCharacterRequest,
  LinkCharacterRequest,
  LinkCharacterResponse,
  ListMyCharactersResponse,
} from "@/domains/character/types";

/**
 * Builds the Authorization header object for bearer-token requests.
 * @param token - The JWT access token.
 * @returns A headers object with the Authorization field set.
 */
function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

/**
 * Fetches all character classes available for the given world theme.
 * Calls GET /api/v1/character-options/classes?theme={theme}.
 * No authentication required.
 * @param theme - The world theme string (e.g. "MEDIEVAL_FANTASY").
 * @returns A promise resolving to a CharacterClassListResponse.
 */
export async function getCharacterClasses(
  theme: string
): Promise<CharacterClassListResponse> {
  return apiGet<CharacterClassListResponse>(
    `/api/v1/character-options/classes?theme=${encodeURIComponent(theme)}`
  );
}

/**
 * Fetches all character species available for the given world theme.
 * Calls GET /api/v1/character-options/species?theme={theme}.
 * No authentication required.
 * @param theme - The world theme string (e.g. "MEDIEVAL_FANTASY").
 * @returns A promise resolving to a CharacterSpeciesListResponse.
 */
export async function getCharacterSpecies(
  theme: string
): Promise<CharacterSpeciesListResponse> {
  return apiGet<CharacterSpeciesListResponse>(
    `/api/v1/character-options/species?theme=${encodeURIComponent(theme)}`
  );
}

/**
 * Creates a new character for the authenticated user.
 * Calls POST /api/v1/characters — requires a Bearer token.
 * @param request - The character creation request body.
 * @param token - The JWT access token of the authenticated user.
 * @returns A promise resolving to the created character response.
 */
export async function createCharacter(
  request: CreateCharacterRequest,
  token: string
): Promise<CharacterCreatedResponse> {
  return apiPost<CharacterCreatedResponse>("/api/v1/characters", request, {
    headers: authHeaders(token),
  });
}

/**
 * Fetches all characters owned by the authenticated user.
 * Calls GET /api/v1/characters — requires a Bearer token.
 * @param token - The JWT access token of the authenticated user.
 * @returns A promise resolving to a ListMyCharactersResponse.
 */
export async function listMyCharacters(
  token: string
): Promise<ListMyCharactersResponse> {
  return apiGet<ListMyCharactersResponse>("/api/v1/characters", {
    headers: authHeaders(token),
  });
}

/**
 * Fetches the full character sheet for the authenticated owner.
 * Calls GET /api/v1/characters/{characterId} — requires a Bearer token.
 * Returns 404 if the character does not exist or belongs to another user.
 * @param characterId - The UUID of the character to fetch.
 * @param token - The JWT access token of the authenticated user.
 * @returns A promise resolving to the CharacterSheet.
 */
export async function getCharacterSheet(
  characterId: string,
  token: string
): Promise<CharacterSheet> {
  return apiGet<CharacterSheet>(`/api/v1/characters/${characterId}`, {
    headers: authHeaders(token),
  });
}

/**
 * Links a character to a campaign.
 * Calls POST /api/v1/campaigns/{campaignId}/characters — requires a Bearer token.
 * @param campaignId - The UUID of the target campaign.
 * @param request - The link character request body containing character_id.
 * @param token - The JWT access token of the authenticated user.
 * @returns A promise resolving to the link response.
 */
export async function linkCharacterToCampaign(
  campaignId: string,
  request: LinkCharacterRequest,
  token: string
): Promise<LinkCharacterResponse> {
  return apiPost<LinkCharacterResponse>(
    `/api/v1/campaigns/${campaignId}/characters`,
    request,
    { headers: authHeaders(token) }
  );
}

/**
 * Unlinks a character from a campaign.
 * Calls DELETE /api/v1/campaigns/{campaignId}/characters/{characterId}.
 * Returns void (204 no content).
 * @param campaignId - The UUID of the campaign.
 * @param characterId - The UUID of the character to unlink.
 * @param token - The JWT access token of the authenticated user.
 * @returns A promise resolving when the unlink is complete.
 */
export async function unlinkCharacterFromCampaign(
  campaignId: string,
  characterId: string,
  token: string
): Promise<void> {
  await apiDelete<void>(
    `/api/v1/campaigns/${campaignId}/characters/${characterId}`,
    { headers: authHeaders(token) }
  );
}

/**
 * Fetches the party roster for a campaign (DM only).
 * Calls GET /api/v1/campaigns/{campaignId}/characters — requires a DM Bearer token.
 * @param campaignId - The UUID of the campaign.
 * @param token - The JWT access token of the authenticated DM.
 * @returns A promise resolving to a CampaignRosterResponse.
 */
export async function getCampaignRoster(
  campaignId: string,
  token: string
): Promise<CampaignRosterResponse> {
  return apiGet<CampaignRosterResponse>(
    `/api/v1/campaigns/${campaignId}/characters`,
    { headers: authHeaders(token) }
  );
}
