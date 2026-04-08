import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import PetLocationInsight from '../features/pets/PetLocationInsight'
import { buildPetPath, getPetIdFromSlug } from '../features/pets/links'
import type { Pet } from '../features/pets/types'
import { getApiErrorMessage } from '../shared/api/http'
import { getPet } from '../shared/api/pets'
import Seo from '../shared/seo/Seo'
import { NotFoundPage } from './NotFoundPage'

function buildJsonLd(pet: Pet, canonicalPath: string, siteUrl: string) {
  const canonicalUrl = `${siteUrl.replace(/\/$/, '')}${canonicalPath}`
  const petName = pet.name?.trim() || `Питомец ${pet.id}`

  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      {
        '@type': 'ListItem',
        position: 1,
        name: 'Pet Finder',
        item: `${siteUrl.replace(/\/$/, '')}/`,
      },
      {
        '@type': 'ListItem',
        position: 2,
        name: 'Объявления о питомцах',
        item: `${siteUrl.replace(/\/$/, '')}/pets`,
      },
      {
        '@type': 'ListItem',
        position: 3,
        name: petName,
        item: canonicalUrl,
      },
    ],
  }
}

export function PetDetailsPage() {
  const { petSlug = '' } = useParams()
  const petId = getPetIdFromSlug(petSlug)
  const [pet, setPet] = useState<Pet | null>(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let isMounted = true

    async function loadPet() {
      if (!petId) {
        if (isMounted) {
          setError('Некорректный адрес объявления')
          setIsLoading(false)
        }
        return
      }

      try {
        const response = await getPet(petId)
        if (isMounted) {
          setPet(response)
        }
      } catch (requestError) {
        if (isMounted) {
          setError(getApiErrorMessage(requestError, 'Не удалось загрузить объявление'))
        }
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    void loadPet()

    return () => {
      isMounted = false
    }
  }, [petId])

  if (!isLoading && (!petId || error)) {
    return <NotFoundPage />
  }

  if (!pet) {
    return (
      <section className="stack">
        <div className="card">
          <h1>Объявление</h1>
          <p className="muted">{isLoading ? 'Загрузка...' : 'Объявление не найдено.'}</p>
        </div>
      </section>
    )
  }

  const canonicalPath = buildPetPath(pet)
  const siteUrl = import.meta.env.VITE_PUBLIC_APP_URL ?? window.location.origin
  const currentPetName = pet.name?.trim() || `Питомец ${pet.id}`
  const title = `${currentPetName} | Pet Finder`
  const description = `Объявление о питомце: ${pet.type}, ${pet.color}, адрес ${pet.address}.`
  const imageAlt = `Фото питомца ${currentPetName}`
  const keywords = [
    'объявление о питомце',
    pet.type,
    pet.color,
    pet.breed ?? '',
    pet.status,
    pet.address,
  ].filter(Boolean)

  return (
    <section className="stack">
      <Seo
        canonicalPath={canonicalPath}
        description={description}
        imageAlt={imageAlt}
        imageUrl={pet.photo_url ?? undefined}
        jsonLd={buildJsonLd(pet, canonicalPath, siteUrl)}
        keywords={keywords}
        title={title}
        type="article"
      />

      <nav aria-label="Хлебные крошки" className="card breadcrumb-nav">
        <ol className="breadcrumb-list">
          <li>
            <Link to="/">Главная</Link>
          </li>
          <li>
            <Link to="/pets">Объявления</Link>
          </li>
          <li>
            <span aria-current="page">{currentPetName}</span>
          </li>
        </ol>
      </nav>

      <article className="card detail-card">
        <header className="detail-header">
          <div className="stack">
            <p className="eyebrow">Публичная SEO-страница объявления</p>
            <h1>{pet.name?.trim() || 'Без клички'}</h1>
            <p className="muted">
              {pet.type} | {pet.breed ?? 'порода не указана'} | статус {pet.status}
            </p>
          </div>
          {pet.photo_url && (
            <img alt={imageAlt} className="detail-image" loading="lazy" src={pet.photo_url} />
          )}
        </header>

        <div className="detail-grid">
          <section className="card detail-section">
            <h2>Карточка объявления</h2>
            <dl className="pet-meta-grid">
              <div>
                <dt>Тип</dt>
                <dd>{pet.type}</dd>
              </div>
              <div>
                <dt>Цвет</dt>
                <dd>{pet.color}</dd>
              </div>
              <div>
                <dt>Пол</dt>
                <dd>{pet.sex}</dd>
              </div>
              <div>
                <dt>Возраст</dt>
                <dd>{pet.age ?? 'не указан'}</dd>
              </div>
              <div>
                <dt>Дата и время</dt>
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
          </section>

          <section className="card detail-section">
            <PetLocationInsight petId={pet.id} />
          </section>
        </div>
      </article>
    </section>
  )
}

export default PetDetailsPage
