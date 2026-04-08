import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { AuthUser } from '../features/auth/types'
import { useAuth } from '../features/auth/useAuth'
import {
  createPet,
  deletePet,
  getMyPets,
  getPets,
  updatePet,
} from '../shared/api/pets'
import PetsPage from './PetsPage'

vi.mock('../features/auth/useAuth', () => ({
  useAuth: vi.fn(),
}))

vi.mock('../shared/api/pets', () => ({
  getPets: vi.fn(),
  getMyPets: vi.fn(),
  createPet: vi.fn(),
  updatePet: vi.fn(),
  deletePet: vi.fn(),
}))

vi.mock('../features/pets/PetForm', () => ({
  default: () => <div data-testid="pet-form">pet-form</div>,
}))

const defaultResponse = {
  items: [],
  meta: {
    page: 1,
    page_size: 9,
    total: 0,
    total_pages: 1,
    has_next: false,
    has_previous: false,
  },
}

const user: AuthUser = {
  id: 1,
  email: 'owner@example.com',
  role: 'user',
  created_at: '2026-04-07T10:00:00Z',
}

describe('PetsPage', () => {
  beforeEach(() => {
    vi.mocked(useAuth).mockReturnValue({
      user,
      accessToken: 'token',
      isAuthenticated: true,
      isBootstrapping: false,
      login: vi.fn(),
      logout: vi.fn(),
      refreshUser: vi.fn(),
    })
    vi.mocked(getPets).mockResolvedValue(defaultResponse)
    vi.mocked(getMyPets).mockResolvedValue(defaultResponse)
    vi.mocked(createPet).mockResolvedValue({} as never)
    vi.mocked(updatePet).mockResolvedValue({} as never)
    vi.mocked(deletePet).mockResolvedValue({ detail: 'Pet deleted' })
  })

  it('загружает публичный список и показывает форму создания для пользователя', async () => {
    renderPage()

    await waitFor(() => expect(getPets).toHaveBeenCalledTimes(1))
    expect(screen.getByTestId('pet-form')).toBeInTheDocument()
  })

  it('передает обновленный поисковый фильтр в API', async () => {
    renderPage()

    const searchField = await screen.findByLabelText(/поиск/i)
    fireEvent.change(searchField, { target: { value: 'luna' } })

    await waitFor(() =>
      expect(getPets).toHaveBeenLastCalledWith(
        expect.objectContaining({
          search: 'luna',
        }),
      ),
    )
  })

  it('показывает текст ошибки при отказе загрузки', async () => {
    vi.mocked(getPets).mockRejectedValueOnce(new Error('Network down'))

    renderPage()

    expect(await screen.findByText('Network down')).toBeInTheDocument()
  })
})

function renderPage() {
  return render(
    <MemoryRouter initialEntries={['/pets']}>
      <Routes>
        <Route path="/pets" element={<PetsPage />} />
      </Routes>
    </MemoryRouter>,
  )
}
