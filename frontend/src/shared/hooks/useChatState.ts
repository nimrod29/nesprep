/**
 * useChatState hook - manages chat state for a session.
 */

import { useState, useEffect, useCallback, useRef } from "react";
import { getSessionMessages } from "../api";
import {
  wsService,
  setEventHandlers,
  type StatusUpdatePayload,
  type ChatCompletedPayload,
  type PlanCompletedPayload,
  type ErrorPayload,
  type SessionJoinedPayload,
  type WeekPlan,
} from "../websocket";

export interface ChatMessage {
  id: string;
  type: "user" | "assistant" | "status" | "plan";
  content: string;
  weekPlans?: WeekPlan[];
  timestamp: Date;
}

export interface StatusEntry {
  message: string;
  timestamp: Date;
}

export function useChatState(sessionId: number | null) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isAgentTyping, setIsAgentTyping] = useState(false);
  const [statusLog, setStatusLog] = useState<StatusEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isJoined, setIsJoined] = useState(false);
  const sessionIdRef = useRef<string>("");

  // Load existing messages when session changes
  useEffect(() => {
    if (!sessionId) {
      setMessages([]);
      setIsJoined(false);
      return;
    }

    sessionIdRef.current = `session_${sessionId}`;

    const loadMessages = async () => {
      try {
        const apiMessages = await getSessionMessages(sessionId);
        const chatMessages: ChatMessage[] = apiMessages
          .filter((m) => m.role === "user" || m.role === "assistant")
          .map((m) => ({
            id: `msg_${m.id}`,
            type: m.role as "user" | "assistant",
            content: m.content,
            timestamp: new Date(m.created_at),
          }));
        setMessages(chatMessages);
      } catch (err) {
        console.error("Failed to load messages:", err);
      }
    };

    loadMessages();

    // Join the session via WebSocket
    if (wsService.isConnected()) {
      wsService.joinSession({ shift_plan_id: sessionId });
    }
  }, [sessionId]);

  // Set up WebSocket event handlers
  useEffect(() => {
    setEventHandlers({
      onSessionJoined: (payload: SessionJoinedPayload) => {
        console.log("[Chat] Session joined:", payload);
        setIsJoined(true);
      },

      onChatStarted: () => {
        setIsAgentTyping(true);
        setStatusLog([{ message: "חושב...", timestamp: new Date() }]);
        setError(null);
      },

      onStatusUpdate: (payload: StatusUpdatePayload) => {
        setStatusLog((prev) => [
          ...prev,
          { message: payload.message, timestamp: new Date() },
        ]);
      },

      onChatCompleted: (payload: ChatCompletedPayload) => {
        setIsAgentTyping(false);
        setStatusLog([]);

        if (!payload.canceled) {
          const newMessage: ChatMessage = {
            id: `msg_${Date.now()}`,
            type: "assistant",
            content: payload.response,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, newMessage]);
        }
      },

      onPlanCompleted: (payload: PlanCompletedPayload) => {
        const planMessage: ChatMessage = {
          id: `plan_${Date.now()}`,
          type: "plan",
          content: "",
          weekPlans: payload.week_plans,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, planMessage]);
      },

      onError: (payload: ErrorPayload) => {
        setIsAgentTyping(false);
        setStatusLog([]);
        setError(payload.message);
      },
    });
  }, []);

  const sendMessage = useCallback(
    (content: string) => {
      if (!sessionId || !content.trim()) return;

      // Add user message immediately
      const userMessage: ChatMessage = {
        id: `msg_${Date.now()}`,
        type: "user",
        content: content.trim(),
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setError(null);

      // Send via WebSocket
      wsService.sendChatMessage(sessionIdRef.current, content.trim());
    },
    [sessionId]
  );

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    messages,
    isAgentTyping,
    statusLog,
    error,
    isJoined,
    sendMessage,
    clearError,
  };
}
