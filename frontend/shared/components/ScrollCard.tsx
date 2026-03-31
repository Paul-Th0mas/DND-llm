"use client";

import React, { useId, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";

// Card width threshold below which the wax seal is hidden to prevent
// it from overlapping card content unacceptably.
const SEAL_HIDE_WIDTH_PX = 200 as const;

/**
 * Deterministic frayed-edge polygon vertices in normalised (0–1) coordinates.
 * Each tuple is [x, y]. Values deviate from the rectangle boundary by ±0.008
 * to ±0.015 to produce a subtly torn-parchment edge without randomness
 * (required for SSR/hydration consistency).
 *
 * The polygon traces the card perimeter clockwise starting from top-left,
 * with multiple points along each edge to create the irregular silhouette.
 */
const CLIP_PATH_VERTICES: readonly [number, number][] = [
  [0.008, 0.012],
  [0.25, 0.005],
  [0.5, 0.01],
  [0.75, 0.003],
  [0.992, 0.009],
  [0.995, 0.25],
  [1.0, 0.5],
  [0.993, 0.75],
  [0.988, 0.991],
  [0.75, 0.995],
  [0.5, 0.988],
  [0.25, 0.993],
  [0.012, 0.992],
  [0.005, 0.75],
  [0.0, 0.5],
  [0.007, 0.25],
];

/**
 * Converts an array of normalised [x, y] vertex tuples into a CSS polygon()
 * clip-path string suitable for use in a clipPath element or CSS property.
 * @param vertices - Array of [x, y] tuples with values in the 0–1 range.
 * @returns A polygon() string, e.g. "polygon(0% 0%, 100% 0%, ...)".
 */
function buildClipPath(vertices: readonly [number, number][]): string {
  const points = vertices
    .map(([x, y]) => `${(x * 100).toFixed(3)}% ${(y * 100).toFixed(3)}%`)
    .join(", ");
  return `polygon(${points})`;
}

// Inline SVG path data for the three seal insignia variants.
// All paths are designed for a 20x20 viewBox.
const SEAL_PATHS: Record<"compass" | "dragon" | "crown", string> = {
  // Compass rose: four cardinal direction diamond points.
  compass:
    "M10 2 L12 9 L10 7 L8 9 Z M10 18 L8 11 L10 13 L12 11 Z M2 10 L9 8 L7 10 L9 12 Z M18 10 L11 12 L13 10 L11 8 Z M10 9 A1 1 0 1 0 10 11 A1 1 0 1 0 10 9 Z",
  // Stylised dragon silhouette outline.
  dragon:
    "M4 14 C4 14 3 11 5 9 C5 9 4 7 6 6 C6 6 7 5 9 6 L10 5 L11 6 C13 5 14 6 14 6 C16 7 15 9 15 9 C17 11 16 14 16 14 C15 16 13 16 13 16 L10 17 L7 16 C7 16 5 16 4 14 Z M8 9 C8 9 9 10 10 10 C11 10 12 9 12 9",
  // Simple crown outline: base band with three points.
  crown:
    "M3 14 L3 10 L6 13 L10 7 L14 13 L17 10 L17 14 Z M3 15 L17 15 L17 16 L3 16 Z",
};

/** Props for the ScrollCard component. */
export interface ScrollCardProps {
  readonly title?: string;
  readonly subtitle?: string;
  readonly chips?: React.ReactNode[];
  readonly actions?: React.ReactNode;
  readonly children?: React.ReactNode;
  readonly className?: string;
  readonly sealVariant?: "compass" | "dragon" | "crown";
  readonly staggerIndex?: number;
  readonly onClick?: () => void;
  readonly selected?: boolean;
}

/**
 * A parchment-themed scroll card with frayed edges, 3D rollers, a Framer
 * Motion unroll animation, and an optional wax seal embellishment.
 *
 * This component is the visual foundation of the card system. Domain
 * components should import AppCard rather than this component directly.
 *
 * @param props - ScrollCardProps including title, subtitle, chips, children,
 *   actions, sealVariant, staggerIndex, onClick, and selected.
 */
export function ScrollCard({
  title,
  subtitle,
  chips,
  actions,
  children,
  className,
  sealVariant,
  staggerIndex = 0,
  onClick,
  selected = false,
}: ScrollCardProps): React.ReactElement {
  const uid = useId();
  const filterId = `scroll-noise-${uid}`;
  const clipId = `scroll-clip-${uid}`;
  const reducedMotion = useReducedMotion();

  // Track whether the expand animation has completed so we can lift
  // overflow:hidden and avoid clipping absolutely-positioned elements (seal).
  const [animationDone, setAnimationDone] = useState(false);

  const clipPathValue = buildClipPath(CLIP_PATH_VERTICES);

  // Framer Motion animation variants for the card body.
  // In reduced-motion mode the card renders at full height immediately with
  // a CSS transition fade-in instead of the JS expand animation.
  const cardVariants = reducedMotion
    ? {}
    : {
        hidden: { height: 0, overflow: "hidden" as const },
        visible: {
          height: "auto",
          overflow: "hidden" as const,
          transition: {
            duration: 0.5,
            ease: "easeOut" as const,
            delay: staggerIndex * 0.08,
          },
        },
      };

  // Keyboard handler so the card is operable via Enter and Space when onClick
  // is provided (accessibility requirement: role="button" + keyboard support).
  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>): void => {
    if (onClick && (e.key === "Enter" || e.key === " ")) {
      e.preventDefault();
      onClick();
    }
  };

  const cardBodyStyle: React.CSSProperties = {
    position: "relative",
    // Radial gradient for parchment background.
    background: "radial-gradient(ellipse at center, #EFE9E3 30%, #D9CFC7 100%)",
    clipPath: clipPathValue,
    padding: "1.25rem",
    display: "flex",
    flexDirection: "column",
    gap: "0.5rem",
    // Allow the card body to grow with its content.
    width: "100%",
    boxSizing: "border-box",
    // CSS custom property for descendant body text font.
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    ["--card-font-family" as any]: "var(--font-caudex), 'Libre Baskerville', serif",
    ...(onClick
      ? {
          cursor: "pointer",
          transition: "box-shadow 0.15s ease",
        }
      : {}),
  };

  const outerWrapperStyle: React.CSSProperties = {
    position: "relative",
    display: "inline-flex",
    flexDirection: "column",
    width: "100%",
    // The selected border sits on the outer wrapper, outside the clip-path,
    // so it is not cropped by the frayed-edge geometry.
    border: selected ? "2px solid #7d5e45" : "2px solid transparent",
    borderRadius: "4px",
    boxSizing: "border-box",
  };

  const reducedMotionCardStyle: React.CSSProperties = reducedMotion
    ? {
        animation: "scrollCardFadeIn 0.2s ease forwards",
      }
    : {};

  return (
    <>
      {/* Inline keyframe for reduced-motion fade-in */}
      {reducedMotion && (
        <style>{`
          @keyframes scrollCardFadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
          }
        `}</style>
      )}
      {/* Hidden SVG definitions for clip-path and noise filter */}
      <svg
        style={{ position: "absolute", width: 0, height: 0, overflow: "hidden" }}
        aria-hidden="true"
      >
        <defs>
          <clipPath id={clipId} clipPathUnits="objectBoundingBox">
            <polygon points={CLIP_PATH_VERTICES.map(([x, y]) => `${x},${y}`).join(" ")} />
          </clipPath>
          <filter id={filterId} x="0%" y="0%" width="100%" height="100%">
            <feTurbulence
              type="fractalNoise"
              baseFrequency="0.65"
              numOctaves={3}
              stitchTiles="stitch"
            />
          </filter>
        </defs>
      </svg>

      <div
        style={outerWrapperStyle}
        className={className}
        data-testid="scroll-card"
        {...(onClick
          ? {
              role: "button" as const,
              tabIndex: 0,
              onClick,
              onKeyDown: handleKeyDown,
            }
          : {})}
      >
        {/* Card body — animates height from 0 to auto */}
        <motion.div
          style={{
            overflow: animationDone ? "visible" : "hidden",
            ...reducedMotionCardStyle,
          }}
          variants={cardVariants}
          initial={reducedMotion ? undefined : "hidden"}
          whileInView={reducedMotion ? undefined : "visible"}
          viewport={{ once: true, amount: 0.1 }}
          onAnimationComplete={() => setAnimationDone(true)}
        >
          <div style={cardBodyStyle}>
            {/* Parchment grain noise overlay — purely decorative */}
            <div
              aria-hidden="true"
              style={{
                position: "absolute",
                inset: 0,
                filter: `url(#${filterId})`,
                opacity: 0.05,
                pointerEvents: "none",
                zIndex: 0,
              }}
            />

            {/* Card content sits above the noise overlay */}
            <div style={{ position: "relative", zIndex: 1, display: "flex", flexDirection: "column", gap: "0.5rem" }}>
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

              {/* Actions section with divider */}
              {actions !== undefined && (
                <>
                  <div
                    style={{
                      borderTop: "1px solid #D9CFC7",
                      marginTop: "0.5rem",
                      paddingTop: "0.75rem",
                    }}
                  >
                    {actions}
                  </div>
                </>
              )}
            </div>
          </div>
        </motion.div>

        {/* Wax seal — rendered outside the clip-path container so it is not cropped.
            Hidden when card width is below SEAL_HIDE_WIDTH_PX via a CSS container query. */}
        {sealVariant !== undefined && (
          <div
            style={{
              position: "absolute",
              bottom: -16,
              right: -16,
              width: 50,
              height: 50,
              // CSS blob shape using 8 asymmetric border-radius values.
              borderRadius: "42% 58% 70% 30% / 45% 45% 55% 55%",
              background: "radial-gradient(ellipse at center, #7d5e45 0%, #3a2820 100%)",
              boxShadow:
                "inset 0 2px 4px rgba(255,230,180,0.18), 0 4px 12px rgba(0,0,0,0.45)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              zIndex: 10,
            }}
          >
            <svg
              viewBox="0 0 20 20"
              width={20}
              height={20}
              role="img"
              aria-label={`${sealVariant} seal`}
              style={{ fill: "#D9CFC7" }}
            >
              <path d={SEAL_PATHS[sealVariant]} />
            </svg>
          </div>
        )}
      </div>

      {/* CSS to hide seal on very narrow cards */}
      <style>{`
        [data-testid="scroll-card"] > div:last-child {
          display: flex;
        }
        @container (max-width: ${SEAL_HIDE_WIDTH_PX}px) {
          [data-testid="scroll-card"] > [style*="position: absolute"][style*="bottom: -16"] {
            display: none;
          }
        }
      `}</style>
    </>
  );
}
