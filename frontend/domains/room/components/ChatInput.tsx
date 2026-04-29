"use client";

import { useState } from "react";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import Button from "@mui/material/Button";
import SendIcon from "@mui/icons-material/Send";
import CampaignIcon from "@mui/icons-material/Campaign";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import { useAuthStore, selectUser } from "@/shared/store/auth.store";
import type { UseGameSocketReturn } from "@/domains/room/hooks/useGameSocket";

/** Props for the ChatInput component. */
interface ChatInputProps {
  /** The send function from useGameSocket, used to emit chat and announcement events. */
  readonly send: UseGameSocketReturn["send"];
}

/**
 * Bottom bar for composing and sending chat messages.
 * Uses the Scriptorium "embedded input" style — surface-container-highest
 * background with no explicit border, shifting on focus.
 * DMs also have an "Announce" button that broadcasts a dm_announcement event.
 * Enter key submits as a chat message.
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
        bgcolor: "#f5e7cb",
      }}
    >
      {/* Embedded input container — no explicit border, shifts bg on focus */}
      <Box
        sx={{
          flex: 1,
          position: "relative",
          display: "flex",
          alignItems: "center",
        }}
      >
        {/* Chat icon — decorative left-side affordance */}
        <ChatBubbleOutlineIcon
          sx={{
            position: "absolute",
            left: 14,
            fontSize: "1.1rem",
            color: "#86795e",
            pointerEvents: "none",
            zIndex: 1,
          }}
        />
        <Box
          component="input"
          value={content}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={isDm ? "Whisper to the party or announce..." : "Whisper to the DM or shout to the party..."}
          sx={{
            width: "100%",
            bgcolor: "#f1e1c1",
            border: "none",
            borderRadius: "0.5rem",
            height: 48,
            pl: 5.5,
            pr: 5,
            fontFamily: "var(--font-work-sans), sans-serif",
            fontSize: "0.875rem",
            color: "#3a311b",
            outline: "none",
            transition: "background-color 200ms ease, box-shadow 200ms ease",
            "&::placeholder": {
              fontStyle: "italic",
              color: "#bfb193",
            },
            "&:focus": {
              bgcolor: "#fff8f1",
              boxShadow: "0 0 0 2px rgba(114,90,66,0.3)",
            },
          }}
        />
        {/* Send icon — right-side affordance inside the input */}
        <IconButton
          onClick={handleSendChat}
          disabled={!content.trim()}
          aria-label="Send message"
          size="small"
          sx={{
            position: "absolute",
            right: 6,
            color: "#725a42",
            "&:hover": { bgcolor: "rgba(114,90,66,0.08)" },
            "&.Mui-disabled": { color: "#bfb193" },
          }}
        >
          <SendIcon fontSize="small" />
        </IconButton>
      </Box>

      {/* DM-only announce button — secondary ghost style */}
      {isDm && (
        <Button
          onClick={handleAnnounce}
          disabled={!content.trim()}
          size="small"
          variant="outlined"
          startIcon={<CampaignIcon fontSize="small" />}
          sx={{
            textTransform: "none",
            fontFamily: "var(--font-work-sans), sans-serif",
            fontWeight: 600,
            fontSize: "0.75rem",
            flexShrink: 0,
            color: "#725a42",
            borderColor: "rgba(114,90,66,0.3)",
            borderRadius: "0.375rem",
            "&:hover": { bgcolor: "#fedcbe", borderColor: "#725a42" },
            "&.Mui-disabled": { color: "#bfb193", borderColor: "rgba(191,177,147,0.3)" },
          }}
        >
          Announce
        </Button>
      )}
    </Box>
  );
}
