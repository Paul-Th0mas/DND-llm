"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import Typography from "@mui/material/Typography";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { DmOnlyRoute } from "@/shared/components/DmOnlyRoute";
import { GeneratedDungeonView } from "@/domains/dungeon/components/GeneratedDungeonView";
import { getDungeonDetail } from "@/domains/dungeon/services/dungeon.service";
import {
  useDungeonStore,
  selectActiveDungeon,
  selectIsLoadingDungeon,
} from "@/domains/dungeon/store/dungeon.store";
import { ApiError } from "@/lib/api/client";

/** Props for the DungeonDetailPageContent component. */
export interface DungeonDetailPageContentProps {
  readonly dungeonId: string;
}

/**
 * Client component for the dungeon detail page.
 * Fetches the full dungeon by ID on mount, stores it in the dungeon store,
 * then renders GeneratedDungeonView.
 * Provides a "Create Room" button that navigates to room creation with dungeon_id
 * passed as a query parameter.
 * Restricted to DM users via DmOnlyRoute.
 */
export function DungeonDetailPageContent({
  dungeonId,
}: DungeonDetailPageContentProps): React.ReactElement {
  const router = useRouter();
  const dungeon = useDungeonStore(selectActiveDungeon);
  const isLoading = useDungeonStore(selectIsLoadingDungeon);
  const { setActiveDungeon, setLoadingDungeon, setError, error } =
    useDungeonStore();

  useEffect(() => {
    if (!dungeonId) return;

    let cancelled = false;
    const token = localStorage.getItem("access_token") ?? "";

    async function fetchDungeon(): Promise<void> {
      setLoadingDungeon(true);
      setError(null);

      try {
        const detail = await getDungeonDetail(dungeonId, token);
        if (!cancelled) {
          setActiveDungeon(detail);
        }
      } catch (err) {
        if (!cancelled) {
          if (err instanceof ApiError) {
            if (err.status === 404) {
              setError("Dungeon not found.");
            } else if (err.status === 401 || err.status === 403) {
              setError("You are not authorised to view this dungeon.");
            } else {
              setError(`Failed to load dungeon: ${err.detail}`);
            }
          } else {
            setError("Failed to load the dungeon. Please try again.");
          }
        }
      } finally {
        if (!cancelled) setLoadingDungeon(false);
      }
    }

    void fetchDungeon();

    return () => {
      cancelled = true;
    };
  }, [dungeonId, setActiveDungeon, setLoadingDungeon, setError]);

  function handleCreateRoom(): void {
    router.push(`/room?dungeon_id=${dungeonId}`);
  }

  return (
    <DmOnlyRoute>
      <Box sx={{ minHeight: "100vh", bgcolor: "background.default" }}>
        {/* Page header */}
        <Box
          component="header"
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 1,
            px: { xs: 3, sm: 6 },
            py: 2,
            borderBottom: "1px solid",
            borderColor: "divider",
            bgcolor: "background.paper",
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <Button
              startIcon={<ArrowBackIcon />}
              onClick={() => router.back()}
              sx={{ textTransform: "none", color: "text.secondary" }}
            >
              Back
            </Button>
            <Typography variant="h6" fontWeight={700} sx={{ ml: 1 }}>
              Dungeon Detail
            </Typography>
          </Box>

          {dungeon !== null && (
            <Button
              variant="contained"
              onClick={handleCreateRoom}
              sx={{
                textTransform: "none",
                fontWeight: 600,
                borderRadius: 2,
                bgcolor: "#a07d60",
                "&:hover": { bgcolor: "#7d5e45" },
              }}
            >
              Create Room
            </Button>
          )}
        </Box>

        {/* Content */}
        <Box sx={{ px: { xs: 3, sm: 6 }, py: 4, maxWidth: 900, mx: "auto" }}>
          {isLoading && (
            <Box sx={{ display: "flex", justifyContent: "center", py: 10 }}>
              <CircularProgress />
            </Box>
          )}

          {!isLoading && error !== null && (
            <Alert severity="error">{error}</Alert>
          )}

          {!isLoading && error === null && dungeon !== null && (
            <GeneratedDungeonView dungeon={dungeon} />
          )}
        </Box>
      </Box>
    </DmOnlyRoute>
  );
}
