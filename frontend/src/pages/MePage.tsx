import { useEffect, useState } from 'react'

import type { AuthUser } from '../features/auth/types'
import { fetchCurrentUser } from '../shared/api/auth'
import { getApiErrorMessage } from '../shared/api/http'
import Seo from '../shared/seo/Seo'

export function MePage() {
  const [profile, setProfile] = useState<AuthUser | null>(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let isMounted = true

    async function loadProfile() {
      try {
        const me = await fetchCurrentUser()
        if (isMounted) {
          setProfile(me)
        }
      } catch (requestError) {
        if (isMounted) {
          setError(getApiErrorMessage(requestError, 'Не удалось загрузить профиль'))
        }
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    void loadProfile()

    return () => {
      isMounted = false
    }
  }, [])

  return (
    <section className="stack">
      <Seo
        canonicalPath="/me"
        description="Личный кабинет пользователя."
        robots="noindex,nofollow"
        title="Мой профиль | Pet Finder"
      />
      <div className="card">
        <h1>Мой профиль</h1>
        {isLoading && <p className="muted">Загрузка профиля...</p>}
        {error && <p className="error">{error}</p>}
        {profile && (
          <div className="stack">
            <div>Email: {profile.email}</div>
            <div>Роль: {profile.role}</div>
            <div>Создан: {new Date(profile.created_at).toLocaleString('ru-RU')}</div>
          </div>
        )}
      </div>
    </section>
  )
}

export default MePage
