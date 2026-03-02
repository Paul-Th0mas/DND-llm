"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Alert from "@mui/material/Alert";
import InputAdornment from "@mui/material/InputAdornment";
import IconButton from "@mui/material/IconButton";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import { registerUser } from "@/domains/auth/services/auth.service";
import { hydrateSession } from "@/domains/auth/services/session.service";

// Shared sx for the primary submit button.
const submitButtonSx = {
  py: 1.25,
  textTransform: "none",
  fontWeight: 600,
  fontSize: "0.9rem",
  borderRadius: 2,
  mt: 0.5,
} as const;

// Shared sx for text fields.
const fieldSx = { "& .MuiOutlinedInput-root": { borderRadius: 2 } } as const;

/**
 * Full-screen registration panel for creating a Dungeon Master account.
 * Registration is DM-only — role is fixed at "dm" and baked into the JWT
 * by the backend at registration time.
 */
export function RegisterPanel(): React.ReactElement {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();

  async function handleSubmit(
    e: React.FormEvent<HTMLFormElement>
  ): Promise<void> {
    e.preventDefault();
    setError(null);

    if (!name.trim() || !email.trim() || !password || !confirm) {
      setError("Please fill in all fields.");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }

    setIsSubmitting(true);
    try {
      // Registration is DM-only; role is fixed and encoded in the issued JWT.
      const { access_token } = await registerUser(name, email, password, "dm");
      await hydrateSession(access_token);
      router.replace("/dashboard");
    } catch {
      setError("Registration failed. The email may already be in use.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        bgcolor: "background.default",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        px: { xs: 3, sm: 6 },
        py: 8,
      }}
    >
      <Box
        sx={{
          width: "100%",
          maxWidth: 420,
          display: "flex",
          flexDirection: "column",
          gap: 3,
        }}
      >
        {/* Heading */}
        <Box>
          <Typography
            variant="h5"
            fontWeight={700}
            sx={{ color: "text.primary", mb: 0.5 }}
          >
            Create a DM account
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Dungeon Masters can create and run game rooms.
          </Typography>
        </Box>

        {/* Registration form */}
        <Box
          component="form"
          onSubmit={handleSubmit}
          noValidate
          sx={{ display: "flex", flexDirection: "column", gap: 2 }}
        >
          {error !== null && (
            <Alert
              severity="error"
              onClose={() => setError(null)}
              sx={{ fontSize: "0.8rem" }}
            >
              {error}
            </Alert>
          )}

          <TextField
            label="Name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            fullWidth
            autoComplete="name"
            size="small"
            sx={fieldSx}
          />

          <TextField
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            fullWidth
            autoComplete="email"
            size="small"
            sx={fieldSx}
          />

          <TextField
            label="Password"
            type={showPassword ? "text" : "password"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            fullWidth
            autoComplete="new-password"
            size="small"
            sx={fieldSx}
            slotProps={{
              input: {
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowPassword((s) => !s)}
                      edge="end"
                      size="small"
                      aria-label={showPassword ? "Hide password" : "Show password"}
                    >
                      {showPassword ? (
                        <VisibilityOffIcon fontSize="small" />
                      ) : (
                        <VisibilityIcon fontSize="small" />
                      )}
                    </IconButton>
                  </InputAdornment>
                ),
              },
            }}
          />

          <TextField
            label="Confirm Password"
            type={showConfirm ? "text" : "password"}
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            fullWidth
            autoComplete="new-password"
            size="small"
            sx={fieldSx}
            slotProps={{
              input: {
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowConfirm((s) => !s)}
                      edge="end"
                      size="small"
                      aria-label={showConfirm ? "Hide password" : "Show password"}
                    >
                      {showConfirm ? (
                        <VisibilityOffIcon fontSize="small" />
                      ) : (
                        <VisibilityIcon fontSize="small" />
                      )}
                    </IconButton>
                  </InputAdornment>
                ),
              },
            }}
          />

          <Button
            type="submit"
            variant="contained"
            fullWidth
            disabled={isSubmitting}
            sx={submitButtonSx}
          >
            {isSubmitting ? "Creating account…" : "Create DM Account"}
          </Button>
        </Box>

        {/* Link back to login */}
        <Typography variant="body2" color="text.secondary" textAlign="center">
          Already have an account?{" "}
          <Link
            href="/login"
            style={{ color: "inherit", fontWeight: 600, textDecoration: "underline" }}
          >
            Sign in
          </Link>
        </Typography>
      </Box>
    </Box>
  );
}
