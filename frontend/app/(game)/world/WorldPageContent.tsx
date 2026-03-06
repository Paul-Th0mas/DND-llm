"use client";

import { useRouter } from "next/navigation";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { DmOnlyRoute } from "@/shared/components/DmOnlyRoute";
import { GeneratedWorldView } from "@/domains/world/components/GeneratedWorldView";
import { selectGeneratedWorld, useWorldStore } from "@/domains/world/store/world.store";

/**
 * Client component for the world view page.
 * Reads the generated world from the world store. If no world has been generated
 * yet in this session, shows a prompt to return to the dashboard and generate one.
 */
export function WorldPageContent(): React.ReactElement {
  const router = useRouter();
  const generatedWorld = useWorldStore(selectGeneratedWorld);

  return (
    <DmOnlyRoute>
      <Box sx={{ minHeight: "100vh", bgcolor: "background.default" }}>
        {/* Page header */}
        <Box
          component="header"
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 1,
            px: { xs: 3, sm: 6 },
            py: 2,
            borderBottom: "1px solid",
            borderColor: "divider",
            bgcolor: "background.paper",
          }}
        >
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => router.push("/dashboard")}
            sx={{ textTransform: "none", color: "text.secondary" }}
          >
            Dashboard
          </Button>
          <Typography variant="h6" fontWeight={700} sx={{ ml: 1 }}>
            Generated World
          </Typography>
        </Box>

        {/* Content */}
        <Box sx={{ px: { xs: 3, sm: 6 }, py: 4, maxWidth: 900, mx: "auto" }}>
          {generatedWorld !== null ? (
            <GeneratedWorldView world={generatedWorld} />
          ) : (
            <Box sx={{ textAlign: "center", py: 8 }}>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                No world generated yet
              </Typography>
              <Typography variant="body1" color="text.secondary" gutterBottom>
                Use the Generate World wizard from the dashboard to create a world.
              </Typography>
              <Button
                variant="contained"
                onClick={() => router.push("/dashboard")}
                sx={{ mt: 2, textTransform: "none", fontWeight: 600, borderRadius: 2 }}
              >
                Go to Dashboard
              </Button>
            </Box>
          )}
        </Box>
      </Box>
    </DmOnlyRoute>
  );
}
