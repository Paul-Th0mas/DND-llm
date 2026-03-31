"use client";

import { create } from "zustand";
import { devtools, persist, createJSONStorage } from "zustand/middleware";
import type { UiState, UiActions } from "./ui.store.types";

// Combined store type merging state shape and actions.
type UiStore = UiState & UiActions;

// The valid set of card style values. Used to validate persisted data
// and fall back to a safe default if the stored value is unrecognised.
const VALID_CARD_STYLES = new Set<string>(["scroll", "flat"]);

/**
 * Zustand store for global UI state shared across all domains.
 * Manages sidebar visibility, global loading indicators, and the card style preference.
 * The cardStyle field is persisted to localStorage under the key "dnd_card_style".
 */
export const useUiStore = create<UiStore>()(
  devtools(
    persist(
      (set) => ({
        sidebarOpen: false,
        globalLoading: false,
        // Default card style is 'scroll'. The persist middleware will override
        // this with the localStorage value on the client after hydration.
        cardStyle: "scroll" as "scroll" | "flat",

        setSidebarOpen: (open) =>
          set({ sidebarOpen: open }, false, "ui/setSidebarOpen"),

        toggleSidebar: () =>
          set(
            (state) => ({ sidebarOpen: !state.sidebarOpen }),
            false,
            "ui/toggleSidebar"
          ),

        setGlobalLoading: (loading) =>
          set({ globalLoading: loading }, false, "ui/setGlobalLoading"),

        setCardStyle: (style) =>
          set({ cardStyle: style }, false, "ui/setCardStyle"),
      }),
      {
        name: "dnd_card_style",
        // Use a custom storage implementation that is SSR-safe.
        // During server-side rendering typeof window is 'undefined', so we
        // return a no-op storage that never reads or writes anything.
        storage: createJSONStorage(() => {
          if (typeof window === "undefined") {
            return {
              getItem: () => null,
              setItem: () => undefined,
              removeItem: () => undefined,
            };
          }
          return window.localStorage;
        }),
        // Only persist the cardStyle field — sidebar and loading state are
        // session-only and should not survive page reloads.
        partialize: (state) => ({ cardStyle: state.cardStyle }),
        // Validate the persisted value on rehydration. If the stored value is
        // not a recognised card style, reset it to the default 'scroll'.
        merge: (persisted, current) => {
          const p = persisted as Partial<UiStore>;
          const restoredStyle =
            typeof p.cardStyle === "string" && VALID_CARD_STYLES.has(p.cardStyle)
              ? (p.cardStyle as "scroll" | "flat")
              : "scroll";
          return { ...current, cardStyle: restoredStyle };
        },
      }
    ),
    { name: "UiStore" }
  )
);

/**
 * Selects the sidebar open state from the UI store.
 * @param state - The current UI store state.
 * @returns Whether the sidebar is currently open.
 */
export const selectSidebarOpen = (state: UiStore): boolean =>
  state.sidebarOpen;

/**
 * Selects the global loading state from the UI store.
 * @param state - The current UI store state.
 * @returns Whether a global loading operation is in progress.
 */
export const selectGlobalLoading = (state: UiStore): boolean =>
  state.globalLoading;

/**
 * Selects the card style preference from the UI store.
 * @param state - The current UI store state.
 * @returns The active card style: 'scroll' or 'flat'.
 */
export const selectCardStyle = (state: UiStore): "scroll" | "flat" =>
  state.cardStyle;
