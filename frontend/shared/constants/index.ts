// Application display name shown in metadata and UI headings.
export const APP_NAME = "Dungeons and Droids" as const;

// Default number of items to show per paginated list.
export const DEFAULT_PAGE_SIZE = 20 as const;

// Maximum length for user-generated text fields such as names and descriptions.
export const MAX_TEXT_LENGTH = 500 as const;

// Debounce delay in milliseconds for search inputs.
export const SEARCH_DEBOUNCE_MS = 300 as const;

// Local storage key used to persist auth tokens on the client.
export const AUTH_TOKEN_KEY = "dnd_auth_token" as const;

// World generation slider constraints — must match backend domain constants.
export const WORLD_ROOM_COUNT_MIN = 5 as const;
export const WORLD_ROOM_COUNT_MAX = 15 as const;

// Campaign intake form constraints.
export const CAMPAIGN_PLAYER_COUNT_MIN = 1 as const;
export const CAMPAIGN_PLAYER_COUNT_MAX = 8 as const;
export const CAMPAIGN_LEVEL_MIN = 1 as const;
export const CAMPAIGN_LEVEL_MAX = 20 as const;
export const CAMPAIGN_SESSION_COUNT_MIN = 1 as const;
export const CAMPAIGN_SESSION_COUNT_MAX = 100 as const;
