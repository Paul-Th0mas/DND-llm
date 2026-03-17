import { apiGet } from "@/lib/api/client";
import type { WorldDetail, WorldSummary } from "@/domains/world/types";

/**
 * Fetches the list of all pre-seeded worlds from GET /api/v1/worlds.
 * No authentication required.
 * @returns A promise resolving to an array of WorldSummary objects.
 */
export async function getWorlds(): Promise<WorldSummary[]> {
  return apiGet<WorldSummary[]>("/api/v1/worlds");
}

/**
 * Fetches full detail for a single pre-seeded world from GET /api/v1/worlds/{worldId}.
 * No authentication required.
 * @param worldId - The UUID of the world to fetch.
 * @returns A promise resolving to the WorldDetail for the given ID.
 */
export async function getWorldById(worldId: string): Promise<WorldDetail> {
  return apiGet<WorldDetail>(`/api/v1/worlds/${worldId}`);
}
