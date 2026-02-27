"use client";

import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import { useAuth } from "@/domains/auth/hooks/useAuth";

/**
 * Client component rendered inside the protected /game route.
 * Displays a personalized welcome message using the authenticated user's name.
 * This is a placeholder — the chat domain will replace this content later.
 */
export function GameContent(): React.ReactElement {
  const { user, logout } = useAuth();

  return (
    <Box
      className="flex min-h-screen flex-col items-center justify-center gap-6"
      sx={{ backgroundColor: "background.default" }}
    >
      <Typography
        variant="h3"
        component="h1"
        sx={{ color: "text.primary", fontWeight: 700 }}
      >
        Welcome to the realm, {user?.name ?? "Adventurer"}
      </Typography>

      <Typography variant="body1" sx={{ color: "text.secondary" }}>
        Your adventure awaits.
      </Typography>

      <Button
        variant="outlined"
        onClick={logout}
        sx={{ textTransform: "none" }}
      >
        Leave the Realm
      </Button>
    </Box>
  );
}
