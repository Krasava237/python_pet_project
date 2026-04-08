export type PetStatus = 'lost' | 'found' | 'returned' | 'closed'
export type PetSortBy = 'found_date' | 'name' | 'type' | 'status' | 'id'
export type SortOrder = 'asc' | 'desc'
export type PetListScope = 'all' | 'my'

export interface Pet {
  id: number
  owner_id: number
  type: string
  breed: string | null
  name: string | null
  color: string
  sex: string
  age: string | null
  chip_number: string | null
  brand_number: string | null
  found_date: string
  found_time: string
  address: string
  description: string
  status: PetStatus
  photo_url: string | null
}

export interface PaginationMeta {
  page: number
  page_size: number
  total: number
  total_pages: number
  has_next: boolean
  has_previous: boolean
}

export interface PaginatedPetsResponse {
  items: Pet[]
  meta: PaginationMeta
}

export interface PetFilters {
  search: string
  type: string
  status: PetStatus | ''
  sex: string
  color: string
  sortBy: PetSortBy
  sortOrder: SortOrder
  page: number
  pageSize: number
  scope: PetListScope
}

export interface PetFormData {
  type: string
  breed: string
  name: string
  color: string
  sex: string
  age: string
  chip_number: string
  brand_number: string
  found_date: string
  found_time: string
  address: string
  description: string
  status: PetStatus
}

export type CreatePetPayload = PetFormData
export type UpdatePetPayload = Partial<PetFormData>

export interface PetAttachment {
  id: number
  pet_id: number
  uploaded_by_id: number | null
  original_filename: string
  content_type: string
  size_bytes: number
  is_image: boolean
  created_at: string
}

export interface PetAttachmentDownloadResponse {
  url: string
  expires_in: number
}

export type LocationInsightStatus = 'ok' | 'not_found' | 'unavailable'

export interface PetLocationInsight {
  status: LocationInsightStatus
  query: string
  provider: string
  attribution: string
  display_name: string | null
  lat: number | null
  lon: number | null
  importance: number | null
  message: string | null
}
