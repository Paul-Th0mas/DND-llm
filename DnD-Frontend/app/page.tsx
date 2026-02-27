import { AuthCallbackPage } from "./AuthCallbackPage";

/**
 * Root page at "/".
 * Renders the AuthCallbackPage client component which handles:
 * - Redirecting authenticated users to /game
 * - Redirecting unauthenticated users to /login
 * The OAuth token-in-URL handling itself occurs inside AuthProvider (in layout).
 */
export default function Home(): React.ReactElement {
  return <AuthCallbackPage />;
}
