import type {
  CreatePetPayload,
  PaginatedPetsResponse,
  Pet,
  PetAttachment,
  PetAttachmentDownloadResponse,
  PetFilters,
  PetLocationInsight,
  UpdatePetPayload,
} from '../../features/pets/types'
import { apiRequest } from './http'

function buildPetsQuery(params: Partial<PetFilters>) {
  const searchParams = new URLSearchParams()

  if (params.search) {
    searchParams.set('search', params.search)
  }
  if (params.type) {
    searchParams.set('type', params.type)
  }
  if (params.status) {
    searchParams.set('status', params.status)
  }
  if (params.sex) {
    searchParams.set('sex', params.sex)
  }
  if (params.color) {
    searchParams.set('color', params.color)
  }
  if (params.sortBy) {
    searchParams.set('sort_by', params.sortBy)
  }
  if (params.sortOrder) {
    searchParams.set('sort_order', params.sortOrder)
  }
  if (params.page) {
    searchParams.set('page', String(params.page))
  }
  if (params.pageSize) {
    searchParams.set('page_size', String(params.pageSize))
  }

  const queryString = searchParams.toString()
  return queryString ? `?${queryString}` : ''
}

export function getPets(params: Partial<PetFilters>) {
  return apiRequest<PaginatedPetsResponse>(`/pets/${buildPetsQuery(params)}`)
}

export function getMyPets(params: Partial<PetFilters>) {
  return apiRequest<PaginatedPetsResponse>(`/pets/my${buildPetsQuery(params)}`)
}

export function getPet(petId: number) {
  return apiRequest<Pet>(`/pets/${petId}`)
}

export function createPet(payload: CreatePetPayload) {
  return apiRequest<Pet>('/pets/', {
    body: payload,
    method: 'POST',
  })
}

export function updatePet(petId: number, payload: UpdatePetPayload) {
  return apiRequest<Pet>(`/pets/${petId}`, {
    body: payload,
    method: 'PUT',
  })
}

export function deletePet(petId: number) {
  return apiRequest<{ detail: string }>(`/pets/${petId}`, {
    method: 'DELETE',
  })
}

export function listPetAttachments(petId: number) {
  return apiRequest<PetAttachment[]>(`/pets/${petId}/attachments`)
}

export function uploadPetAttachment(petId: number, file: File) {
  const formData = new FormData()
  formData.append('file', file)

  return apiRequest<PetAttachment>(`/pets/${petId}/attachments`, {
    body: formData,
    method: 'POST',
  })
}

export function getPetAttachmentDownloadUrl(petId: number, attachmentId: number) {
  return apiRequest<PetAttachmentDownloadResponse>(
    `/pets/${petId}/attachments/${attachmentId}/download-url`,
  )
}

export function deletePetAttachment(petId: number, attachmentId: number) {
  return apiRequest<{ detail: string }>(`/pets/${petId}/attachments/${attachmentId}`, {
    method: 'DELETE',
  })
}

export function getPetLocationInsight(petId: number) {
  return apiRequest<PetLocationInsight>(`/pets/${petId}/location-insight`)
}
