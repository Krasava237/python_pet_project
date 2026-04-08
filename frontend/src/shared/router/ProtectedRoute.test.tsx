import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it } from 'vitest'

import { AuthContext } from '../../app/providers/AuthContext'
import { createAuthContextValue } from '../../test/testUtils'
import { ProtectedRoute } from './ProtectedRoute'

describe('ProtectedRoute', () => {
  it('перенаправляет гостя на страницу логина', () => {
    const authValue = createAuthContextValue()

    renderWithRoute(authValue)

    expect(screen.getByText('login-screen')).toBeInTheDocument()
  })

  it('показывает вложенный маршрут для авторизованного пользователя', () => {
    const authValue = createAuthContextValue({
      isAuthenticated: true,
      user: {
        id: 1,
        email: 'member@example.com',
        role: 'user',
        created_at: '2026-04-07T10:00:00Z',
      },
    })

    renderWithRoute(authValue)

    expect(screen.getByText('profile-screen')).toBeInTheDocument()
  })
})

function renderWithRoute(authValue: ReturnType<typeof createAuthContextValue>) {
  return render(
    <AuthContext.Provider value={authValue}>
      <MemoryRouter initialEntries={['/me']}>
        <Routes>
          <Route path="/login" element={<div>login-screen</div>} />
          <Route element={<ProtectedRoute />}>
            <Route path="/me" element={<div>profile-screen</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  )
}
