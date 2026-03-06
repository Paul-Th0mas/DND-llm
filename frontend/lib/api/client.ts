// Base URL for all API requests. Must be set via NEXT_PUBLIC_API_URL environment variable.
const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

/**
 * Typed error thrown by all API helpers when the server returns a non-ok status.
 * Carries the HTTP status code and the detail message from the response body so
 * callers can distinguish e.g. 400 (validation) from 404 (not found) from 429 (quota).
 */
export class ApiError extends Error {
  /** HTTP status code returned by the server. */
  readonly status: number;
  /** The `detail` field from the JSON error body, if present. */
  readonly detail: string;

  constructor(status: number, detail: string) {
    super(`API error ${status}: ${detail}`);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

/**
 * Reads the response body and throws an ApiError with the status code and
 * the `detail` field from the JSON body (matching FastAPI's error shape).
 * Falls back to the status text if the body cannot be parsed.
 */
async function throwApiError(response: Response): Promise<never> {
  let detail = response.statusText;
  try {
    const body = (await response.json()) as { detail?: string };
    if (typeof body.detail === "string") {
      detail = body.detail;
    }
  } catch {
    // Body was not JSON — keep statusText as the detail.
  }
  throw new ApiError(response.status, detail);
}

// Default headers applied to every request.
const DEFAULT_HEADERS: HeadersInit = {
  "Content-Type": "application/json",
};

/**
 * Performs a typed GET request to the given API path.
 * @param path - The API endpoint path relative to the base URL.
 * @param options - Optional fetch init overrides.
 * @returns A promise resolving to the parsed JSON response typed as T.
 * @throws An error if the response status is not ok.
 */
export async function apiGet<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    method: "GET",
    headers: { ...DEFAULT_HEADERS, ...options?.headers },
  });

  if (!response.ok) {
    await throwApiError(response);
  }

  return response.json() as Promise<T>;
}

/**
 * Performs a typed POST request to the given API path.
 * @param path - The API endpoint path relative to the base URL.
 * @param body - The request body to be serialized as JSON.
 * @param options - Optional fetch init overrides.
 * @returns A promise resolving to the parsed JSON response typed as T.
 * @throws An error if the response status is not ok.
 */
export async function apiPost<T>(
  path: string,
  body: unknown,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    method: "POST",
    headers: { ...DEFAULT_HEADERS, ...options?.headers },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    await throwApiError(response);
  }

  return response.json() as Promise<T>;
}

/**
 * Performs a typed PUT request to the given API path.
 * @param path - The API endpoint path relative to the base URL.
 * @param body - The request body to be serialized as JSON.
 * @param options - Optional fetch init overrides.
 * @returns A promise resolving to the parsed JSON response typed as T.
 * @throws An error if the response status is not ok.
 */
export async function apiPut<T>(
  path: string,
  body: unknown,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    method: "PUT",
    headers: { ...DEFAULT_HEADERS, ...options?.headers },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    await throwApiError(response);
  }

  return response.json() as Promise<T>;
}

/**
 * Performs a typed DELETE request to the given API path.
 * @param path - The API endpoint path relative to the base URL.
 * @param options - Optional fetch init overrides.
 * @returns A promise resolving to the parsed JSON response typed as T.
 * @throws An error if the response status is not ok.
 */
export async function apiDelete<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    method: "DELETE",
    headers: { ...DEFAULT_HEADERS, ...options?.headers },
  });

  if (!response.ok) {
    await throwApiError(response);
  }

  return response.json() as Promise<T>;
}
