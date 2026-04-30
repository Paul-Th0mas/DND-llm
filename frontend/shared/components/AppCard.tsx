"use client";

import React from "react";
import { ScrollCard, type ScrollCardProps } from "@/shared/components/ScrollCard";

/**
 * Thin facade over ScrollCard that domain components use as their card primitive.
 * Keeps domain code decoupled from ScrollCard's internal implementation.
 *
 * @param props - Same props as ScrollCard.
 */
export function AppCard(props: ScrollCardProps): React.ReactElement {
  return <ScrollCard {...props} />;
}
