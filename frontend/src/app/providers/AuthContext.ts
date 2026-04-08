import { createContext } from 'react'

import type { AuthUser, LoginPayload } from '../../features/auth/types'

export interface AuthContextValue {
  user: AuthUser | null
  accessToken: string | null
  isAuthenticated: boolean
  isBootstrapping: boolean
  login: (payload: LoginPayload) => Promise<AuthUser>
  logout: () => Promise<void>
  refreshUser: () => Promise<AuthUser | null>
}

export const AuthContext = createContext<AuthContextValue | null>(null)
