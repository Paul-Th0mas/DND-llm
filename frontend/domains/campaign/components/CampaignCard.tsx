"use client";

import Image from "next/image";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import GroupIcon from "@mui/icons-material/Group";
import type { CampaignSummary } from "@/domains/campaign/types";

/** Props for the CampaignCard component. */
export interface CampaignCardProps {
  /** Campaign summary data from the list endpoint. */
  readonly campaign: CampaignSummary;
  /** Called when the user clicks "Start Session". */
  readonly onStartSession: (campaignId: string) => void;
  /** Called when the card body is clicked (navigate to detail). */
  readonly onClick: (campaignId: string) => void;
}

/**
 * Formats a snake_case tone string into a readable title badge.
 * e.g. "high_fantasy" => "High Fantasy"
 * @param tone - Raw tone string from the backend.
 * @returns Human-readable tone label.
 */
function formatTone(tone: string): string {
  return tone
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * Bento-grid campaign card styled per the Modern Scriptorium design system.
 *
 * Layout:
 *   - h-48 placeholder image, slight desaturate (lifts on hover with scale-110)
 *   - Bottom-to-transparent gradient overlay on the image
 *   - Tone badge: top-right, surface-container-highest pill
 *   - Card body: serif campaign name, world name subtitle, player count, Start Session link
 *
 * Used in the DM "Campaigns" tab of DashboardView.
 */
export function CampaignCard({
  campaign,
  onStartSession,
  onClick,
}: CampaignCardProps): React.ReactElement {
  return (
    <Box
      onClick={() => onClick(campaign.campaign_id)}
      sx={{
        display: "flex",
        flexDirection: "column",
        bgcolor: "#fdf2df",
        borderRadius: "0.5rem",
        overflow: "hidden",
        cursor: "pointer",
        transition: "transform 300ms ease",
        "&:hover": { transform: "translateY(-4px)" },
        "&:hover .campaign-img": {
          transform: "scale(1.1)",
        },
      }}
    >
      {/* Image section — fixed h-48 with overlay and tone badge */}
      <Box sx={{ height: 192, position: "relative", overflow: "hidden" }}>
        <Image
          src="/character-placeholder.png"
          alt={campaign.name}
          fill
          className="campaign-img"
          style={{
            objectFit: "cover",
            filter: "grayscale(0.2)",
            transition: "transform 700ms ease",
          }}
        />
        {/* Bottom gradient — fades into card body color */}
        <Box
          sx={{
            position: "absolute",
            inset: 0,
            background: "linear-gradient(to top, #fdf2df 0%, transparent 60%)",
          }}
        />
        {/* Tone badge */}
        <Box
          sx={{
            position: "absolute",
            top: 16,
            right: 16,
            bgcolor: "#f1e1c1",
            px: 1.5,
            py: 0.5,
            borderRadius: "9999px",
            fontFamily: "var(--font-work-sans), sans-serif",
            fontSize: "0.65rem",
            fontWeight: 600,
            letterSpacing: "0.05em",
            textTransform: "uppercase",
            color: "#725a42",
          }}
        >
          {formatTone(campaign.tone)}
        </Box>
      </Box>

      {/* Card body */}
      <Box
        sx={{
          p: 3,
          display: "flex",
          flexDirection: "column",
          flexGrow: 1,
        }}
      >
        {/* Campaign name — Newsreader serif */}
        <Typography
          component="h3"
          sx={{
            fontFamily: "var(--font-newsreader), serif",
            fontSize: "1.4rem",
            fontWeight: 700,
            color: "#3a311b",
            letterSpacing: "-0.01em",
            mb: 0.5,
          }}
        >
          {campaign.name}
        </Typography>

        {/* World name subtitle */}
        <Typography
          sx={{
            fontFamily: "var(--font-work-sans), sans-serif",
            fontSize: "0.7rem",
            color: "#86795e",
            mb: 2.5,
          }}
        >
          {campaign.world_name ?? "No world assigned"}
        </Typography>

        {/* Footer row — player count + Start Session */}
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mt: "auto",
          }}
        >
          {/* Player count */}
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              gap: 0.5,
              fontFamily: "var(--font-work-sans), sans-serif",
              fontSize: "0.7rem",
              color: "#695e45",
            }}
          >
            <GroupIcon sx={{ fontSize: 14 }} />
            {campaign.player_count}{" "}
            {campaign.player_count === 1 ? "Player" : "Players"}
          </Box>

          {/* Start Session — text link with arrow */}
          <Box
            component="button"
            onClick={(e: React.MouseEvent) => {
              e.stopPropagation();
              onStartSession(campaign.campaign_id);
            }}
            sx={{
              background: "none",
              border: "none",
              cursor: "pointer",
              display: "inline-flex",
              alignItems: "center",
              gap: 0.5,
              fontFamily: "var(--font-work-sans), sans-serif",
              fontSize: "0.8rem",
              fontWeight: 700,
              color: "#725a42",
              p: 0,
              "&:hover": { textDecoration: "underline" },
              "& .fwd-icon": { transition: "transform 150ms ease" },
              "&:hover .fwd-icon": { transform: "translateX(3px)" },
            }}
          >
            Start Session
            <ArrowForwardIcon className="fwd-icon" sx={{ fontSize: 14 }} />
          </Box>
        </Box>
      </Box>
    </Box>
  );
}
