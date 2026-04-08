import type { ReactElement } from 'react'

import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import {
  AuthContext,
  type AuthContextValue,
} from '../app/providers/AuthContext'

export function createAuthContextValue(
  overrides: Partial<AuthContextValue> = {},
): AuthContextValue {
  return {
    user: null,
    accessToken: null,
    isAuthenticated: false,
    isBootstrapping: false,
    login: async () => {
      throw new Error('login is not mocked')
    },
    logout: async () => undefined,
    refreshUser: async () => null,
    ...overrides,
  }
}

export function renderWithProviders(
  ui: ReactElement,
  {
    route = '/',
    authValue = createAuthContextValue(),
  }: {
    route?: string
    authValue?: AuthContextValue
  } = {},
) {
  return render(
    <AuthContext.Provider value={authValue}>
      <MemoryRouter initialEntries={[route]}>{ui}</MemoryRouter>
    </AuthContext.Provider>,
  )
}
