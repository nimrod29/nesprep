/**
 * Auth API functions.
 */

import { apiFetch } from "./client";

export interface ManagerInfo {
  id: number;
  email: string;
  name: string;
  role: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  manager: ManagerInfo;
}

export interface SignupData {
  email: string;
  password: string;
  name: string;
  role: string;
}

export async function signin(
  email: string,
  password: string
): Promise<AuthResponse> {
  return apiFetch<AuthResponse>("/api/auth/signin", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function signup(data: SignupData): Promise<AuthResponse> {
  return apiFetch<AuthResponse>("/api/auth/signup", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
