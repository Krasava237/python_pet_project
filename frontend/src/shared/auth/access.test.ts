import { describe, expect, it } from 'vitest'

import {
  canCreatePets,
  canManagePet,
  canManagePetAttachments,
  hasPermission,
  hasRole,
} from './access'

const member = {
  id: 10,
  email: 'member@example.com',
  role: 'user' as const,
  created_at: '2026-04-07T10:00:00Z',
}

const admin = {
  id: 1,
  email: 'admin@example.com',
  role: 'admin' as const,
  created_at: '2026-04-07T10:00:00Z',
}

describe('access helpers', () => {
  it('проверяет роли и разрешения пользователя', () => {
    expect(hasRole(member, ['user', 'admin'])).toBe(true)
    expect(hasPermission(member, 'pets.create')).toBe(true)
    expect(hasPermission(member, 'roles.manage')).toBe(false)
  })

  it('разрешает владельцу и администратору управлять объявлением', () => {
    expect(canCreatePets(member)).toBe(true)
    expect(canManagePet(member, 10)).toBe(true)
    expect(canManagePet(member, 77)).toBe(false)
    expect(canManagePet(admin, 77)).toBe(true)
  })

  it('разрешает доступ к вложениям только владельцу или администратору', () => {
    expect(canManagePetAttachments(member, 10)).toBe(true)
    expect(canManagePetAttachments(member, 20)).toBe(false)
    expect(canManagePetAttachments(admin, 20)).toBe(true)
  })
})
