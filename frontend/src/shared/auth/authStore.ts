/**
 * Auth store - internal Zustand store for auth state.
 */

import { create } from "zustand";
import { AUTH_STORAGE_KEY } from "./constants";

interface AuthState {
  managerId: number | null;
  managerName: string | null;
  isLoading: boolean;
  setManager: (id: number, name: string | null) => void;
  clearManager: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  managerId: (() => {
    const stored = localStorage.getItem(AUTH_STORAGE_KEY);
    return stored ? parseInt(stored, 10) : null;
  })(),
  managerName: null,
  isLoading: false,

  setManager: (id, name) => {
    localStorage.setItem(AUTH_STORAGE_KEY, String(id));
    set({ managerId: id, managerName: name });
  },

  clearManager: () => {
    localStorage.removeItem(AUTH_STORAGE_KEY);
    set({ managerId: null, managerName: null });
  },

  setLoading: (loading) => set({ isLoading: loading }),
}));
