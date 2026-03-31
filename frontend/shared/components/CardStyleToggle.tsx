"use client";

import React from "react";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import AutoStoriesIcon from "@mui/icons-material/AutoStories";
import GridViewIcon from "@mui/icons-material/GridView";
import { useUiStore, selectCardStyle } from "@/shared/store/ui.store";

/**
 * An icon button that toggles the global card style preference between
 * 'scroll' (parchment aesthetic) and 'flat' (clean MUI design).
 * Reads and writes to the UI store, which persists the preference in localStorage.
 */
export function CardStyleToggle(): React.ReactElement {
  const cardStyle = useUiStore(selectCardStyle);
  const setCardStyle = useUiStore((state) => state.setCardStyle);

  const isScroll = cardStyle === "scroll";

  const handleToggle = (): void => {
    setCardStyle(isScroll ? "flat" : "scroll");
  };

  return (
    <Tooltip title={isScroll ? "Switch to flat cards" : "Switch to scroll cards"}>
      <IconButton
        onClick={handleToggle}
        size="small"
        aria-label={isScroll ? "Switch to flat cards" : "Switch to scroll cards"}
        sx={{ color: "text.secondary" }}
      >
        {isScroll ? (
          // GridView icon signals the user can switch to the flat grid layout.
          <GridViewIcon fontSize="small" />
        ) : (
          // AutoStories icon signals the user can switch back to scroll style.
          <AutoStoriesIcon fontSize="small" />
        )}
      </IconButton>
    </Tooltip>
  );
}
