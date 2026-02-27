"use client";

import { create } from "zustand";
import { devtools } from "zustand/middleware";
import type { UiState, UiActions } from "./ui.store.types";

// Combined store type merging state shape and actions.
type UiStore = UiState & UiActions;

/**
 * Zustand store for global UI state shared across all domains.
 * Manages sidebar visibility and global loading indicators.
 */
export const useUiStore = create<UiStore>()(
  devtools(
    (set) => ({
      sidebarOpen: false,
      globalLoading: false,

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
    }),
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
