"use client";

import { useRouter } from "next/navigation";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { DmOnlyRoute } from "@/shared/components/DmOnlyRoute";
import { GeneratedDungeonView } from "@/domains/dungeon/components/GeneratedDungeonView";
import { selectActiveDungeon, useDungeonStore } from "@/domains/dungeon/store/dungeon.store";

/**
 * Client component for the dungeon view page.
 * Reads the generated dungeon from the dungeon store. If no dungeon has been generated
 * yet in this session, shows a prompt to return to the dashboard.
 */
export function DungeonPageContent(): React.ReactElement {
  const router = useRouter();
  const generatedDungeon = useDungeonStore(selectActiveDungeon);

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
            Generated Dungeon
          </Typography>
        </Box>

        {/* Content */}
        <Box sx={{ px: { xs: 3, sm: 6 }, py: 4, maxWidth: 900, mx: "auto" }}>
          {generatedDungeon !== null ? (
            <GeneratedDungeonView dungeon={generatedDungeon} />
          ) : (
            <Box sx={{ textAlign: "center", py: 8 }}>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                No dungeon generated yet
              </Typography>
              <Typography variant="body1" color="text.secondary" gutterBottom>
                Use the Generate Dungeon wizard from the dashboard to create a dungeon.
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
