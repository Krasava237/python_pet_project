import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import {
  ApiError,
  apiRequest,
  setAccessToken,
  setUnauthorizedHandler,
  subscribeToAccessToken,
} from './http'

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

describe('apiRequest', () => {
  beforeEach(() => {
    setAccessToken(null)
    setUnauthorizedHandler(null)
  })

  afterEach(() => {
    vi.restoreAllMocks()
    setAccessToken(null)
    setUnauthorizedHandler(null)
  })

  it('обновляет access token через refresh и повторяет запрос', async () => {
    const tokenListener = vi.fn()
    const unsubscribe = subscribeToAccessToken(tokenListener)
    setAccessToken('expired-token')

    const fetchSpy = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(jsonResponse({ detail: 'expired' }, 401))
      .mockResolvedValueOnce(jsonResponse({ access_token: 'fresh-token' }))
      .mockResolvedValueOnce(jsonResponse({ items: [] }))

    const response = await apiRequest<{ items: unknown[] }>('/pets/')

    expect(response.items).toEqual([])
    expect(fetchSpy).toHaveBeenCalledTimes(3)
    expect(tokenListener).toHaveBeenCalledWith('fresh-token')
    unsubscribe()
  })

  it('вызывает обработчик неавторизованной сессии, если refresh тоже завершился 401', async () => {
    const unauthorizedHandler = vi.fn()
    setAccessToken('expired-token')
    setUnauthorizedHandler(unauthorizedHandler)

    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(jsonResponse({ detail: 'expired' }, 401))
      .mockResolvedValueOnce(jsonResponse({ detail: 'refresh failed' }, 401))

    await expect(apiRequest('/users/me')).rejects.toBeInstanceOf(ApiError)
    expect(unauthorizedHandler).toHaveBeenCalledTimes(1)
  })
})
