import type { AuthUser, UserRole } from '../../features/auth/types'
import { apiRequest } from './http'

export function getUsers() {
  return apiRequest<AuthUser[]>('/users/')
}

export function updateUserRole(userId: number, role: UserRole) {
  return apiRequest<AuthUser>(`/users/${userId}/role`, {
    body: { role },
    method: 'PATCH',
  })
}
