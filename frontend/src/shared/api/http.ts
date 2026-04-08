const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8001'

type UnauthorizedHandler = (() => void) | null
type AccessTokenListener = (token: string | null) => void

interface ApiRequestOptions extends Omit<RequestInit, 'body'> {
  body?: unknown
  skipAuthRefresh?: boolean
}

export class ApiError extends Error {
  status: number
  data: unknown

  constructor(message: string, status: number, data: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.data = data
  }
}

let accessToken: string | null = null
let unauthorizedHandler: UnauthorizedHandler = null
let refreshPromise: Promise<string | null> | null = null
const accessTokenListeners = new Set<AccessTokenListener>()

export function setUnauthorizedHandler(handler: UnauthorizedHandler) {
  unauthorizedHandler = handler
}

export function subscribeToAccessToken(listener: AccessTokenListener) {
  accessTokenListeners.add(listener)
  return () => {
    accessTokenListeners.delete(listener)
  }
}

export function setAccessToken(token: string | null) {
  accessToken = token
  accessTokenListeners.forEach((listener) => {
    listener(token)
  })
}

function isSerializableJson(body: unknown) {
  return (
    body !== undefined &&
    body !== null &&
    !(body instanceof FormData) &&
    !(body instanceof URLSearchParams) &&
    !(body instanceof Blob) &&
    typeof body !== 'string'
  )
}

function buildBody(body: unknown) {
  if (body === undefined || body === null) {
    return undefined
  }

  if (
    body instanceof FormData ||
    body instanceof URLSearchParams ||
    body instanceof Blob ||
    typeof body === 'string'
  ) {
    return body
  }

  return JSON.stringify(body)
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (response.status === 204) {
    return undefined as T
  }

  const contentType = response.headers.get('content-type') ?? ''
  if (contentType.includes('application/json')) {
    return (await response.json()) as T
  }

  return (await response.text()) as T
}

async function refreshAccessToken() {
  if (!refreshPromise) {
    refreshPromise = (async () => {
      const response = await fetch(`${apiBaseUrl}/users/refresh`, {
        credentials: 'include',
        method: 'POST',
      })

      if (!response.ok) {
        setAccessToken(null)
        return null
      }

      const data = await parseResponse<{ access_token: string }>(response)
      setAccessToken(data.access_token)
      return data.access_token
    })().finally(() => {
      refreshPromise = null
    })
  }

  return refreshPromise
}

export async function apiRequest<T>(
  path: string,
  options: ApiRequestOptions = {},
  attemptRefresh = true,
): Promise<T> {
  const headers = new Headers(options.headers ?? {})

  if (accessToken && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${accessToken}`)
  }

  if (isSerializableJson(options.body) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...options,
    body: buildBody(options.body),
    credentials: 'include',
    headers,
  })

  if (response.status === 401 && attemptRefresh && !options.skipAuthRefresh) {
    const newToken = await refreshAccessToken()
    if (newToken) {
      return apiRequest<T>(path, options, false)
    }
  }

  if (!response.ok) {
    const errorData = await parseResponse<unknown>(response).catch(() => null)
    if (response.status === 401) {
      unauthorizedHandler?.()
    }
    throw new ApiError(`Request failed with status ${response.status}`, response.status, errorData)
  }

  return parseResponse<T>(response)
}

export function getApiErrorMessage(error: unknown, fallback = 'Request failed') {
  if (error instanceof ApiError) {
    const detail =
      typeof error.data === 'object' &&
      error.data !== null &&
      'detail' in error.data &&
      typeof error.data.detail === 'string'
        ? error.data.detail
        : null

    return detail ?? fallback
  }

  if (error instanceof Error && error.message) {
    return error.message
  }

  return fallback
}
