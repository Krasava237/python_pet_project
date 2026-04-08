import { Link } from 'react-router-dom'

import Seo from '../shared/seo/Seo'

export function NotFoundPage() {
  return (
    <section className="stack">
      <Seo
        canonicalPath="/404"
        description="Страница не найдена."
        robots="noindex,nofollow"
        title="404 | Pet Finder"
      />
      <div className="card">
        <h1>404</h1>
        <p className="muted">Такой страницы нет. Проверьте адрес или вернитесь к списку объявлений.</p>
        <div className="actions">
          <Link to="/pets">К объявлениям</Link>
          <Link to="/">На главную</Link>
        </div>
      </div>
    </section>
  )
}

export default NotFoundPage
