import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { Pet } from '../features/pets/types'
import { getPet } from '../shared/api/pets'
import PetDetailsPage from './PetDetailsPage'

vi.mock('../shared/api/pets', () => ({
  getPet: vi.fn(),
}))

vi.mock('../features/pets/PetLocationInsight', () => ({
  default: ({ petId }: { petId: number }) => <div data-testid="pet-location">location-{petId}</div>,
}))

const petFixture: Pet = {
  id: 12,
  type: 'dog',
  breed: 'corgi',
  name: 'Lucky',
  color: 'ginger',
  sex: 'male',
  age: '2 years',
  chip_number: '',
  brand_number: '',
  found_date: '2026-04-01',
  found_time: '09:30:00',
  address: 'Main street 7',
  description: 'Friendly dog near the park.',
  status: 'found',
  owner_id: 3,
  photo_url: 'https://example.com/lucky.jpg',
}

describe('PetDetailsPage', () => {
  beforeEach(() => {
    vi.mocked(getPet).mockResolvedValue(petFixture)
  })

  it('renders semantic breadcrumbs and article landmarks for the pet card', async () => {
    render(
      <MemoryRouter initialEntries={['/pets/12-lucky']}>
        <Routes>
          <Route path="/pets/:petSlug" element={<PetDetailsPage />} />
        </Routes>
      </MemoryRouter>,
    )

    const breadcrumbs = await screen.findByRole('navigation', { name: 'Хлебные крошки' })

    expect(breadcrumbs).toBeInTheDocument()
    expect(screen.getByRole('list')).toHaveClass('breadcrumb-list')
    expect(screen.getByRole('heading', { level: 1, name: 'Lucky' })).toBeInTheDocument()
    expect(screen.getByRole('img', { name: 'Фото питомца Lucky' })).toBeInTheDocument()
    expect(screen.getByRole('article')).toBeInTheDocument()
    expect(screen.getByTestId('pet-location')).toHaveTextContent('location-12')
    expect(screen.getByText('Lucky', { selector: 'span[aria-current="page"]' })).toBeInTheDocument()
  })
})
