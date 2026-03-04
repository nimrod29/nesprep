/**
 * Auth store - internal Zustand store for auth state.
 */

import { create } from "zustand";
import { AUTH_STORAGE_KEY, AUTH_TOKEN_KEY } from "./constants";

interface AuthState {
  managerId: number | null;
  managerName: string | null;
  accessToken: string | null;
  isLoading: boolean;
  setAuth: (id: number, name: string | null, token: string) => void;
  clearAuth: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  managerId: (() => {
    const stored = localStorage.getItem(AUTH_STORAGE_KEY);
    return stored ? parseInt(stored, 10) : null;
  })(),
  managerName: null,
  accessToken: localStorage.getItem(AUTH_TOKEN_KEY),
  isLoading: false,

  setAuth: (id, name, token) => {
    localStorage.setItem(AUTH_STORAGE_KEY, String(id));
    localStorage.setItem(AUTH_TOKEN_KEY, token);
    set({ managerId: id, managerName: name, accessToken: token });
  },

  clearAuth: () => {
    localStorage.removeItem(AUTH_STORAGE_KEY);
    localStorage.removeItem(AUTH_TOKEN_KEY);
    set({ managerId: null, managerName: null, accessToken: null });
  },

  setLoading: (loading) => set({ isLoading: loading }),
}));
