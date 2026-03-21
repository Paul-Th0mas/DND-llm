import type { NextConfig } from "next";

/**
 * Next.js configuration for the DnD Frontend application.
 * standalone output bundles only the required files for production,
 * which significantly reduces the Docker image size.
 */
const nextConfig: NextConfig = {
  output: "standalone",
  async rewrites() {
    // Proxy all /api/v1/* requests to the backend service.
    // Inside Docker Compose the backend is reachable at http://backend:8000.
    // Override BACKEND_URL in docker-compose if the service name changes.
    const backendUrl =
      process.env.BACKEND_URL ?? "http://backend:8000";
    return [
      {
        source: "/api/v1/:path*",
        destination: `${backendUrl}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
