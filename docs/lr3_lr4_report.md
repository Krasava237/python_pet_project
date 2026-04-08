# Отчет по лабораторным работам №3 и №4

## 1. Что сделано по лабораторной работе №3

### 1.1. Сущности и сценарии

Для лаб. 3 использованы реальные сущности текущего домена `pet finder`:

- `pets` как пользовательские объявления о потерянных и найденных питомцах
- `pet_attachments` как приватные пользовательские файлы, привязанные к объявлению

Этим сущностям реально нужны:

- фильтрация и поиск по объявлениям
- сортировка и пагинация списков
- CRUD-управление объявлениями
- прикрепление файлов к объявлению с ограничением доступа

### 1.2. Backend

Реализовано:

- фильтрация `/pets` по `type`, `status`, `sex`, `color`
- поиск `/pets` по `name`, `breed`, `description`, `address`, `chip_number`, `brand_number`
- сортировка `/pets` по `found_date`, `name`, `type`, `status`, `id`
- пагинация `page/page_size`
- пагинированный ответ `{ items, meta }`
- валидация query params и данных питомца через Pydantic
- приватные endpoints для вложений:
  - `GET /pets/{id}/attachments`
  - `POST /pets/{id}/attachments`
  - `GET /pets/{id}/attachments/{attachment_id}/download-url`
  - `DELETE /pets/{id}/attachments/{attachment_id}`
- ограничения доступа:
  - чтение списка объявлений публично
  - создание/изменение/удаление объявления только владельцу или админу
  - доступ к вложениям только владельцу или админу

### 1.3. Object storage

Реализована реальная интеграция с S3-compatible storage через MinIO:

- добавлен [`docker-compose.yml`](../docker-compose.yml) с `postgres` и `minio`
- добавлен storage-service на `boto3` в [`app/storage/service.py`](../app/storage/service.py)
- для выдачи файлов используется pre-signed URL
- есть ограничения по типу и размеру файла
- метаданные файла хранятся в таблице `pet_attachments`

Поддерживаемые типы:

- `.jpg`
- `.jpeg`
- `.png`
- `.webp`
- `.pdf`

Максимальный размер:

- `5 MB`

### 1.4. Frontend

Доработана страница [`frontend/src/pages/PetsPage.tsx`](../frontend/src/pages/PetsPage.tsx):

- фильтры минимум по 3 параметрам и больше
- поиск
- сортировка
- пагинация
- сохранение состояния в query params
- отдельные режимы `все объявления / мои объявления`
- полноценные формы создания и редактирования объявления
- lazy-loaded панель работы с файлами
- состояния `loading / empty / error / success`

Дополнительно:

- добавлена клиентская валидация формы
- добавлена клиентская валидация файла до отправки

## 2. Что сделано по лабораторной работе №4

### 2.1. SEO-цели

Определены страницы:

- индексируемые:
  - `/`
  - `/pets`
  - `/pets/:petSlug`
- неиндексируемые:
  - `/login`
  - `/me`
  - `/admin`
  - клиентская `404`

### 2.2. Frontend SEO

Реализовано:

- динамические `title` и `description`
- `canonical`
- Open Graph
- `robots` meta
- `JSON-LD` (`BreadcrumbList`) для публичной detail-page
- человеко-понятные URL `/pets/{id-slug}`
- семантическая структура публичной detail-page
- `alt` для изображения питомца, если оно есть

SEO-слой вынесен в [`frontend/src/shared/seo/Seo.tsx`](../frontend/src/shared/seo/Seo.tsx).

### 2.3. Техническое SEO на FastAPI

Реализовано:

- [`/robots.txt`](http://127.0.0.1:8001/robots.txt)
- [`/sitemap.xml`](http://127.0.0.1:8001/sitemap.xml)
- `X-Robots-Tag: noindex, nofollow` для API-ответов
- корректные `404` на backend API для несуществующих сущностей

### 2.4. Производительность

Практически уместные улучшения:

- lazy loading страниц в [`frontend/src/app/App.tsx`](../frontend/src/app/App.tsx)
- lazy loading файловой панели вложений
- `useDeferredValue` для поисковой строки
- уменьшение лишних запросов за счет query params и точечных fetch-сценариев

### 2.5. Внешний API

Интегрирован Nominatim:

- backend adapter/service: [`app/integrations/nominatim.py`](../app/integrations/nominatim.py)
- pet endpoint: `GET /pets/{id}/location-insight`
- UI: [`frontend/src/features/pets/PetLocationInsight.tsx`](../frontend/src/features/pets/PetLocationInsight.tsx)

Что реализовано вокруг внешнего API:

- timeout
- retry
- rate limit
- кэширование
- нормализация ответа
- graceful degradation при недоступности внешнего API

## 3. Таблица `требование -> где реализовано`

| Требование | Где реализовано |
| --- | --- |
| Фильтрация по query params | `app/pets/dependencies.py`, `app/pets/repositories.py`, `app/pets/routers.py` |
| Поиск по ключевым полям | `app/pets/repositories.py` |
| Сортировка | `app/pets/repositories.py` |
| Пагинация | `app/pets/schemas.py`, `app/pets/repositories.py`, `app/pets/services.py` |
| Валидация параметров списка | `app/pets/dependencies.py`, `app/pets/schemas.py` |
| CRUD питомцев | `app/pets/routers.py`, `app/pets/services.py`, `frontend/src/pages/PetsPage.tsx` |
| Клиентская валидация формы питомца | `frontend/src/features/pets/validation.ts`, `frontend/src/features/pets/PetForm.tsx` |
| Ограничение доступа к чужим данным | `app/security.py`, `app/users/dependencies.py`, `app/pets/dependencies.py` |
| Интеграция MinIO / S3-compatible storage | `docker-compose.yml`, `app/storage/service.py` |
| Метаданные вложений | `app/pets/models.py`, `migrations/versions/4d7d1b0f7a90_add_pet_attachments.py` |
| Upload/list/delete/download-url для файлов | `app/pets/routers.py`, `app/pets/services.py`, `frontend/src/features/pets/PetAttachmentsPanel.tsx` |
| Ограничения типа и размера файлов | `app/storage/service.py`, `frontend/src/features/pets/constants.ts`, `frontend/src/features/pets/PetAttachmentsPanel.tsx` |
| Query params на клиенте | `frontend/src/pages/PetsPage.tsx` |
| Loading/empty/error states | `frontend/src/pages/PetsPage.tsx`, `frontend/src/features/pets/PetAttachmentsPanel.tsx`, `frontend/src/features/pets/PetLocationInsight.tsx` |
| Dynamic title/description/canonical | `frontend/src/shared/seo/Seo.tsx`, страницы `frontend/src/pages/*` |
| Open Graph | `frontend/src/shared/seo/Seo.tsx` |
| JSON-LD | `frontend/src/pages/PetDetailsPage.tsx` |
| Понятные URL | `frontend/src/features/pets/links.ts`, `frontend/src/app/App.tsx` |
| `robots.txt` | `app/seo.py` |
| `sitemap.xml` | `app/seo.py` |
| Noindex для API | `app/main.py` |
| Интеграция внешнего API | `app/integrations/nominatim.py`, `app/pets/routers.py` |
| Graceful degradation | `app/integrations/nominatim.py`, `frontend/src/features/pets/PetLocationInsight.tsx` |
| Клиентская 404-страница | `frontend/src/pages/NotFoundPage.tsx`, `frontend/src/app/App.tsx` |

## 4. Ключевые измененные файлы и их назначение

- `app/pets/models.py`
  - добавлена модель `PetAttachment`
- `app/pets/schemas.py`
  - валидация сущностей, пагинация, schema для location insight
- `app/pets/repositories.py`
  - фильтры, сортировка, пагинация, attachments query layer
- `app/pets/services.py`
  - service-логика списка, CRUD и файлов
- `app/pets/routers.py`
  - новые endpoints лаб. 3 и endpoint `location-insight`
- `app/storage/service.py`
  - MinIO/S3-compatible storage service
- `app/integrations/nominatim.py`
  - внешний API adapter/service
- `app/seo.py`
  - `robots.txt` и `sitemap.xml`
- `frontend/src/pages/PetsPage.tsx`
  - основной UI лаб. 3
- `frontend/src/features/pets/PetForm.tsx`
  - форма create/edit
- `frontend/src/features/pets/PetAttachmentsPanel.tsx`
  - файловая панель
- `frontend/src/pages/PetDetailsPage.tsx`
  - публичная SEO-страница объявления
- `frontend/src/shared/seo/Seo.tsx`
  - SEO head-management
- `frontend/src/features/pets/PetLocationInsight.tsx`
  - UI для внешнего API
- `docker-compose.yml`
  - локальная инфраструктура PostgreSQL + MinIO

## 5. Команды запуска и проверки

### 5.1. Инфраструктура

```powershell
docker compose up -d
```

### 5.2. Зависимости Python

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Если среда уже собрана, достаточно было:

```powershell
.\.venv\Scripts\python.exe -m pip install boto3==1.40.67 botocore==1.40.67 httpx==0.28.1
```

### 5.3. Миграции

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

### 5.4. Backend

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

### 5.5. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Для проверки сборки:

```powershell
cd frontend
npm run build
```

### 5.6. Автоматизированные проверки

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m compileall app
```

## 6. Что именно было протестировано

### 6.1. Реально проверено командами и запросами

- сборка frontend: `npm run build`
- импорт и синтаксис backend: `python -m compileall app`
- миграции: `python -m alembic upgrade head`
- статус инфраструктуры: `docker compose ps`
- `robots.txt`
- `sitemap.xml`
- заголовок `X-Robots-Tag` на API
- backend smoke-сценарий лаб. 3:
  - login admin
  - create pet
  - update pet
  - `/pets` с фильтрацией/поиском/сортировкой/пагинацией
  - `/pets/my`
  - пустой результат
  - невалидный `page=0`
  - upload attachment
  - list attachments
  - download pre-signed URL
  - реальное скачивание файла по pre-signed URL
  - запрет доступа чужому пользователю
  - delete attachment
  - delete pet
- backend smoke-сценарий лаб. 4:
  - `robots.txt`
  - `sitemap.xml`
  - `location-insight`
  - noindex headers
- headless browser-проверка frontend:
  - `/pets`
  - `/pets/:petSlug`
  - `/login`
  - наличие `canonical`, `og:title`, `robots`, `JSON-LD`
  - наличие блока Nominatim на public detail-page

### 6.2. Минимальные автоматизированные тесты

Добавлены и запущены:

- `tests/test_pets_schemas.py`
- `tests/test_nominatim_service.py`

## 7. Архитектурные решения и компромиссы

- Для лаб. 3 не ломал старый `upload_photo` и local `media/`.
  - Причина: он завязан на существующую ML-логику.
  - Новая объектная интеграция для лабораторной реализована отдельно через `pet_attachments` + MinIO.
- Для лаб. 4 не переводил проект на SSR/Next.js.
  - SEO решено в рамках текущего `React/Vite + FastAPI`.
- Внешний API взят без ключа и без ручной настройки.
  - Выбран Nominatim, потому что он связан с доменом `pet finder` через адрес объявления.
- Для внешнего API добавлен fallback-ответ со статусом `unavailable`, а не жесткий `500`.
  - Это позволяет UI не ломаться при недоступности стороннего сервиса.

## 8. Пошаговый сценарий демонстрации перед преподавателем

1. Показать инфраструктуру:
   - `docker compose ps`
   - `postgres` и `minio` в состоянии `healthy`
2. Показать backend-маршруты лабораторной 3:
   - создать объявление через UI
   - отфильтровать список по `type/status/sex`
   - показать поиск
   - показать сортировку и пагинацию
3. Показать управление своими данными:
   - отредактировать свое объявление
   - удалить его
   - показать, что чужое объявление редактировать нельзя
4. Показать object storage:
   - открыть панель файлов объявления
   - загрузить JPG или PDF
   - показать список вложений
   - нажать скачать и объяснить, что выдается pre-signed URL
   - удалить вложение
5. Показать SEO:
   - открыть `/pets`
   - открыть detail-page `/pets/{id-slug}`
   - показать `title`, `canonical`, `og:*`, `JSON-LD` через DevTools Elements
6. Показать техническое SEO:
   - открыть `/robots.txt`
   - открыть `/sitemap.xml`
7. Показать внешний API:
   - открыть detail-page объявления с адресом
   - показать блок Nominatim
   - если сервис временно недоступен, показать graceful degradation
8. Показать, что сборки и тесты проходили:
   - `npm run build`
   - `python -m unittest discover -s tests -v`

## 9. Что говорить на защите простыми словами

- Я не делал новый проект с нуля, а расширил существующий MVP на FastAPI и React/Vite.
- Для лаб. 3 я выбрал реальные пользовательские данные домена: объявления о питомцах и их вложения.
- На backend добавил фильтрацию, поиск, сортировку и пагинацию, а на frontend сохранил все это в query params.
- Для файлов я не ограничился локальной папкой `media`, а подключил MinIO как S3-compatible object storage.
- Файлы не отдаются напрямую: frontend получает защищенную pre-signed ссылку.
- Права доступа соблюдены: чужие объявления и вложения менять нельзя.
- Для лаб. 4 я не менял бизнес-логику, а добавил SEO вокруг существующих страниц.
- Публичными сделал главную, список объявлений и detail-page объявления.
- Закрытые страницы пометил как `noindex`.
- На FastAPI добавил `robots.txt`, `sitemap.xml` и `X-Robots-Tag` для API.
- Внешний API встроен через отдельный adapter/service слой, а при недоступности есть graceful degradation.

## 10. Честные ограничения и упрощения

- SPA на Vite в dev/preview-режиме не выдает настоящий server-side `404` для frontend-маршрутов.
  - Клиентская `404` страница есть.
  - Backend API для несуществующих сущностей возвращает корректный HTTP `404`.
- Старый `upload_photo` оставлен на локальном `media/` ради совместимости с ML-частью.
  - Для требований лаб. 3 объектное хранилище реализовано отдельно и реально используется в `pet_attachments`.
- Nominatim зависит от внешней доступности и лимитов сервиса.
  - Поэтому реализованы rate limit, retry, cache и graceful degradation.
- Во время верификации были созданы тестовые пользователи.
  - Полноценного пользовательского delete-flow в текущем MVP нет, поэтому эти аккаунты не удалялись.
