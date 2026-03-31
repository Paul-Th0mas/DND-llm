"use client";

import { keyframes } from "@emotion/react";
import { useState } from "react";
import Image from "next/image";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Alert from "@mui/material/Alert";
import InputAdornment from "@mui/material/InputAdornment";
import IconButton from "@mui/material/IconButton";
import GoogleIcon from "@mui/icons-material/Google";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import AutoFixHighIcon from "@mui/icons-material/AutoFixHigh";
import ShieldIcon from "@mui/icons-material/Shield";
import GroupsIcon from "@mui/icons-material/Groups";
import { useRouter } from "next/navigation";
import { useAuth } from "@/domains/auth/hooks/useAuth";
import { loginWithEmail } from "@/domains/auth/services/auth.service";
import { hydrateSession } from "@/domains/auth/services/session.service";

// Slow Ken Burns drift — gently zooms and pans the hero image so the panel feels alive.
const kenBurns = keyframes`
  0%   { transform: scale(1)    translate(0,     0    ); }
  35%  { transform: scale(1.07) translate(-1%,   0.6% ); }
  70%  { transform: scale(1.04) translate(0.6%,  -0.8%); }
  100% { transform: scale(1)    translate(0,     0    ); }
`;


/** Which panel of the auth form is active. */
type AuthTab = "signin" | "signup";

/**
 * Decorative horizontal rule with three centered diamonds.
 * Used as a visual separator in the atmospheric left panel.
 */
function Ornament(): React.ReactElement {
  return (
    <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, width: "100%" }}>
      <Box sx={{ flex: 1, height: "1px", bgcolor: "rgba(201,181,156,0.2)" }} />
      <Typography
        aria-hidden="true"
        sx={{ color: "rgba(201,181,156,0.4)", fontSize: "0.55rem", letterSpacing: "0.2em" }}
      >
        ◆ ◆ ◆
      </Typography>
      <Box sx={{ flex: 1, height: "1px", bgcolor: "rgba(201,181,156,0.2)" }} />
    </Box>
  );
}

/**
 * Dark atmospheric left panel with a pixel-art dragon illustration as the background.
 * A semi-transparent dark overlay preserves text legibility over the image.
 * Hidden on small screens — the form panel takes full width on mobile.
 */
function DecorativePanel(): React.ReactElement {
  const features = [
    { Icon: AutoFixHighIcon, text: "Weave powerful spells and shape the world" },
    { Icon: ShieldIcon, text: "Forge your legend across countless realms" },
    { Icon: GroupsIcon, text: "Rally your party and embark on epic quests" },
  ] as const;

  return (
    <Box
      sx={{
        position: "relative",
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        overflow: "hidden",
        px: 6,
        py: 10,
      }}
    >
      {/* Full-bleed hero image wrapped in slow Ken Burns movement */}
      <Box
        aria-hidden="true"
        sx={{
          position: "absolute",
          inset: 0,
          animation: `${kenBurns} 22s ease-in-out infinite`,
          willChange: "transform",
        }}
      >
        <Image
          src="/login-hero.png"
          alt=""
          aria-hidden="true"
          fill
          style={{ objectFit: "cover", objectPosition: "center top" }}
          priority
        />
      </Box>

      {/* Dark scrim so foreground text stays legible */}
      <Box
        aria-hidden="true"
        sx={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(to bottom, rgba(30,20,16,0.55) 0%, rgba(30,20,16,0.72) 60%, rgba(30,20,16,0.88) 100%)",
          pointerEvents: "none",
        }}
      />

{/* Foreground content */}
      <Box
        sx={{
          position: "relative",
          zIndex: 2,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 4,
          maxWidth: 340,
          width: "100%",
        }}
      >
        <Ornament />

        {/* Heading block */}
        <Box sx={{ textAlign: "center" }}>
          <Typography
            sx={{
              fontSize: "0.65rem",
              letterSpacing: "0.38em",
              color: "#b89a7e",
              textTransform: "uppercase",
              mb: 2,
            }}
          >
            Welcome, Adventurer
          </Typography>
          <Typography
            component="p"
            sx={{
              fontSize: "clamp(2.4rem, 4.5vw, 3.4rem)",
              fontWeight: 800,
              color: "#F9F8F6",
              lineHeight: 1.08,
              letterSpacing: "-0.02em",
            }}
          >
            Enter the
            <br />
            <Box component="span" sx={{ color: "#a07d60" }}>
              Realm
            </Box>
          </Typography>
        </Box>

        {/* Atmospheric quote */}
        <Typography
          sx={{
            color: "rgba(201,181,156,0.55)",
            fontSize: "0.8rem",
            fontStyle: "italic",
            textAlign: "center",
            lineHeight: 1.85,
            maxWidth: "26ch",
          }}
        >
          &ldquo;Not all those who wander are lost &mdash; some are simply
          rolling for initiative.&rdquo;
        </Typography>

        {/* Thin rule */}
        <Box
          aria-hidden="true"
          sx={{ width: "100%", height: "1px", bgcolor: "rgba(201,181,156,0.18)" }}
        />

        {/* Feature list */}
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2.5, width: "100%" }}>
          {features.map(({ Icon, text }, i) => (
            <Box key={i} sx={{ display: "flex", alignItems: "flex-start", gap: 1.75 }}>
              <Box
                sx={{
                  mt: 0.2,
                  color: "#a07d60",
                  opacity: 0.85,
                  flexShrink: 0,
                  "& .MuiSvgIcon-root": { fontSize: "1rem" },
                }}
              >
                <Icon fontSize="small" />
              </Box>
              <Typography
                sx={{ color: "rgba(201,181,156,0.7)", fontSize: "0.78rem", lineHeight: 1.65 }}
              >
                {text}
              </Typography>
            </Box>
          ))}
        </Box>

        <Ornament />
      </Box>
    </Box>
  );
}

/** Props for the TabToggle component. */
interface TabToggleProps {
  readonly tab: AuthTab;
  readonly onChange: (tab: AuthTab) => void;
}

/**
 * Pill-style tab toggle for switching between sign-in and account creation.
 * The active tab is filled with the primary parchment color.
 */
function TabToggle({ tab, onChange }: TabToggleProps): React.ReactElement {
  return (
    <Box
      role="tablist"
      sx={{
        display: "flex",
        bgcolor: "#EFE9E3",
        borderRadius: 2.5,
        p: 0.5,
      }}
    >
      {(["signin", "signup"] as const).map((t) => (
        <Button
          key={t}
          role="tab"
          aria-selected={tab === t}
          onClick={() => onChange(t)}
          disableRipple
          sx={{
            flex: 1,
            py: 0.875,
            borderRadius: 2,
            textTransform: "none",
            fontWeight: tab === t ? 600 : 400,
            fontSize: "0.875rem",
            bgcolor: tab === t ? "primary.main" : "transparent",
            color: tab === t ? "primary.contrastText" : "text.secondary",
            transition: "all 0.22s cubic-bezier(0.4, 0, 0.2, 1)",
            boxShadow: tab === t ? "0 1px 6px rgba(0,0,0,0.18)" : "none",
            "&:hover": {
              bgcolor: tab === t ? "primary.dark" : "rgba(0,0,0,0.05)",
            },
          }}
        >
          {t === "signin" ? "Sign In" : "Create Account"}
        </Button>
      ))}
    </Box>
  );
}

/**
 * Horizontal divider with a centered "or continue with email" label.
 * Separates the OAuth button from the email/password fields.
 */
function OrDivider(): React.ReactElement {
  return (
    <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
      <Box sx={{ flex: 1, height: "1px", bgcolor: "divider" }} />
      <Typography
        variant="caption"
        sx={{ color: "text.disabled", letterSpacing: "0.06em", flexShrink: 0 }}
      >
        or continue with email
      </Typography>
      <Box sx={{ flex: 1, height: "1px", bgcolor: "divider" }} />
    </Box>
  );
}

// Shared sx for the Google OAuth button in both forms.
const googleButtonSx = {
  color: "text.primary",
  borderColor: "divider",
  bgcolor: "background.default",
  py: 1.25,
  textTransform: "none",
  fontWeight: 500,
  fontSize: "0.9rem",
  borderRadius: 2,
  "&:hover": {
    bgcolor: "background.paper",
    borderColor: "text.disabled",
    boxShadow: "0 1px 6px rgba(0,0,0,0.1)",
  },
} as const;

// Shared sx for primary submit buttons in both forms.
const submitButtonSx = {
  py: 1.25,
  textTransform: "none",
  fontWeight: 600,
  fontSize: "0.9rem",
  borderRadius: 2,
  mt: 0.5,
} as const;

// Shared sx for all text fields (consistent border radius).
const fieldSx = { "& .MuiOutlinedInput-root": { borderRadius: 2 } } as const;

/** Props shared between the sign-in and sign-up inner forms. */
interface FormProps {
  readonly onLoginWithGoogle: () => void;
}

/**
 * Sign-in form with a Google OAuth button and an email/password fallback.
 */
function SignInForm({ onLoginWithGoogle }: FormProps): React.ReactElement {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();

  async function handleSubmit(
    e: React.FormEvent<HTMLFormElement>
  ): Promise<void> {
    e.preventDefault();
    setError(null);

    if (!email.trim() || !password) {
      setError("Please fill in both fields.");
      return;
    }

    setIsSubmitting(true);
    try {
      const { access_token } = await loginWithEmail(email, password);
      await hydrateSession(access_token);
      router.replace("/dashboard");
    } catch {
      setError("Invalid email or password. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      noValidate
      sx={{ display: "flex", flexDirection: "column", gap: 2 }}
    >
      <Button
        variant="outlined"
        fullWidth
        type="button"
        startIcon={<GoogleIcon sx={{ color: "#4285F4" }} />}
        onClick={onLoginWithGoogle}
        sx={googleButtonSx}
      >
        Continue with Google
      </Button>

      <OrDivider />

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
        autoComplete="current-password"
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

      <Box sx={{ display: "flex", justifyContent: "flex-end", mt: -0.75 }}>
        <Box
          component="button"
          type="button"
          onClick={() =>
            setError("Password reset is not yet available.")
          }
          sx={{
            fontSize: "0.78rem",
            color: "primary.main",
            cursor: "pointer",
            background: "none",
            border: "none",
            p: 0,
            fontFamily: "inherit",
            "&:hover": { color: "primary.dark", textDecoration: "underline" },
          }}
        >
          Forgot password?
        </Box>
      </Box>

      <Button
        type="submit"
        variant="contained"
        fullWidth
        disabled={isSubmitting}
        sx={submitButtonSx}
      >
        {isSubmitting ? "Signing in…" : "Sign In"}
      </Button>

      <Typography variant="body2" color="text.secondary" textAlign="center">
        Want to run games?{" "}
        <Box
          component="a"
          href="/register"
          sx={{
            color: "primary.main",
            fontWeight: 600,
            textDecoration: "none",
            "&:hover": { textDecoration: "underline" },
          }}
        >
          Create a DM account
        </Box>
      </Typography>
    </Box>
  );
}

/**
 * Account-creation prompt that directs users to the dedicated register page.
 * Google OAuth is offered here; email registration (which requires role selection)
 * lives at /register where the full form is presented.
 */
function SignUpForm({ onLoginWithGoogle }: FormProps): React.ReactElement {
  const router = useRouter();

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
      <Button
        variant="outlined"
        fullWidth
        type="button"
        startIcon={<GoogleIcon sx={{ color: "#4285F4" }} />}
        onClick={onLoginWithGoogle}
        sx={googleButtonSx}
      >
        Sign up with Google
      </Button>

      <OrDivider />

      <Typography variant="body2" color="text.secondary" textAlign="center">
        Register with email to create a Dungeon Master account and run your own
        game rooms.
      </Typography>

      <Button
        variant="contained"
        fullWidth
        onClick={() => router.push("/register")}
        sx={submitButtonSx}
      >
        Register as Dungeon Master
      </Button>
    </Box>
  );
}

/**
 * Full-screen authentication panel for the Dungeons and Droids.
 * Split layout: a dark atmospheric DnD-themed panel on the left and
 * a clean tab-based sign-in / sign-up form panel on the right.
 * The left panel is hidden on mobile — the form takes full width instead.
 */
export function LoginPanel(): React.ReactElement {
  const [tab, setTab] = useState<AuthTab>("signin");
  const { login } = useAuth();

  return (
    <Box sx={{ display: "flex", minHeight: "100vh", bgcolor: "background.default" }}>
      {/* Left: atmospheric decorative panel, visible on md+ only */}
      <Box
        sx={{
          display: { xs: "none", md: "flex" },
          width: { md: "44%", lg: "46%" },
          flexShrink: 0,
        }}
      >
        <DecorativePanel />
      </Box>

      {/* Right: auth form panel */}
      <Box
        sx={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          px: { xs: 3, sm: 6 },
          py: 8,
          overflowY: "auto",
        }}
      >
        {/* Mobile-only header shown when the decorative panel is hidden */}
        <Box
          sx={{
            display: { xs: "flex", md: "none" },
            flexDirection: "column",
            alignItems: "center",
            gap: 0.75,
            mb: 4,
            textAlign: "center",
          }}
        >
          <Typography variant="h4" fontWeight={800} sx={{ color: "text.primary" }}>
            Enter the Realm
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Sign in or create an account to begin your adventure.
          </Typography>
        </Box>

        <Box
          sx={{
            width: "100%",
            maxWidth: 400,
            display: "flex",
            flexDirection: "column",
            gap: 3,
          }}
        >
          {/* Desktop contextual heading */}
          <Box sx={{ display: { xs: "none", md: "block" } }}>
            <Typography
              variant="h5"
              fontWeight={700}
              sx={{ color: "text.primary", mb: 0.5 }}
            >
              {tab === "signin" ? "Welcome back" : "Join the adventure"}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {tab === "signin"
                ? "Sign in to continue your journey."
                : "Create an account and begin your quest."}
            </Typography>
          </Box>

          <TabToggle tab={tab} onChange={setTab} />

          {/* Form area — conditional render on tab; each form owns its local state */}
          <Box>
            {tab === "signin" ? (
              <SignInForm onLoginWithGoogle={login} />
            ) : (
              <SignUpForm onLoginWithGoogle={login} />
            )}
          </Box>
        </Box>
      </Box>
    </Box>
  );
}
