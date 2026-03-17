"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import AddIcon from "@mui/icons-material/Add";
import FolderIcon from "@mui/icons-material/Folder";
import MeetingRoomIcon from "@mui/icons-material/MeetingRoom";
import { useAuthStore, selectUser } from "@/shared/store/auth.store";
import { useAuth } from "@/domains/auth/hooks/useAuth";
import { CreateCampaignWizard } from "@/domains/campaign/components/CreateCampaignWizard";
import { CreateRoomDialog } from "./CreateRoomDialog";
import { JoinRoomPanel } from "./JoinRoomPanel";

/**
 * Main dashboard view rendered after authentication.
 * DMs see buttons to create a campaign or open a room; Players see a panel to join via invite code.
 * The user's role determines which view is displayed.
 */
export function DashboardView(): React.ReactElement {
  const user = useAuthStore(selectUser);
  const { logout } = useAuth();
  const router = useRouter();
  const [campaignWizardOpen, setCampaignWizardOpen] = useState(false);
  const [createRoomOpen, setCreateRoomOpen] = useState(false);

  if (!user) {
    // This state is transient — AuthProvider will redirect to /login.
    return <></>;
  }

  const isDm = user.role === "dm";

  return (
    <Box
      sx={{
        minHeight: "100vh",
        bgcolor: "background.default",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* Top bar */}
      <Box
        component="header"
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          px: { xs: 3, sm: 6 },
          py: 2.5,
          borderBottom: "1px solid",
          borderColor: "divider",
          bgcolor: "background.paper",
        }}
      >
        <Typography
          variant="h6"
          fontWeight={700}
          sx={{ color: "text.primary", letterSpacing: "-0.01em" }}
        >
          DnD Frontend
        </Typography>
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <Typography variant="body2" color="text.secondary">
            {user.name}{" "}
            <Box
              component="span"
              sx={{
                fontSize: "0.7rem",
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: "primary.main",
              }}
            >
              {isDm ? "DM" : "Player"}
            </Box>
          </Typography>
          <Button
            size="small"
            variant="outlined"
            onClick={() => {
              logout();
              router.replace("/login");
            }}
            sx={{ textTransform: "none", borderRadius: 2 }}
          >
            Log out
          </Button>
        </Box>
      </Box>

      {/* Content */}
      <Box
        sx={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          px: { xs: 3, sm: 6 },
          py: 8,
          gap: 4,
        }}
      >
        <Box sx={{ textAlign: "center" }}>
          <Typography
            variant="h4"
            fontWeight={800}
            sx={{ color: "text.primary", mb: 0.75, letterSpacing: "-0.02em" }}
          >
            Welcome back, {user.name}
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {isDm
              ? "Create a campaign and open a room for your players."
              : "Enter an invite code to join a game."}
          </Typography>
        </Box>

        {isDm ? (
          <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap", justifyContent: "center" }}>
            <Button
              variant="outlined"
              size="large"
              startIcon={<FolderIcon />}
              onClick={() => router.push("/campaign")}
              sx={{
                textTransform: "none",
                fontWeight: 600,
                fontSize: "1rem",
                borderRadius: 2.5,
                px: 4,
                py: 1.5,
              }}
            >
              My Campaigns
            </Button>
            <Button
              variant="contained"
              size="large"
              startIcon={<AddIcon />}
              onClick={() => setCampaignWizardOpen(true)}
              sx={{
                textTransform: "none",
                fontWeight: 600,
                fontSize: "1rem",
                borderRadius: 2.5,
                px: 4,
                py: 1.5,
              }}
            >
              Create Campaign
            </Button>
          </Box>
        ) : (
          <Box sx={{ width: "100%", maxWidth: 400 }}>
            <JoinRoomPanel />
          </Box>
        )}

        {isDm && (
          <Button
            variant="text"
            size="small"
            startIcon={<MeetingRoomIcon />}
            onClick={() => router.push("/join")}
            sx={{ textTransform: "none", color: "text.secondary" }}
          >
            Join as player instead
          </Button>
        )}
      </Box>

      {isDm && (
        <CreateCampaignWizard
          open={campaignWizardOpen}
          onClose={() => setCampaignWizardOpen(false)}
          onCreated={(id) => router.push(`/campaign/${id}/world`)}
        />
      )}

      {isDm && (
        <CreateRoomDialog
          open={createRoomOpen}
          onClose={() => setCreateRoomOpen(false)}
        />
      )}
    </Box>
  );
}
