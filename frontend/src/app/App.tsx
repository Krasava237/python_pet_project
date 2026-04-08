import { Suspense, lazy } from 'react'
import { BrowserRouter, Route, Routes } from 'react-router-dom'

import { AppShell } from '../components/AppShell'
import { ProtectedRoute } from '../shared/router/ProtectedRoute'
import { RoleRoute } from '../shared/router/RoleRoute'
import { AuthProvider } from './providers/AuthProvider'

const AdminPage = lazy(() => import('../pages/AdminPage'))
const HomePage = lazy(() => import('../pages/HomePage'))
const LoginPage = lazy(() => import('../pages/LoginPage'))
const MePage = lazy(() => import('../pages/MePage'))
const NotFoundPage = lazy(() => import('../pages/NotFoundPage'))
const PetDetailsPage = lazy(() => import('../pages/PetDetailsPage'))
const PetsPage = lazy(() => import('../pages/PetsPage'))

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Suspense fallback={<div className="page-shell">Загрузка...</div>}>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route element={<AppShell />}>
              <Route index element={<HomePage />} />
              <Route path="/pets" element={<PetsPage />} />
              <Route path="/pets/:petSlug" element={<PetDetailsPage />} />
              <Route element={<ProtectedRoute />}>
                <Route path="/me" element={<MePage />} />
                <Route element={<RoleRoute allowedRoles={['admin']} />}>
                  <Route path="/admin" element={<AdminPage />} />
                </Route>
              </Route>
            </Route>
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Suspense>
      </AuthProvider>
    </BrowserRouter>
  )
}
