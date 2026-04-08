import type { AuthUser, UserRole } from '../../features/auth/types'

export type Permission =
  | 'pets.read'
  | 'pets.create'
  | 'pets.update_own'
  | 'pets.delete_own'
  | 'pets.upload_photo_own'
  | 'pets.attachments_read_own'
  | 'pets.attachments_write_own'
  | 'pets.attachments_delete_own'
  | 'users.read_self'
  | 'users.read_all'
  | 'roles.manage'

const rolePermissions: Record<UserRole, Permission[]> = {
  guest: ['pets.read'],
  user: [
    'pets.read',
    'pets.create',
    'pets.update_own',
    'pets.delete_own',
    'pets.upload_photo_own',
    'pets.attachments_read_own',
    'pets.attachments_write_own',
    'pets.attachments_delete_own',
    'users.read_self',
  ],
  admin: [
    'pets.read',
    'pets.create',
    'pets.update_own',
    'pets.delete_own',
    'pets.upload_photo_own',
    'pets.attachments_read_own',
    'pets.attachments_write_own',
    'pets.attachments_delete_own',
    'users.read_self',
    'users.read_all',
    'roles.manage',
  ],
}

export function hasRole(user: AuthUser | null, roles: UserRole | UserRole[]) {
  if (!user) {
    return false
  }

  const allowedRoles = Array.isArray(roles) ? roles : [roles]
  return allowedRoles.includes(user.role)
}

export function hasPermission(user: AuthUser | null, permission: Permission) {
  if (!user) {
    return false
  }

  return rolePermissions[user.role].includes(permission)
}

export function canCreatePets(user: AuthUser | null) {
  return hasPermission(user, 'pets.create')
}

export function canManagePet(user: AuthUser | null, ownerId: number) {
  if (!user) {
    return false
  }

  if (user.role === 'admin') {
    return true
  }

  return ownerId === user.id && hasPermission(user, 'pets.update_own')
}

export function canManagePetAttachments(user: AuthUser | null, ownerId: number) {
  if (!user) {
    return false
  }

  if (user.role === 'admin') {
    return true
  }

  return ownerId === user.id && hasPermission(user, 'pets.attachments_write_own')
}
