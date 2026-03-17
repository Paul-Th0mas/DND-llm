"use client";

import { useRouter } from "next/navigation";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { DmOnlyRoute } from "@/shared/components/DmOnlyRoute";

/**
 * Client component for the world view page.
 * Worlds are now browsed through the campaign creation wizard.
 * This page redirects users to the campaigns section.
 */
export function WorldPageContent(): React.ReactElement {
  const router = useRouter();

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
            Worlds
          </Typography>
        </Box>

        {/* Content */}
        <Box
          sx={{
            px: { xs: 3, sm: 6 },
            py: 8,
            maxWidth: 600,
            mx: "auto",
            textAlign: "center",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 3,
          }}
        >
          <Typography variant="h6" fontWeight={600}>
            Worlds are selected during campaign creation
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Browse and select a world when creating a new campaign. Each campaign is
            linked to a pre-seeded world with its own lore, factions, and bosses.
          </Typography>
          <Button
            variant="contained"
            onClick={() => router.push("/campaign")}
            sx={{ textTransform: "none", fontWeight: 600, borderRadius: 2 }}
          >
            Go to Campaigns
          </Button>
        </Box>
      </Box>
    </DmOnlyRoute>
  );
}
