import type { PetFilters, PetFormData, PetStatus, PetSortBy, SortOrder } from './types'

export const PET_TYPE_OPTIONS = [
  { label: 'Собака', value: 'dog' },
  { label: 'Кошка', value: 'cat' },
  { label: 'Другое', value: 'other' },
] as const

export const PET_STATUS_OPTIONS: Array<{ label: string; value: PetStatus }> = [
  { label: 'Потерян', value: 'lost' },
  { label: 'Найден', value: 'found' },
  { label: 'Возвращен', value: 'returned' },
  { label: 'Закрыт', value: 'closed' },
]

export const PET_SEX_OPTIONS = [
  { label: 'Самец', value: 'male' },
  { label: 'Самка', value: 'female' },
  { label: 'Неизвестно', value: 'unknown' },
] as const

export const PET_SORT_OPTIONS: Array<{ label: string; value: PetSortBy }> = [
  { label: 'По дате нахождения', value: 'found_date' },
  { label: 'По имени', value: 'name' },
  { label: 'По типу', value: 'type' },
  { label: 'По статусу', value: 'status' },
  { label: 'По ID', value: 'id' },
]

export const SORT_ORDER_OPTIONS: Array<{ label: string; value: SortOrder }> = [
  { label: 'Сначала новые', value: 'desc' },
  { label: 'Сначала старые', value: 'asc' },
]

export const PAGE_SIZE_OPTIONS = [6, 9, 12, 18]

export const ALLOWED_ATTACHMENT_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.pdf']
export const MAX_ATTACHMENT_SIZE_BYTES = 5 * 1024 * 1024

export function createDefaultPetFormData(): PetFormData {
  const now = new Date()
  return {
    type: 'dog',
    breed: '',
    name: '',
    color: '',
    sex: 'male',
    age: '',
    chip_number: '',
    brand_number: '',
    found_date: now.toISOString().slice(0, 10),
    found_time: now.toTimeString().slice(0, 5),
    address: '',
    description: '',
    status: 'lost',
  }
}

export const DEFAULT_PET_FILTERS: PetFilters = {
  search: '',
  type: '',
  status: '',
  sex: '',
  color: '',
  sortBy: 'found_date',
  sortOrder: 'desc',
  page: 1,
  pageSize: 9,
  scope: 'all',
}
