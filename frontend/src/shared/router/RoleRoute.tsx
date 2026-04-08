import { Navigate, Outlet } from 'react-router-dom'

import type { UserRole } from '../../features/auth/types'
import { useAuth } from '../../features/auth/useAuth'
import { hasRole } from '../auth/access'

interface RoleRouteProps {
  allowedRoles: UserRole[]
}

export function RoleRoute({ allowedRoles }: RoleRouteProps) {
  const { isBootstrapping, user } = useAuth()

  if (isBootstrapping) {
    return <p className="muted">Checking role...</p>
  }

  if (!hasRole(user, allowedRoles)) {
    return <Navigate to="/" replace />
  }

  return <Outlet />
}
