import { startTransition, useState, type FormEvent } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'

import { useAuth } from '../features/auth/useAuth'
import { getApiErrorMessage } from '../shared/api/http'
import Seo from '../shared/seo/Seo'

export function LoginPage() {
  const { isAuthenticated, login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  if (isAuthenticated) {
    return <Navigate to="/" replace />
  }

  const from =
    typeof location.state === 'object' &&
    location.state !== null &&
    'from' in location.state &&
    typeof location.state.from === 'string'
      ? location.state.from
      : '/'

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setIsSubmitting(true)
    setError('')

    try {
      await login({ email, password })
      startTransition(() => {
        navigate(from, { replace: true })
      })
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Не удалось выполнить вход'))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="page-shell">
      <Seo
        canonicalPath="/login"
        description="Вход в приватную часть Pet Finder."
        robots="noindex,nofollow"
        title="Вход | Pet Finder"
      />

      <div className="card">
        <h1>Вход</h1>
        <p className="muted">
          Приватная страница. Для SEO помечена как `noindex`, но используется для управления своими
          объявлениями.
        </p>
        <form className="form-grid" onSubmit={handleSubmit}>
          <label className="field">
            <span>Email</span>
            <input
              autoComplete="username"
              onChange={(event) => setEmail(event.target.value)}
              required
              type="email"
              value={email}
            />
          </label>
          <label className="field">
            <span>Пароль</span>
            <input
              autoComplete="current-password"
              onChange={(event) => setPassword(event.target.value)}
              required
              type="password"
              value={password}
            />
          </label>
          <div className="actions">
            <button disabled={isSubmitting} type="submit">
              {isSubmitting ? 'Вход...' : 'Войти'}
            </button>
          </div>
          {error && <p className="error">{error}</p>}
        </form>
      </div>

      <div className="card">
        <h2>Тестовый админ</h2>
        <p className="muted">admin@local.dev / Admin123!</p>
      </div>
    </section>
  )
}

export default LoginPage
