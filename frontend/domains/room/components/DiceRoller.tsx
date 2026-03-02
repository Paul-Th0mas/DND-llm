"use client";

import Box from "@mui/material/Box";
import ButtonGroup from "@mui/material/ButtonGroup";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import type { DiceSides } from "@/domains/room/types";
import type { UseGameSocketReturn } from "@/domains/room/hooks/useGameSocket";

/** All die face counts available for rolling, in display order. */
const DICE: readonly DiceSides[] = [4, 6, 8, 10, 12, 20] as const;

/** Props for the DiceRoller component. */
interface DiceRollerProps {
  /** The send function from useGameSocket, used to emit dice_roll events. */
  readonly send: UseGameSocketReturn["send"];
}

/**
 * Horizontal row of die buttons (d4 through d20).
 * Clicking a button sends a dice_roll event to the server via WebSocket.
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
        gap: 1.5,
        px: 3,
        py: 1.5,
        borderTop: "1px solid #D9CFC7",
        bgcolor: "#F9F8F6",
      }}
    >
      <Typography
        variant="caption"
        sx={{
          color: "#7d5e45",
          fontWeight: 600,
          letterSpacing: "0.08em",
          textTransform: "uppercase",
          flexShrink: 0,
          fontSize: "0.65rem",
        }}
      >
        Roll
      </Typography>
      <ButtonGroup size="small" variant="outlined" aria-label="Dice roller">
        {DICE.map((sides) => (
          <Button
            key={sides}
            onClick={() => handleRoll(sides)}
            sx={{
              textTransform: "none",
              fontWeight: 600,
              fontSize: "0.8rem",
              color: "#5c4230",
              borderColor: "#C9B59C",
              minWidth: 44,
              "&:hover": {
                bgcolor: "#a07d60",
                color: "#F9F8F6",
                borderColor: "#a07d60",
              },
            }}
          >
            d{sides}
          </Button>
        ))}
      </ButtonGroup>
    </Box>
  );
}
