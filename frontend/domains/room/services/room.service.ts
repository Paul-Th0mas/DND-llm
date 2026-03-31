import { apiDelete, apiGet, apiPatch, apiPost } from "@/lib/api/client";
import type {
  JoinRoomByIdResponse,
  LobbyRoom,
  Room,
  RoomResponse,
} from "@/domains/room/types";

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
 * @param dungeonId - UUID of the dungeon session to link to this room.
 * @param campaignId - UUID of the campaign to link to this room.
 * @returns A promise resolving to the created room and its room-scoped token.
 */
export async function createRoom(
  name: string,
  maxPlayers: number,
  token: string,
  dungeonId: string | null = null,
  campaignId: string | null = null
): Promise<RoomResponse> {
  return apiPost<RoomResponse>(
    "/api/v1/rooms/create",
    { name, max_players: maxPlayers, dungeon_id: dungeonId, campaign_id: campaignId },
    { headers: authHeaders(token) }
  );
}

/**
 * Deletes (closes) a room by ID.
 * Calls DELETE /api/v1/rooms/{roomId} — DM-role required.
 * Returns 204 No Content on success; throws ApiError on failure.
 * @param roomId - The UUID of the room to delete.
 * @param token - The JWT access token of the authenticated DM.
 * @returns A promise that resolves when the room is deleted.
 */
export async function deleteRoom(
  roomId: string,
  token: string
): Promise<void> {
  // The backend returns 204 with no body. apiDelete expects a typed response,
  // so we use unknown and discard the value.
  await apiDelete<unknown>(`/api/v1/rooms/${roomId}`, {
    headers: authHeaders(token),
  });
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
 * Links a dungeon and campaign to an existing room.
 * Calls PATCH /api/v1/rooms/{roomId}/link — requires DM-role JWT.
 * @param roomId - UUID of the room to update.
 * @param dungeonId - UUID of the dungeon to link.
 * @param campaignId - UUID of the campaign to link.
 * @param token - JWT access token of the authenticated DM.
 * @returns A promise resolving to the updated Room.
 */
export async function linkRoomDungeon(
  roomId: string,
  dungeonId: string,
  campaignId: string,
  token: string
): Promise<Room> {
  return apiPatch<Room>(
    `/api/v1/rooms/${roomId}/link`,
    { dungeon_id: dungeonId, campaign_id: campaignId },
    { headers: authHeaders(token) }
  );
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

/**
 * Fetches the list of rooms from the lobby browser.
 * Calls GET /api/v1/rooms?status={status}.
 * @param token - The JWT access token of the authenticated user.
 * @param status - Filter by room status (default: "open").
 * @returns A promise resolving to an array of LobbyRoom summaries.
 */
export async function listLobbies(
  token: string,
  status: string = "open"
): Promise<LobbyRoom[]> {
  const data = await apiGet<{ rooms: LobbyRoom[] }>(
    `/api/v1/rooms?status=${status}`,
    { headers: authHeaders(token) }
  );
  return data.rooms;
}

/**
 * Joins a room via the lobby browser using the room's UUID and a password.
 * Calls POST /api/v1/rooms/{roomId}/join.
 * @param roomId - The UUID of the room to join.
 * @param password - The room password (empty string for password-free rooms).
 * @param token - The JWT access token of the authenticated player.
 * @returns A promise resolving to the joined room, a room-scoped token, and a message.
 */
export async function joinRoomById(
  roomId: string,
  password: string,
  token: string
): Promise<JoinRoomByIdResponse> {
  return apiPost<JoinRoomByIdResponse>(
    `/api/v1/rooms/${roomId}/join`,
    { password },
    { headers: authHeaders(token) }
  );
}
