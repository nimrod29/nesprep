/**
 * WebSocket constants matching backend protocol.
 */

function getWebSocketUrl(): string {
  const wsUrl = import.meta.env.VITE_WS_URL;
  if (wsUrl) {
    return wsUrl;
  }

  const apiUrl = import.meta.env.VITE_API_URL;
  if (!apiUrl) {
    return "ws://localhost:8000/ws";
  }

  return apiUrl.replace(/^http/, "ws") + "/ws";
}

export const WS_URL = getWebSocketUrl();

/**
 * Client -> Server message types.
 */
export const ClientMessageTypes = {
  AUTH_SET_TOKEN: "auth.set_token",
  SESSION_JOIN: "session.join",
  CHAT_SEND: "chat.send",
} as const;

/**
 * Server -> Client event types.
 */
export const ServerEventTypes = {
  SESSION_JOINED: "session.joined",
  CHAT_STARTED: "chat.started",
  STATUS_UPDATE: "status.update",
  CHAT_COMPLETED: "chat.completed",
  PLAN_COMPLETED: "plan.completed",
  ERROR: "error",
} as const;

/**
 * Reconnection configuration.
 */
export const RECONNECT_CONFIG = {
  MAX_ATTEMPTS: 5,
  INITIAL_DELAY: 1000,
  MAX_DELAY: 16000,
  BACKOFF_MULTIPLIER: 2,
} as const;
