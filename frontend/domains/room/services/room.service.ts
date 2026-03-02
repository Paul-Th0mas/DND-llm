import { apiGet, apiPost } from "@/lib/api/client";
import type { Room, RoomResponse } from "@/domains/room/types";

/**
 * Builds the Authorization header object for bearer-token requests.
 * @param token - The JWT access token.
 * @returns A headers object with the Authorization field set.
 */
function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

/**
 * Creates a new game room.
 * Calls POST /api/v1/rooms/create with the current user's auth token.
 * @param name - The display name for the room.
 * @param maxPlayers - Maximum number of players allowed in the room.
 * @param token - The JWT access token of the authenticated DM.
 * @returns A promise resolving to the created room and its room-scoped token.
 */
export async function createRoom(
  name: string,
  maxPlayers: number,
  token: string
): Promise<RoomResponse> {
  return apiPost<RoomResponse>(
    "/api/v1/rooms/create",
    { name, max_players: maxPlayers },
    { headers: authHeaders(token) }
  );
}

/**
 * Fetches the details of a specific room.
 * Calls GET /api/v1/rooms/{roomId} with the current user's auth token.
 * @param roomId - The UUID of the room to fetch.
 * @param token - The JWT access token of the authenticated user.
 * @returns A promise resolving to the room details.
 */
export async function getRoomDetail(
  roomId: string,
  token: string
): Promise<Room> {
  return apiGet<Room>(`/api/v1/rooms/${roomId}`, {
    headers: authHeaders(token),
  });
}

/**
 * Joins an existing room using its invite code.
 * Calls POST /api/v1/rooms/join/{inviteCode} with the current user's auth token.
 * @param inviteCode - The room's short invite code shared by the DM.
 * @param token - The JWT access token of the authenticated player.
 * @returns A promise resolving to the joined room and its room-scoped token.
 */
export async function joinRoom(
  inviteCode: string,
  token: string
): Promise<RoomResponse> {
  return apiPost<RoomResponse>(
    `/api/v1/rooms/join/${inviteCode}`,
    {},
    { headers: authHeaders(token) }
  );
}
