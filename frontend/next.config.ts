import type { NextConfig } from "next";

/**
 * Next.js configuration for the DnD Frontend application.
 * standalone output bundles only the required files for production,
 * which significantly reduces the Docker image size.
 */
const nextConfig: NextConfig = {
  output: "standalone",
};

export default nextConfig;
