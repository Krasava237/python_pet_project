import { useEffect, useState, type FormEvent } from 'react'

import {
  PET_SEX_OPTIONS,
  PET_STATUS_OPTIONS,
  PET_TYPE_OPTIONS,
  createDefaultPetFormData,
} from './constants'
import type { PetFormData } from './types'
import { normalizePetForm, validatePetForm, type PetFormErrors } from './validation'

interface PetFormProps {
  initialValue?: PetFormData
  submitLabel: string
  isSubmitting: boolean
  onSubmit: (values: PetFormData) => Promise<void>
  onCancel?: () => void
}

export function PetForm({
  initialValue,
  submitLabel,
  isSubmitting,
  onSubmit,
  onCancel,
}: PetFormProps) {
  const [values, setValues] = useState<PetFormData>(initialValue ?? createDefaultPetFormData())
  const [errors, setErrors] = useState<PetFormErrors>({})

  useEffect(() => {
    setValues(initialValue ?? createDefaultPetFormData())
    setErrors({})
  }, [initialValue])

  function setField<Key extends keyof PetFormData>(field: Key, value: PetFormData[Key]) {
    setValues((current) => ({
      ...current,
      [field]: value,
    }))
    setErrors((current) => ({
      ...current,
      [field]: undefined,
    }))
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const normalized = normalizePetForm(values)
    const nextErrors = validatePetForm(normalized)
    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors)
      return
    }

    await onSubmit(normalized)
  }

  return (
    <form className="pet-form" onSubmit={handleSubmit}>
      <div className="form-columns">
        <label className="field">
          <span>Тип питомца</span>
          <select onChange={(event) => setField('type', event.target.value)} value={values.type}>
            {PET_TYPE_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          {errors.type && <span className="field-error">{errors.type}</span>}
        </label>

        <label className="field">
          <span>Порода</span>
          <input
            onChange={(event) => setField('breed', event.target.value)}
            placeholder="Например, метис"
            value={values.breed}
          />
          {errors.breed && <span className="field-error">{errors.breed}</span>}
        </label>

        <label className="field">
          <span>Кличка</span>
          <input
            onChange={(event) => setField('name', event.target.value)}
            placeholder="Если известна"
            value={values.name}
          />
          {errors.name && <span className="field-error">{errors.name}</span>}
        </label>

        <label className="field">
          <span>Цвет</span>
          <input onChange={(event) => setField('color', event.target.value)} value={values.color} />
          {errors.color && <span className="field-error">{errors.color}</span>}
        </label>

        <label className="field">
          <span>Пол</span>
          <select onChange={(event) => setField('sex', event.target.value)} value={values.sex}>
            {PET_SEX_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          {errors.sex && <span className="field-error">{errors.sex}</span>}
        </label>

        <label className="field">
          <span>Возраст</span>
          <input
            onChange={(event) => setField('age', event.target.value)}
            placeholder="Например, 2 года"
            value={values.age}
          />
        </label>

        <label className="field">
          <span>Чип</span>
          <input
            onChange={(event) => setField('chip_number', event.target.value)}
            value={values.chip_number}
          />
        </label>

        <label className="field">
          <span>Клеймо</span>
          <input
            onChange={(event) => setField('brand_number', event.target.value)}
            value={values.brand_number}
          />
        </label>

        <label className="field">
          <span>Дата</span>
          <input
            onChange={(event) => setField('found_date', event.target.value)}
            type="date"
            value={values.found_date}
          />
          {errors.found_date && <span className="field-error">{errors.found_date}</span>}
        </label>

        <label className="field">
          <span>Время</span>
          <input
            onChange={(event) => setField('found_time', event.target.value)}
            type="time"
            value={values.found_time}
          />
          {errors.found_time && <span className="field-error">{errors.found_time}</span>}
        </label>

        <label className="field">
          <span>Статус</span>
          <select
            onChange={(event) => setField('status', event.target.value as PetFormData['status'])}
            value={values.status}
          >
            {PET_STATUS_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <label className="field field-span-2">
          <span>Адрес</span>
          <input
            onChange={(event) => setField('address', event.target.value)}
            placeholder="Где питомца видели в последний раз"
            value={values.address}
          />
          {errors.address && <span className="field-error">{errors.address}</span>}
        </label>

        <label className="field field-span-2">
          <span>Описание</span>
          <textarea
            onChange={(event) => setField('description', event.target.value)}
            rows={4}
            value={values.description}
          />
          {errors.description && <span className="field-error">{errors.description}</span>}
        </label>
      </div>

      <div className="actions">
        <button disabled={isSubmitting} type="submit">
          {isSubmitting ? 'Сохранение...' : submitLabel}
        </button>
        {onCancel && (
          <button onClick={onCancel} type="button">
            Отмена
          </button>
        )}
      </div>
    </form>
  )
}

export default PetForm
