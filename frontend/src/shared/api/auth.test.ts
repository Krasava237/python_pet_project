import { beforeEach, describe, expect, it, vi } from 'vitest'

import { apiRequest, setAccessToken } from './http'
import { fetchCurrentUser, loginRequest, logoutRequest } from './auth'

vi.mock('./http', () => ({
  apiRequest: vi.fn(),
  setAccessToken: vi.fn(),
}))

describe('auth api helpers', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('сохраняет access token после логина', async () => {
    vi.mocked(apiRequest).mockResolvedValue({
      access_token: 'token-1',
      token_type: 'bearer',
    })

    const response = await loginRequest({
      email: 'member@example.com',
      password: 'User12345!',
    })

    expect(response.access_token).toBe('token-1')
    expect(setAccessToken).toHaveBeenCalledWith('token-1')
  })

  it('очищает access token даже если logout завершается ошибкой', async () => {
    vi.mocked(apiRequest).mockRejectedValue(new Error('logout failed'))

    await expect(logoutRequest()).rejects.toThrow('logout failed')
    expect(setAccessToken).toHaveBeenCalledWith(null)
  })

  it('запрашивает текущего пользователя через /users/me', async () => {
    vi.mocked(apiRequest).mockResolvedValue({
      id: 1,
      email: 'member@example.com',
      role: 'user',
      created_at: '2026-04-07T10:00:00Z',
    })

    await fetchCurrentUser()

    expect(apiRequest).toHaveBeenCalledWith('/users/me')
  })
})
