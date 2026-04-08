import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { AuthUser } from '../../features/auth/types'
import { useAuth } from '../../features/auth/useAuth'
import { AuthProvider } from './AuthProvider'
import { fetchCurrentUser, loginRequest, logoutRequest } from '../../shared/api/auth'
import {
  setAccessToken,
  setUnauthorizedHandler,
  subscribeToAccessToken,
} from '../../shared/api/http'

vi.mock('../../shared/api/auth', () => ({
  fetchCurrentUser: vi.fn(),
  loginRequest: vi.fn(),
  logoutRequest: vi.fn(),
}))

vi.mock('../../shared/api/http', () => ({
  setAccessToken: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
  subscribeToAccessToken: vi.fn(),
}))

const member: AuthUser = {
  id: 1,
  email: 'member@example.com',
  role: 'user',
  created_at: '2026-04-07T10:00:00Z',
}

describe('AuthProvider', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(subscribeToAccessToken).mockImplementation(() => () => undefined)
  })

  it('bootstrap-ит текущего пользователя при монтировании', async () => {
    vi.mocked(fetchCurrentUser).mockResolvedValue(member)

    renderProvider()

    expect(await screen.findByText('member@example.com')).toBeInTheDocument()
    expect(setUnauthorizedHandler).toHaveBeenCalled()
  })

  it('выполняет login, refreshUser и logout с переходом на /login', async () => {
    vi.mocked(fetchCurrentUser)
      .mockRejectedValueOnce(new Error('guest'))
      .mockResolvedValueOnce(member)
      .mockResolvedValueOnce(member)
    vi.mocked(loginRequest).mockResolvedValue({
      access_token: 'fresh-token',
      token_type: 'bearer',
    })
    vi.mocked(logoutRequest).mockResolvedValue({ detail: 'User logged out' })

    renderProvider()

    expect(await screen.findByText('guest')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'login-action' }))
    expect(await screen.findByText('member@example.com')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'refresh-action' }))
    await waitFor(() =>
      expect(vi.mocked(fetchCurrentUser).mock.calls.length).toBeGreaterThanOrEqual(3),
    )

    fireEvent.click(screen.getByRole('button', { name: 'logout-action' }))
    expect(setAccessToken).toHaveBeenCalledWith(null)
    expect(await screen.findByText('login-screen')).toBeInTheDocument()
  })
})

function renderProvider() {
  return render(
    <MemoryRouter initialEntries={['/']}>
      <Routes>
        <Route
          path="/"
          element={
            <AuthProvider>
              <AuthConsumer />
            </AuthProvider>
          }
        />
        <Route path="/login" element={<div>login-screen</div>} />
      </Routes>
    </MemoryRouter>,
  )
}

function AuthConsumer() {
  const auth = useAuth()

  return (
    <div>
      <div>{auth.user?.email ?? 'guest'}</div>
      <button
        onClick={() =>
          void auth.login({
            email: 'member@example.com',
            password: 'User12345!',
          })
        }
        type="button"
      >
        login-action
      </button>
      <button onClick={() => void auth.refreshUser()} type="button">
        refresh-action
      </button>
      <button onClick={() => void auth.logout()} type="button">
        logout-action
      </button>
    </div>
  )
}
