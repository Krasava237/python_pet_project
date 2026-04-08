import type { Pet } from './types'

function slugify(value: string) {
  return value
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[^\w\s-]/g, '')
    .trim()
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

export function buildPetPath(pet: Pick<Pet, 'id' | 'name' | 'type'>) {
  const slug = slugify(pet.name?.trim() || pet.type || 'pet') || 'pet'
  return `/pets/${pet.id}-${slug}`
}

export function getPetIdFromSlug(slug: string) {
  const match = slug.match(/^(\d+)/)
  if (!match) {
    return null
  }

  const value = Number(match[1])
  return Number.isFinite(value) ? value : null
}
