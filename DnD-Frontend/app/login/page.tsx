import type { Metadata } from "next";
import { LoginPanel } from "@/domains/auth/components/LoginPanel";

export const metadata: Metadata = {
  title: "Login – DnD Frontend",
  description: "Sign in or create an account to enter the realm and begin your adventure.",
};

/**
 * Login page for the DnD Frontend application.
 * Renders the full-screen split-panel auth UI.
 * All interactivity is delegated to LoginPanel ("use client").
 */
export default function LoginPage(): React.ReactElement {
  return <LoginPanel />;
}
