import { Suspense, lazy, startTransition, useDeferredValue, useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

import PetForm from '../features/pets/PetForm'
import {
  DEFAULT_PET_FILTERS,
  PAGE_SIZE_OPTIONS,
  PET_SEX_OPTIONS,
  PET_SORT_OPTIONS,
  PET_STATUS_OPTIONS,
  PET_TYPE_OPTIONS,
  SORT_ORDER_OPTIONS,
  createDefaultPetFormData,
} from '../features/pets/constants'
import { buildPetPath } from '../features/pets/links'
import type {
  PaginatedPetsResponse,
  Pet,
  PetFilters,
  PetFormData,
  PetSortBy,
  PetStatus,
  SortOrder,
} from '../features/pets/types'
import { useAuth } from '../features/auth/useAuth'
import { getApiErrorMessage } from '../shared/api/http'
import {
  createPet,
  deletePet,
  getMyPets,
  getPets,
  updatePet,
} from '../shared/api/pets'
import { canCreatePets, canManagePet, canManagePetAttachments } from '../shared/auth/access'
import Seo from '../shared/seo/Seo'

const PetAttachmentsPanel = lazy(() => import('../features/pets/PetAttachmentsPanel'))

function parseNumberParam(value: string | null, fallback: number) {
  const parsed = Number(value)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback
}

function getStatusLabel(status: Pet['status']) {
  return PET_STATUS_OPTIONS.find((option) => option.value === status)?.label ?? status
}

function parseFilters(searchParams: URLSearchParams): PetFilters {
  const scope = searchParams.get('scope') === 'my' ? 'my' : DEFAULT_PET_FILTERS.scope
  const statusParam = searchParams.get('status')
  const normalizedStatus: '' | PetStatus =
    statusParam && PET_STATUS_OPTIONS.some((option) => option.value === statusParam)
      ? (statusParam as PetStatus)
      : DEFAULT_PET_FILTERS.status
  const sortByParam = searchParams.get('sort_by')
  const normalizedSortBy: PetSortBy =
    sortByParam && PET_SORT_OPTIONS.some((option) => option.value === sortByParam)
      ? (sortByParam as PetSortBy)
      : DEFAULT_PET_FILTERS.sortBy
  const sortOrderParam = searchParams.get('sort_order')
  const normalizedSortOrder: SortOrder =
    sortOrderParam && SORT_ORDER_OPTIONS.some((option) => option.value === sortOrderParam)
      ? (sortOrderParam as SortOrder)
      : DEFAULT_PET_FILTERS.sortOrder

  return {
    search: searchParams.get('search') ?? DEFAULT_PET_FILTERS.search,
    type: searchParams.get('type') ?? DEFAULT_PET_FILTERS.type,
    status: normalizedStatus,
    sex: searchParams.get('sex') ?? DEFAULT_PET_FILTERS.sex,
    color: searchParams.get('color') ?? DEFAULT_PET_FILTERS.color,
    sortBy: normalizedSortBy,
    sortOrder: normalizedSortOrder,
    page: parseNumberParam(searchParams.get('page'), DEFAULT_PET_FILTERS.page),
    pageSize: parseNumberParam(searchParams.get('page_size'), DEFAULT_PET_FILTERS.pageSize),
    scope,
  }
}

function petToFormData(pet: Pet): PetFormData {
  return {
    type: pet.type,
    breed: pet.breed ?? '',
    name: pet.name ?? '',
    color: pet.color,
    sex: pet.sex,
    age: pet.age ?? '',
    chip_number: pet.chip_number ?? '',
    brand_number: pet.brand_number ?? '',
    found_date: pet.found_date,
    found_time: pet.found_time.slice(0, 5),
    address: pet.address,
    description: pet.description,
    status: pet.status,
  }
}

export function PetsPage() {
  const { user } = useAuth()
  const [searchParams, setSearchParams] = useSearchParams()
  const filters = parseFilters(searchParams)
  const { color, page, pageSize, scope, search, sex, sortBy, sortOrder, status, type } = filters
  const currentSearchParam = searchParams.get('search') ?? ''
  const currentUserId = user?.id ?? null

  const [searchInput, setSearchInput] = useState(currentSearchParam)
  const deferredSearch = useDeferredValue(searchInput)
  const [petsResponse, setPetsResponse] = useState<PaginatedPetsResponse | null>(null)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [createFormInitial, setCreateFormInitial] = useState(() => createDefaultPetFormData())
  const [editingPetId, setEditingPetId] = useState<number | null>(null)
  const [editingInitialValue, setEditingInitialValue] = useState<PetFormData | null>(null)
  const [expandedFilesPetId, setExpandedFilesPetId] = useState<number | null>(null)
  const [reloadToken, setReloadToken] = useState(0)

  useEffect(() => {
    setSearchInput(currentSearchParam)
  }, [currentSearchParam])

  function updateQuery(updates: Record<string, string | number | null>) {
    const next = new URLSearchParams(searchParams)

    Object.entries(updates).forEach(([key, value]) => {
      if (value === null || value === '') {
        next.delete(key)
      } else {
        next.set(key, String(value))
      }
    })

    startTransition(() => {
      setSearchParams(next, { replace: true })
    })
  }

  useEffect(() => {
    if (deferredSearch === currentSearchParam) {
      return
    }

    const next = new URLSearchParams(searchParams)

    if (deferredSearch) {
      next.set('search', deferredSearch)
    } else {
      next.delete('search')
    }
    next.set('page', '1')

    startTransition(() => {
      setSearchParams(next, { replace: true })
    })
  }, [currentSearchParam, deferredSearch, searchParams, setSearchParams])

  useEffect(() => {
    let isMounted = true

    async function loadPets() {
      if (scope === 'my' && !currentUserId) {
        if (isMounted) {
          setPetsResponse(null)
          setError('')
          setIsLoading(false)
        }
        return
      }

      setIsLoading(true)
      setError('')

      try {
        const requestFilters = {
          color,
          page,
          pageSize,
          scope,
          search,
          sex,
          sortBy,
          sortOrder,
          status,
          type,
        }
        const response = scope === 'my' ? await getMyPets(requestFilters) : await getPets(requestFilters)
        if (isMounted) {
          setPetsResponse(response)
        }
      } catch (requestError) {
        if (isMounted) {
          setError(getApiErrorMessage(requestError, 'Не удалось загрузить объявления'))
          setPetsResponse(null)
        }
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    void loadPets()

    return () => {
      isMounted = false
    }
  }, [
    color,
    currentUserId,
    page,
    pageSize,
    reloadToken,
    scope,
    search,
    sex,
    sortBy,
    sortOrder,
    status,
    type,
  ])

  async function handleCreate(values: PetFormData) {
    setIsSubmitting(true)
    setError('')
    setMessage('')

    try {
      await createPet(values)
      setMessage('Объявление создано')
      setCreateFormInitial(createDefaultPetFormData())
      setReloadToken((current) => current + 1)
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Не удалось создать объявление'))
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleUpdate(values: PetFormData) {
    if (editingPetId === null) {
      return
    }

    setIsSubmitting(true)
    setError('')
    setMessage('')

    try {
      await updatePet(editingPetId, values)
      setMessage('Объявление обновлено')
      setEditingPetId(null)
      setEditingInitialValue(null)
      setReloadToken((current) => current + 1)
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Не удалось обновить объявление'))
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleDelete(petId: number) {
    const confirmed = window.confirm('Удалить объявление?')
    if (!confirmed) {
      return
    }

    setError('')
    setMessage('')

    try {
      await deletePet(petId)
      setMessage('Объявление удалено')
      setReloadToken((current) => current + 1)
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Не удалось удалить объявление'))
    }
  }

  function toggleEditing(pet: Pet) {
    if (editingPetId === pet.id) {
      setEditingPetId(null)
      setEditingInitialValue(null)
    } else {
      setEditingInitialValue(petToFormData(pet))
      setEditingPetId(pet.id)
    }
  }

  const hasItems = (petsResponse?.items.length ?? 0) > 0

  return (
    <section className="stack">
      <Seo
        canonicalPath="/pets"
        description="Публичный каталог объявлений о потерянных и найденных питомцах с фильтрацией и пагинацией."
        keywords={['pet finder', 'объявления о питомцах', 'потерянные животные', 'найденные животные']}
        title="Объявления о питомцах | Pet Finder"
      />
      <div className="card hero-card">
        <div className="hero-copy">
          <h1>Объявления о потерянных и найденных питомцах</h1>
          <p className="muted">
            Страница закрывает лаб. 3: фильтрация, поиск, сортировка, пагинация, CRUD и работа с
            приватными вложениями через объектное хранилище.
          </p>
        </div>
      </div>

      <div className="card">
        <div className="segmented">
          <button
            className={filters.scope === 'all' ? 'is-active' : ''}
            onClick={() => updateQuery({ scope: null, page: 1 })}
            type="button"
          >
            Все объявления
          </button>
          <button
            className={filters.scope === 'my' ? 'is-active' : ''}
            onClick={() => updateQuery({ scope: 'my', page: 1 })}
            type="button"
          >
            Мои объявления
          </button>
        </div>

        <div className="filters-grid">
          <label className="field">
            <span>Поиск</span>
            <input
              onChange={(event) => setSearchInput(event.target.value)}
              placeholder="Имя, порода, адрес, описание"
              value={searchInput}
            />
          </label>

          <label className="field">
            <span>Тип</span>
            <select
              onChange={(event) => updateQuery({ type: event.target.value || null, page: 1 })}
              value={filters.type}
            >
              <option value="">Все</option>
              {PET_TYPE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>Статус</span>
            <select
              onChange={(event) => updateQuery({ status: event.target.value || null, page: 1 })}
              value={filters.status}
            >
              <option value="">Все</option>
              {PET_STATUS_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>Пол</span>
            <select
              onChange={(event) => updateQuery({ sex: event.target.value || null, page: 1 })}
              value={filters.sex}
            >
              <option value="">Все</option>
              {PET_SEX_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>Цвет</span>
            <input
              onChange={(event) => updateQuery({ color: event.target.value || null, page: 1 })}
              placeholder="Например, black"
              value={filters.color}
            />
          </label>

          <label className="field">
            <span>Сортировка</span>
            <select
              onChange={(event) => updateQuery({ sort_by: event.target.value, page: 1 })}
              value={filters.sortBy}
            >
              {PET_SORT_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>Порядок</span>
            <select
              onChange={(event) => updateQuery({ sort_order: event.target.value, page: 1 })}
              value={filters.sortOrder}
            >
              {SORT_ORDER_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>На странице</span>
            <select
              onChange={(event) => updateQuery({ page_size: event.target.value, page: 1 })}
              value={String(filters.pageSize)}
            >
              {PAGE_SIZE_OPTIONS.map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
          </label>

          <div className="actions">
            <button
              onClick={() =>
                updateQuery({
                  search: null,
                  type: null,
                  status: null,
                  sex: null,
                  color: null,
                  sort_by: null,
                  sort_order: null,
                  page: null,
                  page_size: null,
                  scope: filters.scope === 'my' ? 'my' : null,
                })
              }
              type="button"
            >
              Сбросить фильтры
            </button>
          </div>
        </div>
      </div>

      {canCreatePets(user) && (
        <div className="card">
          <h2>Создать объявление</h2>
          <PetForm
            initialValue={createFormInitial}
            isSubmitting={isSubmitting && editingPetId === null}
            onSubmit={handleCreate}
            submitLabel="Создать объявление"
          />
        </div>
      )}

      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}

      <div className="card">
        <div className="results-summary">
          <strong>
            {petsResponse ? `Найдено объявлений: ${petsResponse.meta.total}` : 'Объявления'}
          </strong>
          {petsResponse && (
            <span className="muted">
              Страница {petsResponse.meta.page} из {petsResponse.meta.total_pages}
            </span>
          )}
        </div>

        {filters.scope === 'my' && !user && (
          <p className="muted">Для просмотра своих объявлений нужно войти в систему.</p>
        )}
        {isLoading && <p className="muted">Загрузка объявлений...</p>}
        {!isLoading && !hasItems && filters.scope !== 'my' && (
          <p className="muted">По текущим фильтрам ничего не найдено.</p>
        )}
        {!isLoading && !hasItems && filters.scope === 'my' && user && (
          <p className="muted">У вас пока нет объявлений с такими параметрами.</p>
        )}

        <div className="pets-grid">
          {!isLoading &&
            petsResponse?.items.map((pet) => {
              const canManage = canManagePet(user, pet.owner_id)
              const canManageAttachments = canManagePetAttachments(user, pet.owner_id)

              return (
                <article className="pet-card" key={pet.id}>
                  {pet.photo_url && (
                    <img
                      alt={`Фото питомца ${pet.name?.trim() || pet.type}`}
                      className="pet-card-image"
                      loading="lazy"
                      src={pet.photo_url}
                    />
                  )}

                  <div className="pet-card-header">
                    <div>
                      <h3>{pet.name?.trim() || 'Без клички'}</h3>
                      <p className="muted">
                        {pet.type} | {pet.breed ?? 'порода не указана'}
                      </p>
                    </div>
                    <span className={`status-chip status-${pet.status}`}>
                      {getStatusLabel(pet.status)}
                    </span>
                  </div>

                  <dl className="pet-meta-grid">
                    <div>
                      <dt>Цвет</dt>
                      <dd>{pet.color}</dd>
                    </div>
                    <div>
                      <dt>Пол</dt>
                      <dd>{pet.sex}</dd>
                    </div>
                    <div>
                      <dt>Дата</dt>
                      <dd>
                        {pet.found_date} {pet.found_time.slice(0, 5)}
                      </dd>
                    </div>
                    <div>
                      <dt>Адрес</dt>
                      <dd>{pet.address}</dd>
                    </div>
                  </dl>

                  <p>{pet.description}</p>

                  <div className="actions">
                    <Link to={buildPetPath(pet)}>Открыть страницу</Link>
                    {canManage && (
                      <>
                        <button
                          onClick={() => toggleEditing(pet)}
                          type="button"
                        >
                          {editingPetId === pet.id ? 'Скрыть форму' : 'Редактировать'}
                        </button>
                        <button onClick={() => void handleDelete(pet.id)} type="button">
                          Удалить
                        </button>
                      </>
                    )}

                    {canManageAttachments && (
                      <button
                        onClick={() =>
                          setExpandedFilesPetId((current) => (current === pet.id ? null : pet.id))
                        }
                        type="button"
                      >
                        {expandedFilesPetId === pet.id ? 'Скрыть файлы' : 'Файлы'}
                      </button>
                    )}
                  </div>

                  {!canManage && (
                    <p className="muted">
                      Редактирование и удаление доступны только владельцу объявления или админу.
                    </p>
                  )}

                  {editingPetId === pet.id && editingInitialValue && (
                    <div className="inline-panel">
                      <h4>Редактирование объявления</h4>
                      <PetForm
                        initialValue={editingInitialValue}
                        isSubmitting={isSubmitting}
                        onCancel={() => {
                          setEditingPetId(null)
                          setEditingInitialValue(null)
                        }}
                        onSubmit={handleUpdate}
                        submitLabel="Сохранить изменения"
                      />
                    </div>
                  )}

                  {expandedFilesPetId === pet.id && canManageAttachments && (
                    <div className="inline-panel">
                      <h4>Вложения объявления</h4>
                      <Suspense fallback={<p className="muted">Загрузка файлового менеджера...</p>}>
                        <PetAttachmentsPanel
                          onAttachmentChange={() => setReloadToken((current) => current + 1)}
                          petId={pet.id}
                        />
                      </Suspense>
                    </div>
                  )}
                </article>
              )
            })}
        </div>

        {petsResponse && petsResponse.meta.total_pages > 1 && (
          <div className="pagination-bar">
            <button
              disabled={!petsResponse.meta.has_previous}
              onClick={() => updateQuery({ page: filters.page - 1 })}
              type="button"
            >
              Назад
            </button>
            <span className="muted">
              Страница {petsResponse.meta.page} из {petsResponse.meta.total_pages}
            </span>
            <button
              disabled={!petsResponse.meta.has_next}
              onClick={() => updateQuery({ page: filters.page + 1 })}
              type="button"
            >
              Вперед
            </button>
          </div>
        )}
      </div>
    </section>
  )
}

export default PetsPage
