/**
 * useAuth hook - public API for auth state.
 */

import { useCallback } from "react";
import { useAuthStore } from "./authStore";
import { wsService } from "../websocket";
import { signin, signup, type SignupData, type AuthResponse } from "../api";

export function useAuth() {
  const { managerId, managerName, isLoading, setAuth, clearAuth, setLoading } =
    useAuthStore();

  const handleAuthSuccess = useCallback(
    (data: AuthResponse) => {
      setAuth(data.manager.id, data.manager.name, data.access_token);
      wsService.connect();
      wsService.setAuthToken(data.manager.id);
    },
    [setAuth]
  );

  const login = useCallback(
    async (email: string, password: string) => {
      setLoading(true);
      try {
        const data = await signin(email, password);
        handleAuthSuccess(data);
        return data;
      } finally {
        setLoading(false);
      }
    },
    [setLoading, handleAuthSuccess]
  );

  const signUp = useCallback(
    async (params: SignupData) => {
      setLoading(true);
      try {
        const data = await signup(params);
        handleAuthSuccess(data);
        return data;
      } finally {
        setLoading(false);
      }
    },
    [setLoading, handleAuthSuccess]
  );

  const logout = useCallback(() => {
    wsService.disconnect();
    clearAuth();
  }, [clearAuth]);

  const reconnect = useCallback(() => {
    if (managerId) {
      wsService.connect();
      wsService.setAuthToken(managerId);
    }
  }, [managerId]);

  return {
    managerId,
    managerName,
    isAuthenticated: managerId !== null,
    isLoading,
    login,
    signUp,
    logout,
    reconnect,
  };
}
