/**
 * WebSocket types for shift planning agent communication.
 */

export type ClientMessageType =
  | "auth.set_token"
  | "session.join"
  | "chat.send";

export type ServerEventType =
  | "session.joined"
  | "chat.started"
  | "status.update"
  | "chat.completed"
  | "error";

export type ConnectionState =
  | "disconnected"
  | "connecting"
  | "connected"
  | "reconnecting";

/**
 * Base structure for all client messages.
 */
export interface ClientMessage<T = unknown> {
  type: ClientMessageType;
  [key: string]: unknown;
  payload?: T;
}

/**
 * Payload for auth.set_token message.
 */
export interface AuthSetTokenPayload {
  manager_id: number;
}

/**
 * Payload for session.join message.
 */
export interface SessionJoinPayload {
  session_id?: string;
  shift_plan_id?: number;
  week_start?: string;
  title?: string;
}

/**
 * Payload for chat.send message.
 */
export interface ChatSendPayload {
  session_id: string;
  message: string;
}

/**
 * Base envelope for all server events.
 */
export interface ServerEvent<T = unknown> {
  session_id: string;
  type: ServerEventType;
  ts: number;
  payload: T;
}

/**
 * Server event payloads.
 */
export interface SessionJoinedPayload {
  shift_plan_id: number;
  week_start?: string;
  title?: string;
  new?: boolean;
}

export interface ChatStartedPayload {
  mode?: string;
}

export interface StatusUpdatePayload {
  message: string;
}

export interface ChatCompletedPayload {
  response: string;
  canceled?: boolean;
}

export interface ErrorPayload {
  code: string;
  message: string;
}
