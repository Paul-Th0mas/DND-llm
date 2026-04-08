import type { Metadata } from "next";
import { Geist, Geist_Mono, MedievalSharp, Caudex, Newsreader, Work_Sans } from "next/font/google";
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

// MedievalSharp — used for scroll card titles and headings.
// Exposed as CSS variable --font-medieval-sharp for use in ScrollCard.
const medievalSharp = MedievalSharp({
  variable: "--font-medieval-sharp",
  subsets: ["latin"],
  weight: "400",
});

// Caudex — used for body text inside scroll cards.
// Exposed as CSS variable --font-caudex for use in ScrollCard.
const caudex = Caudex({
  variable: "--font-caudex",
  subsets: ["latin"],
  weight: ["400", "700"],
});

// Newsreader — serif used for editorial headings in the "Modern Scriptorium" design.
// Exposed as CSS variable --font-newsreader.
const newsreader = Newsreader({
  variable: "--font-newsreader",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  style: ["normal", "italic"],
  display: "swap",
});

// Work Sans — clean sans-serif used for all UI labels and body text.
// Exposed as CSS variable --font-work-sans.
const workSans = Work_Sans({
  variable: "--font-work-sans",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Dungeons and Droids",
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
      <body
        className={`${geistSans.variable} ${geistMono.variable} ${medievalSharp.variable} ${caudex.variable} ${newsreader.variable} ${workSans.variable} antialiased`}
      >
        <ThemeRegistry>
          <AuthProvider>{children}</AuthProvider>
        </ThemeRegistry>
      </body>
    </html>
  );
}
