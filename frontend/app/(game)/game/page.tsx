import type { Metadata } from "next";
import { ProtectedRoute } from "@/shared/components/ProtectedRoute";
import { GameContent } from "./GameContent";

export const metadata: Metadata = {
  title: "The Realm – Dungeons and Droids",
  description: "Your active game session.",
};

/**
 * Game page — the main authenticated area of the application.
 * ProtectedRoute guards this content; unauthenticated users are redirected to /login.
 * GameContent is a client component that reads the user from the auth store.
 * The chat domain will be mounted here in a future iteration.
 */
export default function GamePage(): React.ReactElement {
  return (
    <ProtectedRoute>
      <GameContent />
    </ProtectedRoute>
  );
}
