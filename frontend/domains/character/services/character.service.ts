import { apiGet, apiPost } from "@/lib/api/client";
import type {
  CampaignRosterResponse,
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
 * Fetches the list of characters owned by the authenticated player.
 * Calls GET /api/v1/characters — requires a valid JWT.
 * @param token - The JWT access token of the authenticated player.
 * @returns A promise resolving to the player's character list.
 */
export async function listMyCharacters(
  token: string
): Promise<ListMyCharactersResponse> {
  return apiGet<ListMyCharactersResponse>("/api/v1/characters", {
    headers: authHeaders(token),
  });
}

/**
 * Links a character to a campaign.
 * Calls POST /api/v1/campaigns/{campaignId}/characters — requires a valid JWT.
 * @param campaignId - The UUID of the target campaign.
 * @param request - The link request body containing the character_id.
 * @param token - The JWT access token of the authenticated player.
 * @returns A promise resolving to the link confirmation response.
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
 * Fetches the full character roster for a campaign (DM only).
 * Calls GET /api/v1/campaigns/{campaignId}/characters — requires a DM-role JWT.
 * @param campaignId - The UUID of the campaign.
 * @param token - The JWT access token of the authenticated DM.
 * @returns A promise resolving to the campaign roster.
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
