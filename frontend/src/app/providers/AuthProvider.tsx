import { startTransition, useEffect, useEffectEvent, useState, type ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'

import type { AuthUser, LoginPayload } from '../../features/auth/types'
import { fetchCurrentUser, loginRequest, logoutRequest } from '../../shared/api/auth'
import {
  setAccessToken,
  setUnauthorizedHandler,
  subscribeToAccessToken,
} from '../../shared/api/http'
import { AuthContext } from './AuthContext'

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const navigate = useNavigate()
  const [user, setUser] = useState<AuthUser | null>(null)
  const [accessToken, setAccessTokenState] = useState<string | null>(null)
  const [isBootstrapping, setIsBootstrapping] = useState(true)

  function clearSession() {
    setUser(null)
    setAccessToken(null)
  }

  const clearSessionAndRedirect = useEffectEvent(() => {
    const hadSession = Boolean(user || accessToken)
    clearSession()

    if (hadSession) {
      startTransition(() => {
        navigate('/login', { replace: true })
      })
    }
  })

  const bootstrapSession = useEffectEvent(async () => {
    try {
      const currentUser = await fetchCurrentUser()
      setUser(currentUser)
    } catch {
      clearSession()
    } finally {
      setIsBootstrapping(false)
    }
  })

  useEffect(() => {
    setUnauthorizedHandler(() => {
      clearSessionAndRedirect()
    })

    const unsubscribe = subscribeToAccessToken((token) => {
      setAccessTokenState(token)
    })

    void bootstrapSession()

    return () => {
      setUnauthorizedHandler(null)
      unsubscribe()
    }
  }, [])

  async function login(payload: LoginPayload) {
    const tokenResponse = await loginRequest(payload)
    setAccessToken(tokenResponse.access_token)
    const currentUser = await fetchCurrentUser()
    setUser(currentUser)
    return currentUser
  }

  async function logout() {
    try {
      await logoutRequest()
    } finally {
      clearSession()
      startTransition(() => {
        navigate('/login', { replace: true })
      })
    }
  }

  async function refreshUser() {
    try {
      const currentUser = await fetchCurrentUser()
      setUser(currentUser)
      return currentUser
    } catch {
      clearSession()
      return null
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        accessToken,
        isAuthenticated: Boolean(user),
        isBootstrapping,
        login,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
