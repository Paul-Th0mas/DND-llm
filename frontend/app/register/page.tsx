import type { Metadata } from "next";
import { RegisterPanel } from "@/domains/auth/components/RegisterPanel";

export const metadata: Metadata = {
  title: "Register – Dungeons and Droids",
  description: "Create a new account and choose your role to enter the realm.",
};

/**
 * Registration page for the Dungeons and Droids application.
 * Renders the full-screen email + role registration form.
 * All interactivity is delegated to RegisterPanel ("use client").
 */
export default function RegisterPage(): React.ReactElement {
  return <RegisterPanel />;
}
