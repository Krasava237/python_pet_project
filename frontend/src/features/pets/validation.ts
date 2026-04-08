import type { PetFormData } from './types'

export type PetFormErrors = Partial<Record<keyof PetFormData, string>>

function normalizeOptionalValue(value: string) {
  return value.trim()
}

export function validatePetForm(values: PetFormData): PetFormErrors {
  const errors: PetFormErrors = {}

  if (values.type.trim().length < 2) {
    errors.type = 'Укажите тип питомца'
  }
  if (values.color.trim().length < 2) {
    errors.color = 'Укажите цвет'
  }
  if (values.sex.trim().length < 2) {
    errors.sex = 'Укажите пол'
  }
  if (values.address.trim().length < 5) {
    errors.address = 'Укажите адрес не короче 5 символов'
  }
  if (values.description.trim().length < 10) {
    errors.description = 'Описание должно быть не короче 10 символов'
  }
  if (!values.found_date) {
    errors.found_date = 'Укажите дату'
  }
  if (!values.found_time) {
    errors.found_time = 'Укажите время'
  }
  if (values.name.trim().length > 255) {
    errors.name = 'Имя слишком длинное'
  }
  if (values.breed.trim().length > 100) {
    errors.breed = 'Порода слишком длинная'
  }

  return errors
}

export function normalizePetForm(values: PetFormData): PetFormData {
  return {
    ...values,
    type: values.type.trim().toLowerCase(),
    breed: normalizeOptionalValue(values.breed),
    name: normalizeOptionalValue(values.name),
    color: values.color.trim().toLowerCase(),
    sex: values.sex.trim().toLowerCase(),
    age: normalizeOptionalValue(values.age),
    chip_number: normalizeOptionalValue(values.chip_number),
    brand_number: normalizeOptionalValue(values.brand_number),
    address: values.address.trim(),
    description: values.description.trim(),
  }
}
