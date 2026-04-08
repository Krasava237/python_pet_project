import { useEffect, useState } from 'react'

import type { PetLocationInsight } from './types'
import { getApiErrorMessage } from '../../shared/api/http'
import { getPetLocationInsight } from '../../shared/api/pets'

interface PetLocationInsightProps {
  petId: number
}

export default function PetLocationInsight({ petId }: PetLocationInsightProps) {
  const [insight, setInsight] = useState<PetLocationInsight | null>(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let isMounted = true

    async function loadInsight() {
      setIsLoading(true)
      setError('')

      try {
        const response = await getPetLocationInsight(petId)
        if (isMounted) {
          setInsight(response)
        }
      } catch (requestError) {
        if (isMounted) {
          setError(getApiErrorMessage(requestError, 'Не удалось получить данные о локации'))
        }
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    void loadInsight()

    return () => {
      isMounted = false
    }
  }, [petId])

  if (isLoading) {
    return <p className="muted">Проверка адреса через внешний API...</p>
  }

  if (error) {
    return <p className="error">{error}</p>
  }

  if (!insight || insight.status === 'unavailable') {
    return (
      <div className="insight-card">
        <p className="muted">
          Внешний сервис геокодирования временно недоступен. Основное объявление продолжает работать
          без этого блока.
        </p>
        <p className="muted">{insight?.message ?? ''}</p>
      </div>
    )
  }

  if (insight.status === 'not_found') {
    return (
      <div className="insight-card">
        <p className="muted">
          Внешний API не нашел надежного совпадения для этого адреса. Это не влияет на работу
          основного объявления.
        </p>
      </div>
    )
  }

  return (
    <div className="insight-card">
      <h3>Подтверждение адреса через Nominatim</h3>
      <dl className="pet-meta-grid">
        <div>
          <dt>Нормализованный адрес</dt>
          <dd>{insight.display_name ?? 'Нет данных'}</dd>
        </div>
        <div>
          <dt>Координаты</dt>
          <dd>
            {insight.lat}, {insight.lon}
          </dd>
        </div>
        <div>
          <dt>Надежность</dt>
          <dd>{insight.importance ?? 'Нет данных'}</dd>
        </div>
        <div>
          <dt>Источник</dt>
          <dd>{insight.provider}</dd>
        </div>
      </dl>
      <p className="muted">{insight.attribution}</p>
    </div>
  )
}
