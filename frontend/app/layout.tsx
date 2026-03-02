import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { ThemeRegistry } from "@/lib/mui/ThemeRegistry";
import { AuthProvider } from "@/domains/auth/components/AuthProvider";
import "./globals.css";

// Geist sans-serif font — used as the primary UI typeface.
const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

// Geist monospace font — used for code and numeric displays.
const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "DnD Frontend",
  description: "Domain Driven Design Next.js application",
};

/**
 * Root layout for the entire application.
 * Applies global fonts, MUI theme, and CSS baseline.
 * All pages are rendered inside this layout.
 */
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <ThemeRegistry>
          <AuthProvider>{children}</AuthProvider>
        </ThemeRegistry>
      </body>
    </html>
  );
}
