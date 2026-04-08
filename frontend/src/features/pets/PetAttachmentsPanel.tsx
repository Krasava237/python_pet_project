import { useEffect, useState } from 'react'

import { ALLOWED_ATTACHMENT_EXTENSIONS, MAX_ATTACHMENT_SIZE_BYTES } from './constants'
import type { PetAttachment } from './types'
import {
  deletePetAttachment,
  getPetAttachmentDownloadUrl,
  listPetAttachments,
  uploadPetAttachment,
} from '../../shared/api/pets'
import { getApiErrorMessage } from '../../shared/api/http'

interface PetAttachmentsPanelProps {
  petId: number
  onAttachmentChange?: () => void
}

function formatFileSize(sizeBytes: number) {
  if (sizeBytes < 1024) {
    return `${sizeBytes} B`
  }
  if (sizeBytes < 1024 * 1024) {
    return `${(sizeBytes / 1024).toFixed(1)} KB`
  }
  return `${(sizeBytes / (1024 * 1024)).toFixed(1)} MB`
}

function validateFile(file: File) {
  const extension = file.name.slice(file.name.lastIndexOf('.')).toLowerCase()
  if (!ALLOWED_ATTACHMENT_EXTENSIONS.includes(extension)) {
    return 'Допустимы только JPG, PNG, WEBP и PDF'
  }
  if (file.size > MAX_ATTACHMENT_SIZE_BYTES) {
    return 'Размер файла не должен превышать 5 MB'
  }
  return null
}

export default function PetAttachmentsPanel({
  petId,
  onAttachmentChange,
}: PetAttachmentsPanelProps) {
  const [attachments, setAttachments] = useState<PetAttachment[]>([])
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isUploading, setIsUploading] = useState(false)
  const [deletingId, setDeletingId] = useState<number | null>(null)

  async function loadAttachments() {
    setIsLoading(true)
    setError('')

    try {
      const response = await listPetAttachments(petId)
      setAttachments(response)
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Не удалось загрузить вложения'))
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    let isMounted = true

    async function loadInitialAttachments() {
      setIsLoading(true)
      setError('')

      try {
        const response = await listPetAttachments(petId)
        if (isMounted) {
          setAttachments(response)
        }
      } catch (requestError) {
        if (isMounted) {
          setError(getApiErrorMessage(requestError, 'РќРµ СѓРґР°Р»РѕСЃСЊ Р·Р°РіСЂСѓР·РёС‚СЊ РІР»РѕР¶РµРЅРёСЏ'))
        }
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    void loadInitialAttachments()

    return () => {
      isMounted = false
    }
  }, [petId])

  async function handleUpload() {
    if (!selectedFile) {
      setError('Сначала выберите файл')
      return
    }

    const validationError = validateFile(selectedFile)
    if (validationError) {
      setError(validationError)
      return
    }

    setIsUploading(true)
    setError('')
    setMessage('')

    try {
      await uploadPetAttachment(petId, selectedFile)
      setMessage('Файл загружен в объектное хранилище')
      setSelectedFile(null)
      await loadAttachments()
      onAttachmentChange?.()
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Не удалось загрузить файл'))
    } finally {
      setIsUploading(false)
    }
  }

  async function handleDownload(attachmentId: number) {
    setError('')
    setMessage('')

    try {
      const response = await getPetAttachmentDownloadUrl(petId, attachmentId)
      window.open(response.url, '_blank', 'noopener,noreferrer')
      setMessage(`Ссылка выдана на ${Math.round(response.expires_in / 60)} мин.`)
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Не удалось получить ссылку на скачивание'))
    }
  }

  async function handleDelete(attachmentId: number) {
    const confirmed = window.confirm('Удалить это вложение?')
    if (!confirmed) {
      return
    }

    setDeletingId(attachmentId)
    setError('')
    setMessage('')

    try {
      await deletePetAttachment(petId, attachmentId)
      setMessage('Вложение удалено')
      await loadAttachments()
      onAttachmentChange?.()
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Не удалось удалить вложение'))
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="attachments-panel">
      <div className="attachments-uploader">
        <label className="field">
          <span>Загрузить файл</span>
          <input
            accept=".jpg,.jpeg,.png,.webp,.pdf"
            onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
            type="file"
          />
        </label>
        <div className="muted">
          Допустимы JPG, PNG, WEBP, PDF. Максимум 5 MB. Доступ к файлам ограничен владельцем
          объявления или администратором.
        </div>
        <div className="actions">
          <button disabled={!selectedFile || isUploading} onClick={() => void handleUpload()} type="button">
            {isUploading ? 'Загрузка...' : 'Загрузить'}
          </button>
        </div>
      </div>

      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}

      <div className="attachments-list">
        {isLoading && <p className="muted">Загрузка списка вложений...</p>}
        {!isLoading && attachments.length === 0 && (
          <p className="muted">Пока нет вложений. Добавьте фото или PDF-файл для объявления.</p>
        )}
        {!isLoading &&
          attachments.map((attachment) => (
            <article className="attachment-row" key={attachment.id}>
              <div className="row-main">
                <strong>{attachment.original_filename}</strong>
                <span className="muted">
                  {attachment.is_image ? 'Изображение' : 'PDF'} |{' '}
                  {formatFileSize(attachment.size_bytes)}
                </span>
              </div>
              <div className="muted">
                Загружено: {new Date(attachment.created_at).toLocaleString('ru-RU')}
              </div>
              <div className="actions">
                <button onClick={() => void handleDownload(attachment.id)} type="button">
                  Скачать
                </button>
                <button
                  disabled={deletingId === attachment.id}
                  onClick={() => void handleDelete(attachment.id)}
                  type="button"
                >
                  {deletingId === attachment.id ? 'Удаление...' : 'Удалить'}
                </button>
              </div>
            </article>
          ))}
      </div>
    </div>
  )
}
