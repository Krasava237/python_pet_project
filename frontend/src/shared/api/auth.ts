import type { AuthUser, LoginPayload, TokenResponse } from '../../features/auth/types'
import { apiRequest, setAccessToken } from './http'

export async function loginRequest(payload: LoginPayload) {
  const response = await apiRequest<TokenResponse>('/users/login', {
    body: payload,
    method: 'POST',
    skipAuthRefresh: true,
  })

  setAccessToken(response.access_token)
  return response
}

export async function logoutRequest() {
  try {
    return await apiRequest<{ detail: string }>('/users/logout', {
      method: 'POST',
      skipAuthRefresh: true,
    })
  } finally {
    setAccessToken(null)
  }
}

export function fetchCurrentUser() {
  return apiRequest<AuthUser>('/users/me')
}
