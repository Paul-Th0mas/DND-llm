import { apiGet, apiPost } from "@/lib/api/client";
import type {
  GeneratedWorldResponse,
  Theme,
  WorldOptionsResponse,
  WorldSettingsRequest,
} from "@/domains/world/types";

/**
 * Fetches all valid enum values and constraints for world generation settings.
 * Calls GET /api/v1/worlds/options — no auth required.
 * When theme is provided, the backend may return a filtered subset of options
 * relevant to that theme (e.g. theme-appropriate quest focuses).
 * @param theme - Optional theme to filter options by. Omit to fetch all options.
 * @returns A promise resolving to the world options response.
 */
export async function getWorldOptions(theme?: Theme): Promise<WorldOptionsResponse> {
  const path = theme
    ? `/api/v1/worlds/options?theme=${theme}`
    : "/api/v1/worlds/options";
  return apiGet<WorldOptionsResponse>(path);
}

/**
 * Builds the Authorization header object for bearer-token requests.
 * @param token - The JWT access token.
 * @returns A headers object with the Authorization field set.
 */
function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

/**
 * Sends the DM's world settings to the API and returns the generated world.
 * Calls POST /api/v1/worlds/generate — requires a DM-role JWT.
 * The returned world is not persisted; it exists only in client memory for the session.
 * @param settings - The world configuration chosen by the DM.
 * @param token - The JWT access token of the authenticated DM.
 * @returns A promise resolving to the fully generated world response.
 */
export async function generateWorld(
  settings: WorldSettingsRequest,
  token: string
): Promise<GeneratedWorldResponse> {
  return apiPost<GeneratedWorldResponse>(
    "/api/v1/worlds/generate",
    settings,
    { headers: authHeaders(token) }
  );
}
