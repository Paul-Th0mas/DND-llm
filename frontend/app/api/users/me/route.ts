import { NextRequest, NextResponse } from "next/server";

// CORS: the backend needs CORSMiddleware added to app/main.py before this BFF
// proxy can be removed and the frontend calls the backend directly.
const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

/**
 * BFF proxy for GET /api/v1/users/me.
 * Forwards the Authorization header from the client to the backend and
 * returns the raw JSON response (or the error status code).
 * @param request - The incoming Next.js request containing the Authorization header.
 * @returns The proxied response from the backend.
 */
export async function GET(request: NextRequest): Promise<NextResponse> {
  const authorization = request.headers.get("Authorization");

  if (!authorization) {
    return NextResponse.json(
      { message: "Missing Authorization header" },
      { status: 401 }
    );
  }

  const backendResponse = await fetch(
    `${BACKEND_URL}/api/v1/users/me`,
    {
      method: "GET",
      headers: {
        Authorization: authorization,
        "Content-Type": "application/json",
      },
    }
  );

  const data: unknown = await backendResponse.json();

  return NextResponse.json(data, { status: backendResponse.status });
}
