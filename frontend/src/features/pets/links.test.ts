import { describe, expect, it } from 'vitest'

import { buildPetPath, getPetIdFromSlug } from './links'

describe('pet links', () => {
  it('собирает человеко-понятный slug для карточки питомца', () => {
    expect(
      buildPetPath({
        id: 12,
        name: ' Lucky Dog ',
        type: 'dog',
      }),
    ).toBe('/pets/12-lucky-dog')
  })

  it('извлекает id из slug и отбрасывает некорректные значения', () => {
    expect(getPetIdFromSlug('15-lucky-dog')).toBe(15)
    expect(getPetIdFromSlug('invalid-slug')).toBeNull()
  })
})
