/**
 * WebSocket event handlers.
 *
 * Dispatches server events to the appropriate handlers/stores.
 */

import type {
  ServerEvent,
  SessionJoinedPayload,
  ChatStartedPayload,
  StatusUpdatePayload,
  ChatCompletedPayload,
  ErrorPayload,
} from "./types";
import { ServerEventTypes } from "../constants";

type EventCallback<T> = (payload: T, sessionId: string) => void;

interface EventHandlers {
  onSessionJoined?: EventCallback<SessionJoinedPayload>;
  onChatStarted?: EventCallback<ChatStartedPayload>;
  onStatusUpdate?: EventCallback<StatusUpdatePayload>;
  onChatCompleted?: EventCallback<ChatCompletedPayload>;
  onError?: EventCallback<ErrorPayload>;
}

let handlers: EventHandlers = {};

/**
 * Register event handlers.
 */
export function setEventHandlers(newHandlers: EventHandlers): void {
  handlers = { ...handlers, ...newHandlers };
}

/**
 * Clear all event handlers.
 */
export function clearEventHandlers(): void {
  handlers = {};
}

/**
 * Handle incoming server event.
 */
export function handleServerEvent(event: ServerEvent): void {
  const { type, payload, session_id } = event;

  switch (type) {
    case ServerEventTypes.SESSION_JOINED:
      handlers.onSessionJoined?.(payload as SessionJoinedPayload, session_id);
      break;

    case ServerEventTypes.CHAT_STARTED:
      handlers.onChatStarted?.(payload as ChatStartedPayload, session_id);
      break;

    case ServerEventTypes.STATUS_UPDATE:
      handlers.onStatusUpdate?.(payload as StatusUpdatePayload, session_id);
      break;

    case ServerEventTypes.CHAT_COMPLETED:
      handlers.onChatCompleted?.(payload as ChatCompletedPayload, session_id);
      break;

    case ServerEventTypes.ERROR:
      handlers.onError?.(payload as ErrorPayload, session_id);
      break;

    default:
      console.warn("[WebSocket] Unknown event type:", type);
  }
}
