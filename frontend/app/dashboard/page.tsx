import type { Metadata } from "next";
import { DashboardView } from "@/domains/room/components/DashboardView";

export const metadata: Metadata = {
  title: "Dashboard – Dungeons and Droids",
  description: "Create or join a game room.",
};

/**
 * Dashboard page — the main landing page after authentication.
 * Delegates all rendering and interactivity to DashboardView ("use client").
 */
export default function DashboardPage(): React.ReactElement {
  return <DashboardView />;
}
