import type { Metadata } from "next";
import { LoginPanel } from "@/domains/auth/components/LoginPanel";

export const metadata: Metadata = {
  title: "Login – Dungeons and Droids",
  description: "Sign in or create an account to enter the realm and begin your adventure.",
};

/**
 * Login page for the Dungeons and Droids application.
 * Renders the full-screen split-panel auth UI.
 * All interactivity is delegated to LoginPanel ("use client").
 */
export default function LoginPage(): React.ReactElement {
  return <LoginPanel />;
}
