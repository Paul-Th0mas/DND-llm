import { apiGet, apiPost } from "@/lib/api/client";
import type {
  CampaignDetail,
  CampaignResponse,
  CampaignSummary,
  CampaignWorldDetailResponse,
  CreateCampaignRequest,
} from "@/domains/campaign/types";
import type { DungeonSummary } from "@/domains/dungeon/types";

/**
 * Builds the Authorization header object for bearer-token requests.
 * @param token - The JWT access token.
 * @returns A headers object with the Authorization field set.
 */
function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

/**
 * Creates a new campaign by sending DM requirements to the API.
 * Calls POST /api/v1/campaigns — requires a DM-role JWT.
 * @param request - The campaign requirements from the intake form.
 * @param token - The JWT access token of the authenticated DM.
 * @returns A promise resolving to the campaign response with ID and next step.
 */
export async function createCampaign(
  request: CreateCampaignRequest,
  token: string
): Promise<CampaignResponse> {
  return apiPost<CampaignResponse>("/api/v1/campaigns", request, {
    headers: authHeaders(token),
  });
}

/**
 * Fetches the list of all campaigns owned by the authenticated DM.
 * Calls GET /api/v1/campaigns — requires a DM-role JWT.
 * @param token - The JWT access token of the authenticated DM.
 * @returns A promise resolving to an array of CampaignSummary objects.
 */
export async function getCampaigns(token: string): Promise<CampaignSummary[]> {
  return apiGet<CampaignSummary[]>("/api/v1/campaigns", {
    headers: authHeaders(token),
  });
}

/**
 * Fetches full detail for a single campaign.
 * Calls GET /api/v1/campaigns/{campaignId} — requires a DM-role JWT.
 * @param campaignId - The UUID of the campaign to fetch.
 * @param token - The JWT access token of the authenticated DM.
 * @returns A promise resolving to the CampaignDetail for the given ID.
 */
export async function getCampaignById(
  campaignId: string,
  token: string
): Promise<CampaignDetail> {
  return apiGet<CampaignDetail>(`/api/v1/campaigns/${campaignId}`, {
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
export async function listCampaignDungeons(
  campaignId: string,
  token: string
): Promise<DungeonSummary[]> {
  return apiGet<DungeonSummary[]>(`/api/v1/campaigns/${campaignId}/dungeons`, {
    headers: authHeaders(token),
  });
}

/**
 * Triggers LLM world generation for the given campaign.
 * Calls POST /api/v1/campaigns/{campaignId}/world/generate — requires a DM-role JWT.
 * The response contains the fully generated world with factions, NPCs, and adventure hooks.
 * @param campaignId - The UUID of the campaign to generate a world for.
 * @param token - The JWT access token of the authenticated DM.
 * @returns A promise resolving to the generated campaign world detail.
 */
export async function generateCampaignWorld(
  campaignId: string,
  token: string
): Promise<CampaignWorldDetailResponse> {
  return apiPost<CampaignWorldDetailResponse>(
    `/api/v1/campaigns/${campaignId}/world/generate`,
    {},
    { headers: authHeaders(token) }
  );
}
