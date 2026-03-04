export { wsService, getWebSocketService } from "./WebSocketService";
export { setEventHandlers, clearEventHandlers } from "./eventHandlers";
export type {
  ConnectionState,
  ServerEvent,
  SessionJoinedPayload,
  ChatStartedPayload,
  StatusUpdatePayload,
  ChatCompletedPayload,
  PlanCompletedPayload,
  ErrorPayload,
  WeekPlan,
  DayPlan,
} from "./types";
