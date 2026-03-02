/**
 * User profile returned by the backend after successful authentication.
 * Matches the shape of GET /api/v1/users/me exactly.
 */
export interface UserProfile {
  readonly id: string;
  readonly email: string;
  readonly name: string;
  readonly role: "dm" | "player";
  readonly picture_url?: string | null;
  readonly created_at: string;
}

/** Auth token response shape returned by login and register endpoints. */
export interface AuthTokenResponse {
  readonly access_token: string;
  readonly token_type: string;
}

/**
 * Typed error thrown when an authentication request fails.
 */
export class AuthError extends Error {
  readonly statusCode: number;

  constructor(message: string, statusCode: number) {
    super(message);
    this.name = "AuthError";
    this.statusCode = statusCode;
  }
}
