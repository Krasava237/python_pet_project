import { NavLink, Outlet } from 'react-router-dom'

import { useAuth } from '../features/auth/useAuth'
import { hasRole } from '../shared/auth/access'

export function AppShell() {
  const { isAuthenticated, logout, user } = useAuth()

  return (
    <div className="page-shell">
      <header className="topbar">
        <nav aria-label="Основная навигация" className="nav-links">
          <NavLink to="/">Главная</NavLink>
          <NavLink to="/pets">Объявления</NavLink>
          {isAuthenticated && <NavLink to="/me">Профиль</NavLink>}
          {hasRole(user, 'admin') && <NavLink to="/admin">Админ</NavLink>}
        </nav>
        <div className="actions">
          {isAuthenticated ? (
            <>
              <span className="status-badge">
                {user?.email} ({user?.role})
              </span>
              <button onClick={() => void logout()}>Выйти</button>
            </>
          ) : (
            <NavLink to="/login">Войти</NavLink>
          )}
        </div>
      </header>
      <main className="site-main" id="main-content">
        <Outlet />
      </main>
      <footer className="site-footer">
        <p className="muted">
          Pet Finder помогает быстро открыть публичные объявления и перейти к нужному сценарию.
        </p>
      </footer>
    </div>
  )
}
