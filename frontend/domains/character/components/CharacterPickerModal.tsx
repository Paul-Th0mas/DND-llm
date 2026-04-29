"use client";

import { useCallback, useEffect, useState } from "react";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardContent from "@mui/material/CardContent";
import CircularProgress from "@mui/material/CircularProgress";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Typography from "@mui/material/Typography";
import {
  listMyCharacters,
  linkCharacterToCampaign,
} from "@/domains/character/services/character.service";
import { ApiError } from "@/lib/api/client";
import type { CharacterSummary } from "@/domains/character/types";

/** Props for CharacterPickerModal. */
export interface CharacterPickerModalProps {
  /** Whether the dialog is open. */
  readonly open: boolean;
  /** The UUID of the campaign to link a character to. */
  readonly campaignId: string;
  /** The JWT access token of the authenticated player. */
  readonly token: string;
  /** Called when the dialog should be closed without linking. */
  readonly onClose: () => void;
  /** Called after a character is successfully linked to the campaign. */
  readonly onLinked: () => void;
}

/**
 * Modal dialog that lets a player pick one of their characters and link it
 * to a campaign. Fetches the player's character list on open, renders each
 * as a selectable card, and calls POST /api/v1/campaigns/{campaignId}/characters
 * on confirm. Handles loading, error, and empty states.
 */
export function CharacterPickerModal({
  open,
  campaignId,
  token,
  onClose,
  onLinked,
}: CharacterPickerModalProps): React.ReactElement {
  const [characters, setCharacters] = useState<readonly CharacterSummary[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [isLinking, setIsLinking] = useState(false);
  const [linkError, setLinkError] = useState<string | null>(null);

  const fetchCharacters = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    setFetchError(null);
    try {
      const data = await listMyCharacters(token);
      setCharacters(data.characters);
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setFetchError(`Failed to load your characters: ${err.detail}`);
      } else {
        setFetchError("Failed to load your characters. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  // Fetch when the dialog opens; reset selection state on every open.
  useEffect(() => {
    if (!open) return;
    setSelectedId(null);
    setLinkError(null);
    void fetchCharacters();
  }, [open, fetchCharacters]);

  async function handleConfirm(): Promise<void> {
    if (selectedId === null) return;
    setIsLinking(true);
    setLinkError(null);
    try {
      await linkCharacterToCampaign(campaignId, { character_id: selectedId }, token);
      onLinked();
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        if (err.status === 404) {
          setLinkError("Campaign not found.");
        } else if (err.status === 403) {
          setLinkError("You do not have permission to join this campaign.");
        } else {
          setLinkError(`Failed to link character: ${err.detail}`);
        }
      } else {
        setLinkError("Failed to link character. Please try again.");
      }
    } finally {
      setIsLinking(false);
    }
  }

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: { bgcolor: "#EFE9E3", border: "1px solid #D9CFC7" },
      }}
    >
      <DialogTitle sx={{ color: "#1e1410", fontWeight: 700 }}>
        Join with a Character
      </DialogTitle>

      <DialogContent dividers sx={{ borderColor: "#D9CFC7" }}>
        {isLoading && (
          <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
            <CircularProgress size={28} />
          </Box>
        )}

        {!isLoading && fetchError !== null && (
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <Alert severity="error">{fetchError}</Alert>
            <Button
              size="small"
              variant="outlined"
              onClick={() => void fetchCharacters()}
              sx={{ alignSelf: "flex-start", textTransform: "none" }}
            >
              Retry
            </Button>
          </Box>
        )}

        {!isLoading && fetchError === null && characters.length === 0 && (
          <Typography variant="body2" color="text.secondary">
            You have no characters yet. Create one first before joining a campaign.
          </Typography>
        )}

        {!isLoading && fetchError === null && characters.length > 0 && (
          <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
            {characters.map((character) => {
              const isSelected = character.id === selectedId;
              return (
                <Card
                  key={character.id}
                  variant="outlined"
                  sx={{
                    border: isSelected ? "2px solid #a07d60" : "1px solid #D9CFC7",
                    bgcolor: isSelected ? "#F9F8F6" : "#EFE9E3",
                    transition: "border-color 0.15s, background-color 0.15s",
                  }}
                >
                  <CardActionArea onClick={() => setSelectedId(character.id)}>
                    <CardContent sx={{ py: 1.5, "&:last-child": { pb: 1.5 } }}>
                      <Typography
                        variant="subtitle2"
                        fontWeight={700}
                        sx={{ color: "#1e1410" }}
                      >
                        {character.name}
                      </Typography>
                      <Typography variant="body2" sx={{ color: "#7d5e45" }}>
                        {[character.class_name, character.species_name]
                          .filter(Boolean)
                          .join(" - ")}
                      </Typography>
                    </CardContent>
                  </CardActionArea>
                </Card>
              );
            })}
          </Box>
        )}

        {linkError !== null && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {linkError}
          </Alert>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2, gap: 1 }}>
        <Button
          onClick={onClose}
          disabled={isLinking}
          sx={{ textTransform: "none", color: "#5c4230" }}
        >
          Cancel
        </Button>
        <Button
          variant="contained"
          onClick={() => void handleConfirm()}
          disabled={selectedId === null || isLinking}
          sx={{
            textTransform: "none",
            fontWeight: 600,
            bgcolor: "#7d5e45",
            "&:hover": { bgcolor: "#5c4230" },
            "&:disabled": { bgcolor: "#C9B59C" },
          }}
        >
          {isLinking ? "Joining..." : "Join Campaign"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
