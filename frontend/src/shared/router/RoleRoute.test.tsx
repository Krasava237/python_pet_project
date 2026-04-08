import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it } from 'vitest'

import { AuthContext } from '../../app/providers/AuthContext'
import { createAuthContextValue } from '../../test/testUtils'
import { RoleRoute } from './RoleRoute'

describe('RoleRoute', () => {
  it('не пускает обычного пользователя в admin-раздел', () => {
    const authValue = createAuthContextValue({
      isAuthenticated: true,
      user: {
        id: 2,
        email: 'member@example.com',
        role: 'user',
        created_at: '2026-04-07T10:00:00Z',
      },
    })

    renderWithRoute(authValue)

    expect(screen.getByText('home-screen')).toBeInTheDocument()
  })

  it('пускает администратора в admin-раздел', () => {
    const authValue = createAuthContextValue({
      isAuthenticated: true,
      user: {
        id: 1,
        email: 'admin@example.com',
        role: 'admin',
        created_at: '2026-04-07T10:00:00Z',
      },
    })

    renderWithRoute(authValue)

    expect(screen.getByText('admin-screen')).toBeInTheDocument()
  })
})

function renderWithRoute(authValue: ReturnType<typeof createAuthContextValue>) {
  return render(
    <AuthContext.Provider value={authValue}>
      <MemoryRouter initialEntries={['/admin']}>
        <Routes>
          <Route path="/" element={<div>home-screen</div>} />
          <Route element={<RoleRoute allowedRoles={['admin']} />}>
            <Route path="/admin" element={<div>admin-screen</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  )
}
