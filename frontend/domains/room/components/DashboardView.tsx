"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import Typography from "@mui/material/Typography";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import LogoutIcon from "@mui/icons-material/Logout";
import IconButton from "@mui/material/IconButton";
import PersonAddIcon from "@mui/icons-material/PersonAdd";
import AddCircleIcon from "@mui/icons-material/AddCircle";
import AddBoxIcon from "@mui/icons-material/AddBox";
import { CharacterCard } from "@/domains/character/components/CharacterCard";
import { CampaignCard } from "@/domains/campaign/components/CampaignCard";
import { useAuthStore, selectUser, selectToken } from "@/shared/store/auth.store";
import { useAuth } from "@/domains/auth/hooks/useAuth";
import { CardStyleToggle } from "@/shared/components/CardStyleToggle";
import { CreateCampaignWizard } from "@/domains/campaign/components/CreateCampaignWizard";
import { StartSessionWizard } from "@/domains/campaign/components/StartSessionWizard";
import { useCampaignList } from "@/domains/campaign/hooks/useCampaignList";
import { LobbyTable } from "./LobbyTable";
import { listMyCharacters } from "@/domains/character/services/character.service";
import {
  useCharacterStore,
  selectMyCharacters,
} from "@/domains/character/store/character.store";
import { ApiError } from "@/lib/api/client";

// Tab index constants for readability.
const TAB_LOBBIES = 0 as const;
const TAB_MY_CHARACTERS = 1 as const;
const TAB_CAMPAIGNS = 2 as const;

/**
 * Main dashboard view rendered after authentication.
 * Redesigned with MUI Tabs (US-047):
 *   Tab 0 — Lobbies: existing join-room panel.
 *   Tab 1 — My Characters: list of characters owned by the authenticated user.
 *   Tab 2 — Campaigns (DM only): campaign list and create-campaign wizard.
 * The active tab is local component state — the URL does not change on switch.
 */
export function DashboardView(): React.ReactElement {
  const user = useAuthStore(selectUser);
  const token = useAuthStore(selectToken);
  const { logout } = useAuth();
  const router = useRouter();

  const [activeTab, setActiveTab] = useState<number>(TAB_LOBBIES);
  const [campaignWizardOpen, setCampaignWizardOpen] = useState(false);
  const [sessionWizardCampaignId, setSessionWizardCampaignId] = useState<string | null>(null);

  const { campaigns, isLoading: isCampaignsLoading, error: campaignsError, reload: reloadCampaigns } = useCampaignList(token ?? "");

  // Character list state
  const myCharacters = useCharacterStore(selectMyCharacters);
  const { setMyCharacters } = useCharacterStore();
  const [isLoadingCharacters, setIsLoadingCharacters] = useState(false);
  const [characterError, setCharacterError] = useState<string | null>(null);
  // Track whether we have already fetched for this session.
  const [charactersFetched, setCharactersFetched] = useState(false);

  const fetchMyCharacters = useCallback(async (): Promise<void> => {
    if (!token) return;
    setIsLoadingCharacters(true);
    setCharacterError(null);

    try {
      const data = await listMyCharacters(token);
      setMyCharacters(data.characters);
      setCharactersFetched(true);
    } catch (err: unknown) {
      if (err instanceof ApiError && err.status !== 401) {
        setCharacterError("Could not load your characters. Please try again.");
      }
    } finally {
      setIsLoadingCharacters(false);
    }
  }, [token, setMyCharacters]);

  // Fetch characters when the user first switches to the My Characters tab.
  // The result is cached in the Zustand store; subsequent tab switches do not
  // re-fetch within the same dashboard session.
  useEffect(() => {
    if (activeTab === TAB_MY_CHARACTERS && !charactersFetched && !isLoadingCharacters) {
      void fetchMyCharacters();
    }
  }, [activeTab, charactersFetched, isLoadingCharacters, fetchMyCharacters]);

  if (!user) {
    // Transient state — AuthProvider will redirect to /login.
    return <></>;
  }

  const isDm = user.role === "dm";

  // Nav items for the Scriptorium top navigation.
  const navItems = [
    { label: "Lobbies", tab: TAB_LOBBIES },
    { label: "My Characters", tab: TAB_MY_CHARACTERS },
    ...(isDm ? [{ label: "Campaigns", tab: TAB_CAMPAIGNS }] : []),
  ];

  // Heading and subtitle text for the currently active tab.
  const tabHeadings: Record<
    number,
    { title: string; subtitle: string; italic?: boolean }
  > = {
    [TAB_LOBBIES]: { title: "Open Lobbies", subtitle: "Digital Scriptorium Dashboard" },
    [TAB_MY_CHARACTERS]: { title: "My Characters", subtitle: "Your chronicle of heroes and legends across the realms." },
    [TAB_CAMPAIGNS]: {
      title: "The Grand Chronicles",
      subtitle: "Managing your active realms and legends",
      italic: true,
    },
  };
  const heading = tabHeadings[activeTab] ?? tabHeadings[TAB_LOBBIES];

  return (
    <Box
      sx={{
        minHeight: "100vh",
        bgcolor: "#fff8f1",
        display: "flex",
        flexDirection: "column",
        position: "relative",
      }}
    >
      {/* Ambient background gradients — decorative, pointer-events-none */}
      <Box
        sx={{
          position: "fixed",
          top: 0,
          right: 0,
          zIndex: 0,
          width: "40vw",
          height: "614px",
          background: "linear-gradient(225deg, #f9ecd5, transparent)",
          opacity: 0.4,
          pointerEvents: "none",
          borderBottomLeftRadius: "50%",
        }}
      />
      <Box
        sx={{
          position: "fixed",
          bottom: 0,
          left: 0,
          zIndex: 0,
          width: "30vw",
          height: "409px",
          background: "linear-gradient(45deg, rgba(241,225,193,0.3), transparent)",
          opacity: 0.3,
          pointerEvents: "none",
        }}
      />

      {/* Top navigation bar */}
      <Box
        component="header"
        sx={{
          position: "sticky",
          top: 0,
          zIndex: 50,
          bgcolor: "#fff8f1",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          px: { xs: 3, sm: 6 },
          py: 2,
        }}
      >
        {/* Brand — Newsreader serif */}
        <Typography
          sx={{
            fontFamily: "var(--font-newsreader), serif",
            fontSize: "1.25rem",
            fontWeight: 700,
            color: "#3a311b",
            letterSpacing: "-0.02em",
          }}
        >
          Dungeons &amp; Droids
        </Typography>

        {/* Navigation links */}
        <Box
          component="nav"
          sx={{ display: { xs: "none", md: "flex" }, gap: 4, alignItems: "center" }}
        >
          {navItems.map(({ label, tab }) => {
            const isActive = activeTab === tab;
            return (
              <Box
                key={tab}
                component="button"
                onClick={() => setActiveTab(tab)}
                sx={{
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  fontFamily: "var(--font-work-sans), sans-serif",
                  fontSize: "0.8rem",
                  fontWeight: isActive ? 700 : 400,
                  letterSpacing: "0.05em",
                  color: isActive ? "#725a42" : "#3a311b",
                  borderBottom: isActive ? "2px solid #725a42" : "2px solid transparent",
                  pb: 0.25,
                  transition: "all 150ms ease",
                  "&:hover": {
                    color: "#725a42",
                  },
                }}
              >
                {label}
              </Box>
            );
          })}
        </Box>

        {/* Trailing actions */}
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <CardStyleToggle />
          <IconButton
            size="small"
            title={user.name}
            sx={{ color: "#725a42", "&:hover": { bgcolor: "#fdf2df" } }}
          >
            <AccountCircleIcon />
          </IconButton>
          <IconButton
            size="small"
            title="Log out"
            onClick={() => {
              logout();
              router.replace("/login");
            }}
            sx={{ color: "#725a42", "&:hover": { bgcolor: "#fdf2df" } }}
          >
            <LogoutIcon />
          </IconButton>
        </Box>
      </Box>

      {/* Main content */}
      <Box
        component="main"
        sx={{ flex: 1, maxWidth: "72rem", mx: "auto", width: "100%", px: { xs: 3, sm: 6 }, py: 8, position: "relative", zIndex: 1 }}
      >
        {/* Page heading — large serif */}
        <Box sx={{ mb: 6 }}>
          <Typography
            component="h1"
            sx={{
              fontFamily: "var(--font-newsreader), serif",
              fontSize: { xs: "2.5rem", sm: "3rem" },
              fontWeight: heading.italic === true ? 800 : 600,
              fontStyle: heading.italic === true ? "italic" : "normal",
              color: "#3a311b",
              letterSpacing: "-0.02em",
              lineHeight: 1.1,
              mb: 0.5,
            }}
          >
            {heading.title}
          </Typography>
          <Typography
            sx={{
              fontFamily: "var(--font-work-sans), sans-serif",
              fontSize: "0.7rem",
              fontWeight: 500,
              textTransform: "uppercase",
              letterSpacing: "0.15em",
              color: "#695e45",
            }}
          >
            {heading.subtitle}
          </Typography>
        </Box>

        {/* Tab panels */}
        {/* Lobbies tab — shows the live lobby browser (US-032/US-033) */}
        {activeTab === TAB_LOBBIES && (
          <Box>
            <LobbyTable token={token ?? ""} />
          </Box>
        )}

        {/* My Characters tab (AC5-AC7, AC11-AC12) */}
        {activeTab === TAB_MY_CHARACTERS && (
          <Box>
            {/* Action row — foil-stamp Create Character CTA */}
            <Box sx={{ display: "flex", justifyContent: "flex-end", mb: 4 }}>
              <Button
                component={Link}
                href="/world"
                sx={{
                  textTransform: "uppercase",
                  letterSpacing: "0.1em",
                  fontFamily: "var(--font-work-sans), sans-serif",
                  fontSize: "0.75rem",
                  fontWeight: 700,
                  background: "linear-gradient(135deg, #725a42, #fedcbe)",
                  color: "#fff6f1",
                  px: 4,
                  py: 1.5,
                  borderRadius: "0.375rem",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 1,
                  boxShadow: "0 8px 24px rgba(114,90,66,0.2)",
                  "&:hover": { filter: "brightness(1.1)" },
                  transition: "all 150ms ease",
                }}
              >
                <AddCircleIcon sx={{ fontSize: 18 }} />
                Create Character
              </Button>
            </Box>

            {isLoadingCharacters && (
              <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
                <CircularProgress sx={{ color: "#725a42" }} />
              </Box>
            )}

            {!isLoadingCharacters && characterError !== null && (
              <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
                <Alert severity="error">{characterError}</Alert>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => {
                    setCharactersFetched(false);
                    void fetchMyCharacters();
                  }}
                  sx={{ alignSelf: "flex-start", textTransform: "none" }}
                >
                  Retry
                </Button>
              </Box>
            )}

            {!isLoadingCharacters && characterError === null && charactersFetched && (
              // 2-column grid matching the Scriptorium design.
              <Box
                sx={{
                  display: "grid",
                  gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" },
                  gap: 5,
                }}
              >
                {(myCharacters ?? []).map((character) => (
                  <CharacterCard key={character.id} character={character} />
                ))}

                {/* "Forge a New Hero" — always shown as the last grid item */}
                <Link href="/world" style={{ textDecoration: "none" }}>
                  <Box
                    sx={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      justifyContent: "center",
                      p: 6,
                      // Dashed border using outline-variant at ~30% opacity.
                      border: "2px dashed rgba(191,177,147,0.3)",
                      borderRadius: "0.75rem",
                      bgcolor: "rgba(255,255,255,0.5)",
                      cursor: "pointer",
                      transition: "background-color 200ms ease",
                      "&:hover": { bgcolor: "#fdf2df" },
                      "&:hover .forge-icon": { color: "#725a42", transform: "scale(1.1)" },
                      minHeight: 200,
                    }}
                  >
                    <Box
                      className="forge-icon"
                      sx={{
                        width: 64,
                        height: 64,
                        borderRadius: "50%",
                        bgcolor: "#f9ecd5",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        mb: 2,
                        color: "#bfb193",
                        transition: "color 200ms ease, transform 200ms ease",
                      }}
                    >
                      <PersonAddIcon sx={{ fontSize: 28 }} />
                    </Box>
                    <Typography
                      sx={{
                        fontFamily: "var(--font-newsreader), serif",
                        fontSize: "1.2rem",
                        fontWeight: 700,
                        color: "#3a311b",
                      }}
                    >
                      Forge a New Hero
                    </Typography>
                    <Typography
                      sx={{
                        fontFamily: "var(--font-work-sans), sans-serif",
                        fontSize: "0.8rem",
                        color: "#695e45",
                        mt: 0.5,
                        textAlign: "center",
                      }}
                    >
                      Add a new adventurer to your fellowship.
                    </Typography>
                  </Box>
                </Link>
              </Box>
            )}
          </Box>
        )}

        {/* Campaigns tab — DM only (AC8). Never rendered for players (isDm guard). */}
        {isDm && activeTab === TAB_CAMPAIGNS && (
          <Box>
            {/* Foil-stamp Create Campaign CTA */}
            <Box sx={{ display: "flex", justifyContent: "flex-end", mb: 4 }}>
              <Button
                onClick={() => setCampaignWizardOpen(true)}
                sx={{
                  textTransform: "none",
                  fontFamily: "var(--font-work-sans), sans-serif",
                  fontSize: "0.8rem",
                  fontWeight: 600,
                  background: "linear-gradient(135deg, #725a42, #fedcbe)",
                  color: "#fff6f1",
                  px: 4,
                  py: 1.5,
                  borderRadius: "0.375rem",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 1,
                  boxShadow: "0 8px 24px rgba(114,90,66,0.2)",
                  "&:hover": { opacity: 0.9 },
                  transition: "all 150ms ease",
                }}
              >
                <AddBoxIcon sx={{ fontSize: 18 }} />
                Create Campaign
              </Button>
            </Box>

            {isCampaignsLoading && (
              <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
                <CircularProgress sx={{ color: "#725a42" }} />
              </Box>
            )}

            {!isCampaignsLoading && campaignsError !== null && (
              <Alert
                severity="error"
                action={
                  <Button color="inherit" size="small" onClick={reloadCampaigns}>
                    Retry
                  </Button>
                }
              >
                {campaignsError}
              </Alert>
            )}

            {!isCampaignsLoading && campaignsError === null && campaigns.length === 0 && (
              <Typography
                sx={{
                  fontFamily: "var(--font-work-sans), sans-serif",
                  fontSize: "0.875rem",
                  color: "#bfb193",
                }}
              >
                You have not created any campaigns yet.
              </Typography>
            )}

            {/* Bento grid — 3 columns on lg, 2 on md, 1 on mobile */}
            {!isCampaignsLoading && campaignsError === null && campaigns.length > 0 && (
              <Box
                sx={{
                  display: "grid",
                  gridTemplateColumns: {
                    xs: "1fr",
                    md: "1fr 1fr",
                    lg: "1fr 1fr 1fr",
                  },
                  gap: 4,
                }}
              >
                {campaigns.map((campaign) => (
                  <CampaignCard
                    key={campaign.campaign_id}
                    campaign={campaign}
                    onClick={(id) => router.push(`/campaign/${id}`)}
                    onStartSession={(id) => setSessionWizardCampaignId(id)}
                  />
                ))}
              </Box>
            )}
          </Box>
        )}
      </Box>

      {/* Footer — anchored to the bottom of the page */}
      <Box
        component="footer"
        sx={{
          mt: "auto",
          bgcolor: "#fdf2df",
          borderTop: "1px solid rgba(191,177,147,0.15)",
          px: { xs: 3, sm: 6 },
          py: 4,
          display: "flex",
          flexDirection: { xs: "column", md: "row" },
          alignItems: "center",
          justifyContent: "space-between",
          gap: 2,
          position: "relative",
          zIndex: 1,
        }}
      >
        <Typography
          sx={{
            fontFamily: "var(--font-work-sans), sans-serif",
            fontSize: "0.65rem",
            textTransform: "uppercase",
            letterSpacing: "0.12em",
            color: "rgba(58,49,27,0.6)",
          }}
        >
          &copy; Scriptorium Digital. All rights reserved.
        </Typography>
        <Box sx={{ display: "flex", gap: 4 }}>
          {(["The Ledger", "Privacy Scroll", "Contact Sage"] as const).map(
            (link) => (
              <Typography
                key={link}
                component="span"
                sx={{
                  fontFamily: "var(--font-work-sans), sans-serif",
                  fontSize: "0.65rem",
                  textTransform: "uppercase",
                  letterSpacing: "0.12em",
                  color: "rgba(58,49,27,0.6)",
                  cursor: "pointer",
                  "&:hover": {
                    color: "#725a42",
                    textDecoration: "underline",
                    textDecorationColor: "#725a42",
                  },
                }}
              >
                {link}
              </Typography>
            )
          )}
        </Box>
      </Box>

      {/* Campaign creation wizard — DM only */}
      {isDm && (
        <CreateCampaignWizard
          open={campaignWizardOpen}
          onClose={() => setCampaignWizardOpen(false)}
          onCreated={(id) => {
            setCampaignWizardOpen(false);
            reloadCampaigns();
            router.push(`/campaign/${id}/world`);
          }}
        />
      )}

      {/* Session wizard — opens when a campaign's Start Session is clicked */}
      {isDm && sessionWizardCampaignId !== null && (
        <StartSessionWizard
          open
          onClose={() => {
            setSessionWizardCampaignId(null);
            reloadCampaigns();
          }}
          campaignId={sessionWizardCampaignId}
        />
      )}
    </Box>
  );
}
