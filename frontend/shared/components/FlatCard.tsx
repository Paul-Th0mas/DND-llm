"use client";

import React from "react";
import type { ScrollCardProps } from "./ScrollCard";

/**
 * A flat, no-frills card that accepts the same props as ScrollCard but renders
 * without parchment texture, clip-path, scroll rollers, or Framer Motion animation.
 * Used when the user has toggled the card style to 'flat' via the CardStyleToggle.
 *
 * Domain components should import AppCard rather than this component directly.
 *
 * @param props - ScrollCardProps including title, subtitle, chips, children,
 *   actions, onClick, and selected. sealVariant and staggerIndex are accepted
 *   but produce no visual output in flat mode.
 */
export function FlatCard({
  title,
  subtitle,
  chips,
  actions,
  children,
  className,
  onClick,
  selected = false,
}: ScrollCardProps): React.ReactElement {
  // Keyboard handler: makes the card operable via Enter and Space when onClick
  // is provided (accessibility requirement: role="button" + keyboard support).
  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>): void => {
    if (onClick && (e.key === "Enter" || e.key === " ")) {
      e.preventDefault();
      onClick();
    }
  };

  const containerStyle: React.CSSProperties = {
    background: "#EFE9E3",
    border: selected ? "2px solid var(--mui-palette-primary-main, #1976d2)" : "1px solid #D9CFC7",
    borderRadius: "8px",
    display: "flex",
    flexDirection: "column",
    boxSizing: "border-box",
    width: "100%",
    // CSS custom property for descendant body text font, matching ScrollCard.
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    ["--card-font-family" as any]: "var(--font-caudex), 'Libre Baskerville', serif",
    ...(onClick
      ? {
          cursor: "pointer",
          transition: "border-color 0.15s ease",
        }
      : {}),
  };

  return (
    <div
      style={containerStyle}
      className={className}
      data-testid="flat-card"
      {...(onClick
        ? {
            role: "button" as const,
            tabIndex: 0,
            onClick,
            onKeyDown: handleKeyDown,
          }
        : {})}
      // Hover effect via CSS — border darkens to parchment-400 when onClick present.
      onMouseEnter={
        onClick
          ? (e) => {
              if (!selected) {
                (e.currentTarget as HTMLDivElement).style.borderColor = "#b89a7e";
              }
            }
          : undefined
      }
      onMouseLeave={
        onClick
          ? (e) => {
              if (!selected) {
                (e.currentTarget as HTMLDivElement).style.borderColor = "#D9CFC7";
              }
            }
          : undefined
      }
    >
      <div style={{ padding: "1.25rem", display: "flex", flexDirection: "column", gap: "0.5rem", flex: 1 }}>
        {/* Header: title and subtitle */}
        {(title !== undefined || subtitle !== undefined) && (
          <div>
            {title !== undefined && (
              <h2
                style={{
                  fontFamily: "var(--font-medieval-sharp), serif",
                  fontSize: "1.25rem",
                  color: "#1e1410",
                  margin: 0,
                  lineHeight: 1.3,
                }}
              >
                {title}
              </h2>
            )}
            {subtitle !== undefined && (
              <p
                style={{
                  fontFamily: "var(--font-caudex), 'Libre Baskerville', serif",
                  fontSize: "0.875rem",
                  color: "#5c4230",
                  margin: "0.25rem 0 0",
                }}
              >
                {subtitle}
              </p>
            )}
          </div>
        )}

        {/* Chips row */}
        {chips !== undefined && chips.length > 0 && (
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: "0.5rem",
              alignItems: "center",
            }}
          >
            {chips.map((chip, i) => (
              <React.Fragment key={i}>{chip}</React.Fragment>
            ))}
          </div>
        )}

        {/* Body content */}
        {children}
      </div>

      {/* Actions section with divider — only rendered when actions are provided */}
      {actions !== undefined && (
        <div
          style={{
            borderTop: "1px solid #D9CFC7",
            padding: "0.75rem 1.25rem",
          }}
        >
          {actions}
        </div>
      )}
    </div>
  );
}
