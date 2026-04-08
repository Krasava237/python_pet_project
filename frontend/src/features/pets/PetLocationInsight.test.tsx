import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { getPetLocationInsight } from '../../shared/api/pets'
import PetLocationInsight from './PetLocationInsight'

vi.mock('../../shared/api/pets', () => ({
  getPetLocationInsight: vi.fn(),
}))

describe('PetLocationInsight', () => {
  it('показывает нормализованный адрес после успешной загрузки', async () => {
    vi.mocked(getPetLocationInsight).mockResolvedValue({
      status: 'ok',
      query: 'Moscow Kremlin',
      provider: 'Nominatim',
      attribution: 'Test provider',
      display_name: 'Normalized: Moscow Kremlin',
      lat: 55.7558,
      lon: 37.6173,
      importance: 0.8,
      message: null,
    })

    render(<PetLocationInsight petId={1} />)

    expect(await screen.findByText('Normalized: Moscow Kremlin')).toBeInTheDocument()
  })

  it('показывает graceful degradation при недоступности внешнего API', async () => {
    vi.mocked(getPetLocationInsight).mockResolvedValue({
      status: 'unavailable',
      query: 'Moscow Kremlin',
      provider: 'Nominatim',
      attribution: 'Test provider',
      display_name: null,
      lat: null,
      lon: null,
      importance: null,
      message: 'Nominatim is temporarily unavailable',
    })

    render(<PetLocationInsight petId={2} />)

    expect(
      await screen.findByText(/Nominatim is temporarily unavailable/i),
    ).toBeInTheDocument()
  })
})
