import { expect, test, type APIRequestContext, type Page } from '@playwright/test'

const apiBaseUrl = 'http://127.0.0.1:8001'
const defaultPassword = 'User12345!'

test.beforeEach(async ({ request }) => {
  // Каждый e2e-сценарий начинается с полностью очищенного состояния backend.
  const response = await request.post(`${apiBaseUrl}/_test/reset`)
  expect(response.ok()).toBeTruthy()
})

test('администратор входит в систему, открывает admin-раздел и восстанавливает сессию после перезагрузки', async ({
  page,
}) => {
  await login(page, 'admin@local.dev', 'Admin123!')

  await page.goto('/admin')
  await expect(page).toHaveURL(/\/admin$/)

  await page.reload()
  await expect(page.locator('.status-badge')).toContainText('admin@local.dev')

  await page.getByRole('button', { name: /выйти/i }).click()
  await expect(page).toHaveURL(/\/login$/)
})

test('пользователь выполняет CRUD, фильтрацию, пагинацию и видит оба состояния внешнего API', async ({
  page,
  request,
}) => {
  const email = 'owner@example.com'
  await registerUser(request, email)
  const authHeaders = await apiLogin(request, email, defaultPassword)

  for (let index = 0; index < 10; index += 1) {
    await createPetThroughApi(request, authHeaders, {
      name: `Seed ${index + 1}`,
      address: `Seed address ${index + 1}`,
    })
  }

  await login(page, email, defaultPassword)
  await page.goto('/pets')

  const petForm = page.locator('.pet-form').first()

  await expect(page.getByRole('button', { name: /вперед/i })).toBeVisible()
  await page.getByRole('button', { name: /вперед/i }).click()
  await expect(page.locator('.pagination-bar')).toContainText(/2/)

  await page.getByRole('button', { name: /назад/i }).click()
  await expect(page.locator('.pagination-bar')).toContainText(/1/)

  await petForm.getByLabel(/кличка/i).fill('Luna UI')
  await petForm.getByLabel(/^цвет$/i).fill('black')
  await petForm.getByLabel(/адрес/i).fill('Moscow Kremlin')
  await petForm
    .getByLabel(/описание/i)
    .fill('Friendly dog seen near the main square and ready for UI checks.')
  await page.getByRole('button', { name: /создать объявление/i }).click()

  const lunaCard = page.locator('.pet-card').filter({ hasText: 'Luna UI' }).first()
  await expect(lunaCard).toBeVisible()

  await page.getByLabel(/поиск/i).fill('Luna UI')
  await expect(lunaCard).toBeVisible()

  await lunaCard.getByRole('link').click()
  await expect(page).toHaveURL(/\/pets\/\d+-luna-ui$/)
  await expect(page.locator('.insight-card')).toContainText('Normalized: Moscow Kremlin')

  const unavailableResponse = await request.post(`${apiBaseUrl}/_test/nominatim-mode`, {
    data: { mode: 'unavailable' },
  })
  expect(unavailableResponse.ok()).toBeTruthy()

  await page.reload()
  await expect(page.locator('.insight-card')).toContainText(/temporarily unavailable/i)
})

test('владелец загружает вложение, получает ссылку на скачивание и удаляет объявление', async ({
  page,
  request,
}) => {
  const email = 'files@example.com'
  await registerUser(request, email)
  await login(page, email, defaultPassword)
  await page.goto('/pets')

  const petForm = page.locator('.pet-form').first()

  await petForm.getByLabel(/кличка/i).fill('Files UI')
  await petForm.getByLabel(/^цвет$/i).fill('white')
  await petForm.getByLabel(/адрес/i).fill('Arbat street')
  await petForm
    .getByLabel(/описание/i)
    .fill('File upload scenario for object storage integration checks.')
  await page.getByRole('button', { name: /создать объявление/i }).click()

  const petCard = page.locator('.pet-card').filter({ hasText: 'Files UI' }).first()
  await expect(petCard).toBeVisible()

  await petCard.getByRole('button', { name: /файлы/i }).click()
  await petCard
    .getByLabel(/загрузить файл/i)
    .setInputFiles('./e2e/fixtures/sample-attachment.pdf')
  await petCard.getByRole('button', { name: /^загрузить$/i }).click()

  await expect(petCard).toContainText('sample-attachment.pdf')

  await petCard.getByRole('button', { name: /скачать/i }).click()
  await expect(petCard).toContainText(/ссылка выдана/i)

  page.on('dialog', (dialog) => dialog.accept())
  await petCard.locator(':scope > .actions').getByRole('button', { name: /^удалить$/i }).click()
  await expect(petCard).not.toBeVisible()
})

async function registerUser(request: APIRequestContext, email: string) {
  const response = await request.post(`${apiBaseUrl}/users/register`, {
    data: {
      email,
      password: defaultPassword,
    },
  })
  expect(response.ok()).toBeTruthy()
}

async function apiLogin(request: APIRequestContext, email: string, password: string) {
  const response = await request.post(`${apiBaseUrl}/users/login`, {
    data: { email, password },
  })
  expect(response.ok()).toBeTruthy()
  const payload = await response.json()
  return {
    Authorization: `Bearer ${payload.access_token}`,
  }
}

async function createPetThroughApi(
  request: APIRequestContext,
  headers: Record<string, string>,
  overrides: { name: string; address: string },
) {
  // Часть фикстур создаем через API, чтобы UI-тест не тратил время на однотипный ввод десяти записей.
  const response = await request.post(`${apiBaseUrl}/pets/`, {
    data: {
      type: 'dog',
      breed: 'Corgi',
      name: overrides.name,
      color: 'black',
      sex: 'male',
      age: '2 years',
      chip_number: `CHIP-${overrides.name}`,
      brand_number: `BRAND-${overrides.name}`,
      found_date: '2026-03-24',
      found_time: '11:20:00',
      address: overrides.address,
      description: `Generated seed record for ${overrides.name}.`,
      status: 'lost',
    },
    headers,
  })

  expect(response.ok()).toBeTruthy()
}

async function login(page: Page, email: string, password: string) {
  await page.goto('/login')
  await page.getByLabel('Email').fill(email)
  await page.getByLabel(/пароль/i).fill(password)
  await page.getByRole('button', { name: /войти/i }).click()
  await expect(page).toHaveURL(/\/$/)
}
