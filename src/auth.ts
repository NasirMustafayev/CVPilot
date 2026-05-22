/**
 * Client-side auth session (JWT in localStorage).
 */

import type { AppMode } from './modeCopy'

const TOKEN_KEY = 'cvpilot_token'
const API_BASE_URL = import.meta.env.VITE_API_URL ?? '/api'

export interface AuthUser {
  id: number
  email: string
  display_name: string
  role: AppMode
  created_at?: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: AuthUser
}

function parseApiError(detail: unknown, fallback: string): string {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === 'string') return item
        if (item && typeof item === 'object' && 'msg' in item) {
          return String((item as { msg: string }).msg)
        }
        return JSON.stringify(item)
      })
      .join('; ')
  }
  if (detail && typeof detail === 'object') {
    return JSON.stringify(detail)
  }
  return fallback
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearSession(): void {
  localStorage.removeItem(TOKEN_KEY)
}

export function authHeaders(): HeadersInit {
  const token = getToken()
  if (!token) return {}
  return { Authorization: `Bearer ${token}` }
}

async function authRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers)
  const token = getToken()
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }
  if (options.body && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  })

  if (!response.ok) {
    let message = 'Request failed'
    try {
      const error = await response.json()
      message = parseApiError(error.detail, message)
    } catch {
      message = response.statusText || message
    }
    throw new Error(message)
  }

  return response.json()
}

export async function registerAccount(payload: {
  email: string
  password: string
  role: AppMode
  display_name: string
}): Promise<AuthResponse> {
  const data = await authRequest<AuthResponse>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
  setToken(data.access_token)
  return data
}

export async function loginAccount(
  email: string,
  password: string,
): Promise<AuthResponse> {
  const data = await authRequest<AuthResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
  setToken(data.access_token)
  return data
}

export async function fetchCurrentUser(): Promise<AuthUser> {
  return authRequest<AuthUser>('/auth/me')
}

export function logout(): void {
  clearSession()
}
