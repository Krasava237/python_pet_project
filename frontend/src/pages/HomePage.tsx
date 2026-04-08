import { Link } from 'react-router-dom'

import { useAuth } from '../features/auth/useAuth'
import Seo from '../shared/seo/Seo'

export function HomePage() {
  const { isAuthenticated, user } = useAuth()

  return (
    <section className="stack">
      <Seo
        canonicalPath="/"
        description="Pet Finder помогает публиковать объявления о потерянных и найденных питомцах."
        keywords={[
          'поиск питомцев',
          'потерянные питомцы',
          'найденные питомцы',
          'объявления о животных',
        ]}
        title="Pet Finder | Поиск потерянных и найденных питомцев"
      />

      <div className="card hero-card">
        <div className="hero-copy">
          <h1>Pet Finder</h1>
          <p className="muted">
            Публичная главная страница для SEO и навигации по объявлениям о потерянных и найденных
            питомцах.
          </p>
          <div className="actions">
            <Link to="/pets">Перейти к объявлениям</Link>
            {!isAuthenticated && <Link to="/login">Войти</Link>}
          </div>
        </div>
      </div>

      <div className="card">
        <h2>Состояние сессии</h2>
        {isAuthenticated && user ? (
          <div className="stack">
            <div>Email: {user.email}</div>
            <div>Роль: {user.role}</div>
            <div>ID пользователя: {user.id}</div>
          </div>
        ) : (
          <p className="muted">Гостевая сессия. Авторизация нужна для управления своими объявлениями.</p>
        )}
      </div>
    </section>
  )
}

export default HomePage
