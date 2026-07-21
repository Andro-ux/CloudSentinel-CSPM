import { apiClient } from './client'

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  success: boolean
  data: {
    access_token: string
    refresh_token: string
    token_type: string
    expires_in: number
    user: {
      id: number
      username: string
      organization_id: number
    }
  }
}

export interface RefreshRequest {
  refresh_token: string
}

export interface RefreshResponse {
  success: boolean
  data: {
    access_token: string
    refresh_token: string
    token_type: string
    expires_in: number
  }
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const response = await apiClient.post('/auth/login', new URLSearchParams({
    username,
    password,
  }), {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return response.data
}

export async function refreshTokens(refresh_token: string): Promise<RefreshResponse> {
  const response = await apiClient.post('/auth/refresh', { refresh_token })
  return response.data
}

export async function logout(refresh_token: string): Promise<void> {
  await apiClient.post('/auth/logout', { refresh_token })
}
