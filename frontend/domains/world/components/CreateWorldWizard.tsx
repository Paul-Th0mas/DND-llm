"use client";

import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Typography from "@mui/material/Typography";
import { useWorldOptions } from "@/domains/world/hooks/useWorldOptions";

/**
 * Converts a SCREAMING_SNAKE_CASE enum value to Title Case for display.
 * @param value - The enum string to format (e.g. "MEDIEVAL_FANTASY").
 * @returns A human-readable label (e.g. "Medieval Fantasy").
 */
function toLabel(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

/** Props for the WorldBrowserDialog component. */
interface CreateWorldWizardProps {
  readonly open: boolean;
  readonly onClose: () => void;
  /**
   * Called after the DM selects a world and clicks "Proceed".
   * No longer triggers room creation — campaigns handle world association.
   */
  readonly onProceedToCreateRoom: () => void;
}

/**
 * Browse-only dialog that displays the list of admin-seeded worlds.
 * World generation via LLM has been replaced by admin-curated pre-set worlds.
 * DMs browse worlds here for reference; world selection happens inside the Campaign wizard.
 */
export function CreateWorldWizard({
  open,
  onClose,
}: CreateWorldWizardProps): React.ReactElement {
  const { worlds, isLoading, error } = useWorldOptions();

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ fontWeight: 700, pb: 1 }}>Available Worlds</DialogTitle>

      <DialogContent>
        {error !== null && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {isLoading ? (
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 2,
              py: 5,
            }}
          >
            <CircularProgress size={32} />
            <Typography variant="body2" color="text.secondary">
              Loading worlds...
            </Typography>
          </Box>
        ) : (
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 1 }}>
            {worlds.length === 0 && !error && (
              <Typography variant="body2" color="text.secondary">
                No worlds available.
              </Typography>
            )}
            {worlds.map((world) => (
              <Card
                key={world.world_id}
                variant="outlined"
                sx={{ borderRadius: 2 }}
              >
                <CardActionArea sx={{ p: 0 }}>
                  <CardContent>
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                        mb: 0.5,
                      }}
                    >
                      <Typography variant="subtitle1" fontWeight={600}>
                        {world.name}
                      </Typography>
                      <Chip label={toLabel(world.theme)} size="small" />
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {world.description}
                    </Typography>
                  </CardContent>
                </CardActionArea>
              </Card>
            ))}
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2.5 }}>
        <Button
          onClick={onClose}
          sx={{ textTransform: "none", color: "text.secondary" }}
        >
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
}
