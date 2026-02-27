// Application display name shown in metadata and UI headings.
export const APP_NAME = "DnD Frontend" as const;

// Default number of items to show per paginated list.
export const DEFAULT_PAGE_SIZE = 20 as const;

// Maximum length for user-generated text fields such as names and descriptions.
export const MAX_TEXT_LENGTH = 500 as const;

// Debounce delay in milliseconds for search inputs.
export const SEARCH_DEBOUNCE_MS = 300 as const;

// Local storage key used to persist auth tokens on the client.
export const AUTH_TOKEN_KEY = "dnd_auth_token" as const;
