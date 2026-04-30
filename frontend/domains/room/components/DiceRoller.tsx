"use client";

import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import ChangeHistoryIcon from "@mui/icons-material/ChangeHistory";
import CropSquareIcon from "@mui/icons-material/CropSquare";
import DiamondIcon from "@mui/icons-material/Diamond";
import PentagonIcon from "@mui/icons-material/Pentagon";
import HexagonIcon from "@mui/icons-material/Hexagon";
import StarOutlineIcon from "@mui/icons-material/StarOutline";
import type { DiceSides } from "@/domains/room/types";
import type { UseGameSocketReturn } from "@/domains/room/hooks/useGameSocket";

/** All die face counts available for rolling, in display order. */
const DICE: readonly DiceSides[] = [4, 6, 8, 10, 12, 20] as const;

/**
 * Returns a geometric icon representing the die's physical shape.
 * Maps each die size to its closest polygon equivalent.
 * @param sides - The number of sides on the die.
 * @returns A MUI SvgIcon element.
 */
function DiceIcon({ sides }: { readonly sides: DiceSides }): React.ReactElement {
  const iconSx = { fontSize: "1.1rem", color: "#725a42" };
  switch (sides) {
    case 4:
      return <ChangeHistoryIcon sx={iconSx} />;
    case 6:
      return <CropSquareIcon sx={iconSx} />;
    case 8:
      return <DiamondIcon sx={iconSx} />;
    case 10:
      return <PentagonIcon sx={iconSx} />;
    case 12:
      return <HexagonIcon sx={iconSx} />;
    case 20:
      return <StarOutlineIcon sx={iconSx} />;
  }
}

/** Props for the DiceRoller component. */
interface DiceRollerProps {
  /** The send function from useGameSocket, used to emit dice_roll events. */
  readonly send: UseGameSocketReturn["send"];
}

/**
 * Horizontal row of die buttons (d4 through d20).
 * Each button shows a geometric polygon icon above the die label.
 * Clicking a button sends a dice_roll event to the server via WebSocket.
 * Background uses surface-container-high (#f5e7cb) to separate from the event feed.
 */
export function DiceRoller({ send }: DiceRollerProps): React.ReactElement {
  function handleRoll(sides: DiceSides): void {
    send({ type: "dice_roll", sides });
  }

  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        gap: 1,
        px: 3,
        py: 1.5,
        bgcolor: "#f5e7cb",
      }}
    >
      {/* Grouped die buttons with shared background container */}
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          bgcolor: "#f1e1c1",
          borderRadius: "0.5rem",
          p: 0.75,
          gap: 0.25,
        }}
      >
        {DICE.map((sides) => (
          <Box
            key={sides}
            component="button"
            onClick={() => handleRoll(sides)}
            sx={{
              width: 44,
              height: 44,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: 0.25,
              bgcolor: "transparent",
              border: "none",
              borderRadius: "0.375rem",
              cursor: "pointer",
              transition: "background-color 150ms ease",
              "&:hover": {
                bgcolor: "#fedcbe",
                "& .dice-label": { color: "#725a42" },
              },
              "&:active": { transform: "scale(0.95)" },
            }}
          >
            <Typography
              className="dice-label"
              sx={{
                fontFamily: "var(--font-work-sans), sans-serif",
                fontSize: "0.6rem",
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.05em",
                color: "#86795e",
                lineHeight: 1,
                transition: "color 150ms ease",
              }}
            >
              d{sides}
            </Typography>
            <DiceIcon sides={sides} />
          </Box>
        ))}
      </Box>
    </Box>
  );
}
