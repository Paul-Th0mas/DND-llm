// Global UI state shape for the shared UI store.
export interface UiState {
  readonly sidebarOpen: boolean;
  readonly globalLoading: boolean;
}

// Actions available on the global UI store.
export interface UiActions {
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
  setGlobalLoading: (loading: boolean) => void;
}
