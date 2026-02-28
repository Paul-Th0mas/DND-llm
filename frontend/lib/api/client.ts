// Base URL for all API requests. Must be set via NEXT_PUBLIC_API_URL environment variable.
const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

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
    throw new Error(`GET ${path} failed with status ${response.status}`);
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
    throw new Error(`POST ${path} failed with status ${response.status}`);
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
    throw new Error(`PUT ${path} failed with status ${response.status}`);
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
    throw new Error(`DELETE ${path} failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}
