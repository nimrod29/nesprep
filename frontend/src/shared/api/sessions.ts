/**
 * Sessions API functions.
 */

import { apiFetch } from "./client";

export interface Session {
  id: number;
  manager_id: number;
  title: string | null;
  week_start: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: number;
  role: string;
  content: string;
  created_at: string;
}

interface SessionsListResponse {
  sessions: Session[];
}

interface MessagesListResponse {
  messages: Message[];
}

interface CreateSessionParams {
  manager_id: number;
  title?: string;
  week_start?: string;
}

export async function getSessions(managerId: number): Promise<Session[]> {
  const response = await apiFetch<SessionsListResponse>("/api/sessions", {
    params: { manager_id: managerId },
  });
  return response.sessions;
}

export async function getSession(sessionId: number): Promise<Session> {
  return apiFetch<Session>(`/api/sessions/${sessionId}`);
}

export async function createSession(params: CreateSessionParams): Promise<Session> {
  return apiFetch<Session>("/api/sessions", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

export async function deleteSession(sessionId: number): Promise<void> {
  await apiFetch(`/api/sessions/${sessionId}`, {
    method: "DELETE",
  });
}

export async function getSessionMessages(sessionId: number): Promise<Message[]> {
  const response = await apiFetch<MessagesListResponse>(
    `/api/sessions/${sessionId}/messages`
  );
  return response.messages;
}
