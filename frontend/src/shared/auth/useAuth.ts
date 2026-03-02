/**
 * useAuth hook - public API for auth state.
 */

import { useCallback } from "react";
import { useAuthStore } from "./authStore";
import { wsService } from "../websocket";

interface LoginParams {
  managerId?: number;
  name?: string;
}

interface LoginResponse {
  manager_id: number;
  name: string | null;
}

export function useAuth() {
  const { managerId, managerName, isLoading, setManager, clearManager, setLoading } =
    useAuthStore();

  const login = useCallback(
    async (params: LoginParams = {}) => {
      setLoading(true);
      try {
        const response = await fetch("/api/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            manager_id: params.managerId,
            name: params.name,
          }),
        });

        if (!response.ok) {
          throw new Error("Login failed");
        }

        const data: LoginResponse = await response.json();
        setManager(data.manager_id, data.name);

        // Connect WebSocket and set auth token
        wsService.connect();
        wsService.setAuthToken(data.manager_id);

        return data;
      } finally {
        setLoading(false);
      }
    },
    [setManager, setLoading]
  );

  const logout = useCallback(() => {
    wsService.disconnect();
    clearManager();
  }, [clearManager]);

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
    logout,
    reconnect,
  };
}
