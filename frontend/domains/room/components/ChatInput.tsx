"use client";

import { useState } from "react";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import IconButton from "@mui/material/IconButton";
import Button from "@mui/material/Button";
import SendIcon from "@mui/icons-material/Send";
import CampaignIcon from "@mui/icons-material/Campaign";
import { useAuthStore, selectUser } from "@/shared/store/auth.store";
import type { UseGameSocketReturn } from "@/domains/room/hooks/useGameSocket";

/** Props for the ChatInput component. */
interface ChatInputProps {
  /** The send function from useGameSocket, used to emit chat and announcement events. */
  readonly send: UseGameSocketReturn["send"];
}

/**
 * Bottom bar for composing and sending chat messages.
 * DMs also have an "Announce" button to broadcast a dm_announcement event.
 * Enter key submits as a chat message; the Announce button sends a dm_announcement.
 */
export function ChatInput({ send }: ChatInputProps): React.ReactElement {
  const [content, setContent] = useState("");
  const user = useAuthStore(selectUser);
  const isDm = user?.role === "dm";

  function handleSendChat(): void {
    const text = content.trim();
    if (!text) return;
    send({ type: "chat_message", content: text });
    setContent("");
  }

  function handleAnnounce(): void {
    const text = content.trim();
    if (!text) return;
    send({ type: "dm_announcement", content: text });
    setContent("");
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLDivElement>): void {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendChat();
    }
  }

  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        gap: 1,
        px: 2,
        py: 1.5,
        borderTop: "1px solid #D9CFC7",
        bgcolor: "#EFE9E3",
      }}
    >
      <TextField
        value={content}
        onChange={(e) => setContent(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={isDm ? "Chat or announce…" : "Say something…"}
        size="small"
        fullWidth
        multiline
        maxRows={3}
        sx={{
          "& .MuiOutlinedInput-root": {
            borderRadius: 2.5,
            bgcolor: "#F9F8F6",
            fontSize: "0.875rem",
          },
        }}
      />

      {isDm && (
        <Button
          onClick={handleAnnounce}
          disabled={!content.trim()}
          size="small"
          variant="outlined"
          startIcon={<CampaignIcon fontSize="small" />}
          sx={{
            textTransform: "none",
            fontWeight: 600,
            borderRadius: 2,
            flexShrink: 0,
            color: "#5c4230",
            borderColor: "#C9B59C",
            "&:hover": { bgcolor: "rgba(92,66,48,0.06)" },
          }}
        >
          Announce
        </Button>
      )}

      <IconButton
        onClick={handleSendChat}
        disabled={!content.trim()}
        aria-label="Send message"
        sx={{
          color: "#a07d60",
          "&:hover": { bgcolor: "rgba(160,125,96,0.12)" },
          flexShrink: 0,
        }}
      >
        <SendIcon fontSize="small" />
      </IconButton>
    </Box>
  );
}
