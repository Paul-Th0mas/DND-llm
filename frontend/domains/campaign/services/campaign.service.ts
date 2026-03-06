import { apiPost } from "@/lib/api/client";
import type {
  CampaignResponse,
  CreateCampaignRequest,
  GenerateCampaignWorldResponse,
} from "@/domains/campaign/types";

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
 * Triggers world generation for an existing campaign.
 * Calls POST /api/v1/campaigns/{id}/world — requires a DM-role JWT.
 * The DM must own the campaign.
 * @param campaignId - The UUID of the campaign to generate a world for.
 * @param token - The JWT access token of the authenticated DM.
 * @returns A promise resolving to the generated world summary.
 */
export async function generateCampaignWorld(
  campaignId: string,
  token: string
): Promise<GenerateCampaignWorldResponse> {
  return apiPost<GenerateCampaignWorldResponse>(
    `/api/v1/campaigns/${campaignId}/world`,
    {},
    { headers: authHeaders(token) }
  );
}
