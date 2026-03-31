"use client";

import React from "react";
import { useUiStore, selectCardStyle } from "@/shared/store/ui.store";
import { ScrollCard } from "./ScrollCard";
import { FlatCard } from "./FlatCard";
import type { ScrollCardProps } from "./ScrollCard";

// Re-export the props type so domain consumers can type their own wrappers
// without importing from ScrollCard directly.
export type { ScrollCardProps };

/**
 * The single entry point for card rendering across all domain components.
 * Reads the user's card style preference from the UI store and renders either
 * a ScrollCard (parchment scroll aesthetic) or a FlatCard (clean flat design).
 *
 * Domain components must import AppCard — never ScrollCard or FlatCard directly.
 * This ensures the card style toggle affects all cards simultaneously.
 *
 * @param props - ScrollCardProps forwarded unchanged to the active card variant.
 */
export function AppCard(props: ScrollCardProps): React.ReactElement {
  const cardStyle = useUiStore(selectCardStyle);

  if (cardStyle === "flat") {
    return <FlatCard {...props} />;
  }

  return <ScrollCard {...props} />;
}
