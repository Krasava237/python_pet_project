import { useEffect } from 'react'

const DEFAULT_LOCALE = 'ru_RU'
const DEFAULT_SITE_NAME = 'Pet Finder'

interface SeoProps {
  title: string
  description: string
  canonicalPath: string
  robots?: string
  keywords?: string[]
  imageUrl?: string
  imageAlt?: string
  type?: 'website' | 'article'
  jsonLd?: Record<string, unknown> | null
}

function syncMeta(selector: string, attributes: Record<string, string> | null) {
  let element = document.head.querySelector<HTMLMetaElement>(selector)
  if (!attributes) {
    element?.remove()
    return
  }

  if (!element) {
    element = document.createElement('meta')
    document.head.appendChild(element)
  }

  Object.entries(attributes).forEach(([key, value]) => {
    element?.setAttribute(key, value)
  })
}

function upsertCanonical(href: string) {
  let element = document.head.querySelector<HTMLLinkElement>('link[rel="canonical"]')
  if (!element) {
    element = document.createElement('link')
    element.rel = 'canonical'
    document.head.appendChild(element)
  }
  element.href = href
}

function upsertJsonLd(payload: Record<string, unknown> | null) {
  const existing = document.getElementById('seo-jsonld')
  if (!payload) {
    existing?.remove()
    return
  }

  const script = existing ?? document.createElement('script')
  script.id = 'seo-jsonld'
  script.setAttribute('type', 'application/ld+json')
  script.textContent = JSON.stringify(payload)
  if (!existing) {
    document.head.appendChild(script)
  }
}

export function Seo({
  title,
  description,
  canonicalPath,
  robots = 'index,follow',
  keywords,
  imageUrl,
  imageAlt,
  type = 'website',
  jsonLd = null,
}: SeoProps) {
  useEffect(() => {
    const siteUrl = import.meta.env.VITE_PUBLIC_APP_URL ?? window.location.origin
    const canonicalUrl = `${siteUrl.replace(/\/$/, '')}${canonicalPath}`
    const keywordContent =
      keywords?.map((keyword) => keyword.trim()).filter(Boolean).join(', ') || null

    document.title = title
    document.documentElement.lang = 'ru'

    syncMeta('meta[name="description"]', {
      name: 'description',
      content: description,
    })
    syncMeta('meta[name="robots"]', {
      name: 'robots',
      content: robots,
    })
    syncMeta(
      'meta[name="keywords"]',
      keywordContent
        ? {
            name: 'keywords',
            content: keywordContent,
          }
        : null,
    )
    syncMeta('meta[property="og:title"]', {
      property: 'og:title',
      content: title,
    })
    syncMeta('meta[property="og:description"]', {
      property: 'og:description',
      content: description,
    })
    syncMeta('meta[property="og:type"]', {
      property: 'og:type',
      content: type,
    })
    syncMeta('meta[property="og:url"]', {
      property: 'og:url',
      content: canonicalUrl,
    })
    syncMeta('meta[property="og:site_name"]', {
      property: 'og:site_name',
      content: DEFAULT_SITE_NAME,
    })
    syncMeta('meta[property="og:locale"]', {
      property: 'og:locale',
      content: DEFAULT_LOCALE,
    })
    syncMeta('meta[name="twitter:card"]', {
      name: 'twitter:card',
      content: imageUrl ? 'summary_large_image' : 'summary',
    })
    syncMeta('meta[name="twitter:title"]', {
      name: 'twitter:title',
      content: title,
    })
    syncMeta('meta[name="twitter:description"]', {
      name: 'twitter:description',
      content: description,
    })
    syncMeta(
      'meta[property="og:image"]',
      imageUrl
        ? {
            property: 'og:image',
            content: imageUrl,
          }
        : null,
    )
    syncMeta(
      'meta[property="og:image:alt"]',
      imageUrl && imageAlt
        ? {
            property: 'og:image:alt',
            content: imageAlt,
          }
        : null,
    )
    syncMeta(
      'meta[name="twitter:image"]',
      imageUrl
        ? {
            name: 'twitter:image',
            content: imageUrl,
          }
        : null,
    )
    syncMeta(
      'meta[name="twitter:image:alt"]',
      imageUrl && imageAlt
        ? {
            name: 'twitter:image:alt',
            content: imageAlt,
          }
        : null,
    )

    upsertCanonical(canonicalUrl)
    upsertJsonLd(jsonLd)
  }, [canonicalPath, description, imageAlt, imageUrl, jsonLd, keywords, robots, title, type])

  return null
}

export default Seo
