/**
 * WebSocket service for agent communication.
 *
 * Singleton service that manages a single WebSocket connection.
 * Handles connection lifecycle, auto-reconnection, and message routing.
 */

import {
  WS_URL,
  ClientMessageTypes,
  RECONNECT_CONFIG,
} from "../constants";
import type {
  ClientMessageType,
  ConnectionState,
  ServerEvent,
  AuthSetTokenPayload,
  SessionJoinPayload,
  ChatSendPayload,
} from "./types";
import { handleServerEvent } from "./eventHandlers";

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private reconnectTimeoutId: ReturnType<typeof setTimeout> | null = null;
  private connectionState: ConnectionState = "disconnected";
  private onConnectionStateChange?: (state: ConnectionState) => void;
  private pendingAuthToken: number | null = null;

  /**
   * Get current connection state.
   */
  getConnectionState(): ConnectionState {
    return this.connectionState;
  }

  /**
   * Set callback for connection state changes.
   */
  setConnectionStateCallback(
    callback: (state: ConnectionState) => void
  ): void {
    this.onConnectionStateChange = callback;
  }

  /**
   * Update connection state and notify listeners.
   */
  private setConnectionState(state: ConnectionState): void {
    this.connectionState = state;
    this.onConnectionStateChange?.(state);
  }

  /**
   * Connect to the WebSocket server.
   */
  connect(): void {
    if (
      this.ws?.readyState === WebSocket.OPEN ||
      this.ws?.readyState === WebSocket.CONNECTING
    ) {
      console.log("[WebSocket] Already connected or connecting");
      return;
    }

    this.setConnectionState("connecting");
    console.log("[WebSocket] Connecting to", WS_URL);

    try {
      this.ws = new WebSocket(WS_URL);
      this.setupEventHandlers();
    } catch (error) {
      console.error("[WebSocket] Failed to create connection:", error);
      this.setConnectionState("disconnected");
      this.scheduleReconnect();
    }
  }

  /**
   * Disconnect from the WebSocket server.
   */
  disconnect(): void {
    console.log("[WebSocket] Disconnecting");
    this.clearReconnectTimeout();
    this.reconnectAttempts = 0;
    this.pendingAuthToken = null;

    if (this.ws) {
      this.ws.onclose = null;
      this.ws.onerror = null;
      this.ws.onmessage = null;
      this.ws.onopen = null;
      this.ws.close();
      this.ws = null;
    }

    this.setConnectionState("disconnected");
  }

  /**
   * Send a message to the server.
   */
  send<T>(type: ClientMessageType, payload: T): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn("[WebSocket] Cannot send message - not connected");
      return;
    }

    const message = { type, ...payload };
    console.log("[WebSocket] Sending:", type);
    this.ws.send(JSON.stringify(message));
  }

  /**
   * Set auth token (manager_id).
   * If not connected yet, stores it to send when connection opens.
   */
  setAuthToken(managerId: number): void {
    this.pendingAuthToken = managerId;
    
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.sendAuthToken(managerId);
    }
  }

  private sendAuthToken(managerId: number): void {
    this.send<AuthSetTokenPayload>(ClientMessageTypes.AUTH_SET_TOKEN, {
      manager_id: managerId,
    });
  }

  /**
   * Join a session.
   */
  joinSession(payload: SessionJoinPayload): void {
    this.send<SessionJoinPayload>(ClientMessageTypes.SESSION_JOIN, payload);
  }

  /**
   * Send a chat message.
   */
  sendChatMessage(sessionId: string, message: string): void {
    this.send<ChatSendPayload>(ClientMessageTypes.CHAT_SEND, {
      session_id: sessionId,
      message,
    });
  }

  /**
   * Check if connected.
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  private setupEventHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = this.handleOpen.bind(this);
    this.ws.onclose = this.handleClose.bind(this);
    this.ws.onerror = this.handleError.bind(this);
    this.ws.onmessage = this.handleMessage.bind(this);
  }

  private handleOpen(): void {
    console.log("[WebSocket] Connected");
    this.setConnectionState("connected");
    this.reconnectAttempts = 0;

    // Send pending auth token if we have one
    if (this.pendingAuthToken !== null) {
      this.sendAuthToken(this.pendingAuthToken);
    }
  }

  private handleClose(event: CloseEvent): void {
    console.log("[WebSocket] Closed:", event.code, event.reason);

    if (this.connectionState !== "disconnected") {
      this.setConnectionState("reconnecting");
      this.scheduleReconnect();
    }
  }

  private handleError(event: Event): void {
    console.error("[WebSocket] Error:", event);
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data) as ServerEvent;
      console.log("[WebSocket] Received:", data.type);
      handleServerEvent(data);
    } catch (error) {
      console.error("[WebSocket] Failed to parse message:", error);
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= RECONNECT_CONFIG.MAX_ATTEMPTS) {
      console.log("[WebSocket] Max reconnection attempts reached");
      this.setConnectionState("disconnected");
      return;
    }

    const delay = Math.min(
      RECONNECT_CONFIG.INITIAL_DELAY *
        Math.pow(
          RECONNECT_CONFIG.BACKOFF_MULTIPLIER,
          this.reconnectAttempts
        ),
      RECONNECT_CONFIG.MAX_DELAY
    );

    console.log(
      `[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts + 1}/${RECONNECT_CONFIG.MAX_ATTEMPTS})`
    );

    this.reconnectTimeoutId = setTimeout(() => {
      this.reconnectAttempts++;
      this.connect();
    }, delay);
  }

  private clearReconnectTimeout(): void {
    if (this.reconnectTimeoutId) {
      clearTimeout(this.reconnectTimeoutId);
      this.reconnectTimeoutId = null;
    }
  }
}

/**
 * Singleton WebSocket service instance.
 */
export const wsService = new WebSocketService();

/**
 * Get the WebSocket service instance.
 */
export function getWebSocketService(): WebSocketService {
  return wsService;
}
