import { apiGet, apiPost } from "@/lib/api/client";
import type {
  DungeonCreatedResponse,
  DungeonDetail,
  DungeonSummary,
  GenerateDungeonRequest,
} from "../types";

/**
 * Builds the Authorization header object for bearer-token requests.
 * @param token - The JWT access token.
 * @returns A headers object with the Authorization field set.
 */
function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

/**
 * Generates a new dungeon for the given campaign.
 * Calls POST /api/v1/campaigns/{campaignId}/dungeons — requires a DM-role JWT.
 * Generation may take several seconds while the LLM produces the content.
 * @param campaignId - The UUID of the campaign to generate a dungeon for.
 * @param request - The dungeon configuration (room count, party size, etc.).
 * @param token - The JWT access token of the authenticated DM.
 * @returns A promise resolving to the dungeon creation summary (not full detail).
 */
export async function generateDungeon(
  campaignId: string,
  request: GenerateDungeonRequest,
  token: string
): Promise<DungeonCreatedResponse> {
  return apiPost<DungeonCreatedResponse>(
    `/api/v1/campaigns/${campaignId}/dungeons`,
    request,
    { headers: authHeaders(token) }
  );
}

/**
 * Fetches the full detail for a single dungeon including all rooms and quest.
 * Calls GET /api/v1/dungeons/{dungeonId}.
 * Accessible by any authenticated user — both DMs and players inside a room.
 * @param dungeonId - The UUID of the dungeon to fetch.
 * @param token - The JWT access token of the authenticated user.
 * @returns A promise resolving to the full DungeonDetail.
 */
export async function getDungeonDetail(
  dungeonId: string,
  token: string
): Promise<DungeonDetail> {
  return apiGet<DungeonDetail>(`/api/v1/dungeons/${dungeonId}`, {
    headers: authHeaders(token),
  });
}

/**
 * Fetches all dungeons generated for the given campaign.
 * Calls GET /api/v1/campaigns/{campaignId}/dungeons — requires a DM-role JWT.
 * Results are ordered newest first.
 * @param campaignId - The UUID of the campaign.
 * @param token - The JWT access token of the authenticated DM.
 * @returns A promise resolving to an array of DungeonSummary items.
 */
export async function listDungeons(
  campaignId: string,
  token: string
): Promise<DungeonSummary[]> {
  return apiGet<DungeonSummary[]>(`/api/v1/campaigns/${campaignId}/dungeons`, {
    headers: authHeaders(token),
  });
}
