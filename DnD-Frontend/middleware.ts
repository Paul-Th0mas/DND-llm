import { type NextRequest, NextResponse } from "next/server";

// Cookie name that mirrors the localStorage key used by AuthProvider.
const TOKEN_COOKIE = "access_token" as const;

// Routes that require an authenticated session.
const PROTECTED_PREFIXES = ["/dashboard", "/room", "/join"] as const;

// Routes that should redirect authenticated users away (login/register).
const AUTH_ONLY_PREFIXES = ["/login", "/register"] as const;

/**
 * Returns true if the given pathname starts with any of the provided prefixes.
 * @param pathname - The current request pathname.
 * @param prefixes - An array of route prefix strings to check against.
 * @returns True if the pathname matches a prefix.
 */
function matchesPrefix(
  pathname: string,
  prefixes: readonly string[]
): boolean {
  return prefixes.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`)
  );
}

/**
 * Next.js edge middleware for server-side authentication route guarding.
 *
 * Rules:
 * - Protected routes (/dashboard, /room, /join): redirect to /login if no token cookie.
 * - Auth-only routes (/login, /register): redirect to /dashboard if a token cookie is present.
 * - All other routes: pass through unchanged.
 *
 * The access_token cookie is set by AuthProvider on the client after successful
 * OAuth login, and cleared on logout. It is not httpOnly so that client JS
 * can manage it alongside localStorage.
 */
export function middleware(request: NextRequest): NextResponse {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get(TOKEN_COOKIE)?.value;
  const isAuthenticated = Boolean(token);

  if (matchesPrefix(pathname, PROTECTED_PREFIXES) && !isAuthenticated) {
    const loginUrl = request.nextUrl.clone();
    loginUrl.pathname = "/login";
    loginUrl.search = "";
    return NextResponse.redirect(loginUrl);
  }

  if (matchesPrefix(pathname, AUTH_ONLY_PREFIXES) && isAuthenticated) {
    const dashboardUrl = request.nextUrl.clone();
    dashboardUrl.pathname = "/dashboard";
    dashboardUrl.search = "";
    return NextResponse.redirect(dashboardUrl);
  }

  return NextResponse.next();
}

export const config = {
  // Run on all routes except Next.js internals and static assets.
  matcher: ["/((?!_next/static|_next/image|favicon.ico|api/).*)"],
};
