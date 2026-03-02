/**
 * Generic API response wrapper used across all domains.
 * @template T - The shape of the response data payload.
 */
export interface ApiResponse<T> {
  readonly data: T;
  readonly message: string;
  readonly success: boolean;
}

/**
 * Generic paginated response wrapper for list endpoints.
 * @template T - The shape of each item in the results array.
 */
export interface PaginatedResponse<T> {
  readonly data: readonly T[];
  readonly total: number;
  readonly page: number;
  readonly pageSize: number;
  readonly totalPages: number;
}

/**
 * Standard error shape returned by the API.
 */
export interface ApiError {
  readonly message: string;
  readonly code: string;
  readonly statusCode: number;
}

/**
 * Represents an entity with a unique identifier and timestamps.
 * Extend this for any domain entity that is persisted.
 */
export interface BaseEntity {
  readonly id: string;
  readonly createdAt: string;
  readonly updatedAt: string;
}

/**
 * Async operation state used in Zustand store slices.
 * Tracks whether an async operation is loading, has errored, or is idle.
 */
export interface AsyncState {
  readonly isLoading: boolean;
  readonly error: string | null;
}
