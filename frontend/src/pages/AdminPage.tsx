import { useEffect, useState } from 'react'

import type { AuthUser, UserRole } from '../features/auth/types'
import { useAuth } from '../features/auth/useAuth'
import { getApiErrorMessage } from '../shared/api/http'
import { getUsers, updateUserRole } from '../shared/api/users'
import Seo from '../shared/seo/Seo'

const availableRoles: UserRole[] = ['guest', 'user', 'admin']

export function AdminPage() {
  const { user } = useAuth()
  const [users, setUsers] = useState<AuthUser[]>([])
  const [draftRoles, setDraftRoles] = useState<Record<number, UserRole>>({})
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [savingUserId, setSavingUserId] = useState<number | null>(null)

  async function loadUsers() {
    setIsLoading(true)
    setError('')

    try {
      const response = await getUsers()
      setUsers(response)
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Не удалось загрузить пользователей'))
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    void loadUsers()
  }, [])

  async function handleSaveRole(targetUser: AuthUser) {
    const nextRole = draftRoles[targetUser.id] ?? targetUser.role
    setSavingUserId(targetUser.id)
    setError('')
    setMessage('')

    try {
      await updateUserRole(targetUser.id, nextRole)
      setMessage(`Роль для ${targetUser.email} обновлена: ${nextRole}`)
      await loadUsers()
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Не удалось обновить роль'))
    } finally {
      setSavingUserId(null)
    }
  }

  return (
    <section className="stack">
      <Seo
        canonicalPath="/admin"
        description="Административный раздел Pet Finder."
        robots="noindex,nofollow"
        title="Админ-панель | Pet Finder"
      />

      <div className="card">
        <h1>Админ-панель</h1>
        <p className="muted">Закрытая страница с управлением ролями пользователей.</p>
      </div>

      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}

      <div className="users-list">
        {isLoading && <p className="muted">Загрузка пользователей...</p>}
        {!isLoading &&
          users.map((listedUser) => {
            const selectedRole = draftRoles[listedUser.id] ?? listedUser.role
            const isCurrentUser = listedUser.id === user?.id

            return (
              <article className="user-row" key={listedUser.id}>
                <div className="row-main">
                  <strong>{listedUser.email}</strong>
                  <span className="muted">текущая роль: {listedUser.role}</span>
                </div>
                <div className="actions">
                  <select
                    disabled={isCurrentUser}
                    onChange={(event) =>
                      setDraftRoles((current) => ({
                        ...current,
                        [listedUser.id]: event.target.value as UserRole,
                      }))
                    }
                    value={selectedRole}
                  >
                    {availableRoles.map((role) => (
                      <option key={role} value={role}>
                        {role}
                      </option>
                    ))}
                  </select>
                  <button
                    disabled={isCurrentUser || savingUserId === listedUser.id}
                    onClick={() => void handleSaveRole(listedUser)}
                    type="button"
                  >
                    {savingUserId === listedUser.id ? 'Сохранение...' : 'Применить'}
                  </button>
                </div>
                {isCurrentUser && (
                  <span className="muted">Смена собственной admin-роли отключена в UI.</span>
                )}
              </article>
            )
          })}
      </div>
    </section>
  )
}

export default AdminPage
