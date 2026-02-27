"use client";

import Button from "@mui/material/Button";
import GoogleIcon from "@mui/icons-material/Google";
import { useAuth } from "@/domains/auth/hooks/useAuth";

/**
 * DnD-themed sign-in button that initiates Google OAuth.
 * Clicking triggers a full browser navigation to the backend OAuth endpoint.
 * Production note: ensure the backend OAuth redirect URI uses HTTPS.
 */
export function SignInButton(): React.ReactElement {
  const { login } = useAuth();

  return (
    <Button
      variant="contained"
      size="large"
      startIcon={<GoogleIcon />}
      onClick={login}
      sx={{
        backgroundColor: "primary.main",
        "&:hover": { backgroundColor: "primary.dark" },
        px: 4,
        py: 1.5,
        fontSize: "1rem",
        fontWeight: 600,
        textTransform: "none",
        borderRadius: 2,
      }}
    >
      Continue with Google
    </Button>
  );
}
