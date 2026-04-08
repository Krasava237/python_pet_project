import { render } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import Seo from './Seo'

describe('Seo', () => {
  it('updates title, canonical link, keywords, social meta tags, and JSON-LD', () => {
    render(
      <Seo
        canonicalPath="/pets/12-lucky"
        description="Подробная карточка питомца."
        imageAlt="Фото питомца Лаки"
        imageUrl="https://example.com/lucky.jpg"
        jsonLd={{ '@context': 'https://schema.org', '@type': 'BreadcrumbList' }}
        keywords={['pet finder', 'lost pet', 'lucky']}
        title="Lucky | Pet Finder"
        type="article"
      />,
    )

    expect(document.title).toBe('Lucky | Pet Finder')
    expect(document.querySelector('meta[name="description"]')).toHaveAttribute(
      'content',
      'Подробная карточка питомца.',
    )
    expect(document.querySelector('meta[name="keywords"]')).toHaveAttribute(
      'content',
      'pet finder, lost pet, lucky',
    )
    expect(document.querySelector('meta[property="og:type"]')).toHaveAttribute(
      'content',
      'article',
    )
    expect(document.querySelector('meta[property="og:site_name"]')).toHaveAttribute(
      'content',
      'Pet Finder',
    )
    expect(document.querySelector('meta[property="og:locale"]')).toHaveAttribute(
      'content',
      'ru_RU',
    )
    expect(document.querySelector('meta[property="og:image"]')).toHaveAttribute(
      'content',
      'https://example.com/lucky.jpg',
    )
    expect(document.querySelector('meta[property="og:image:alt"]')).toHaveAttribute(
      'content',
      'Фото питомца Лаки',
    )
    expect(document.querySelector('meta[name="twitter:title"]')).toHaveAttribute(
      'content',
      'Lucky | Pet Finder',
    )
    expect(document.querySelector('meta[name="twitter:description"]')).toHaveAttribute(
      'content',
      'Подробная карточка питомца.',
    )
    expect(document.querySelector('meta[name="twitter:image"]')).toHaveAttribute(
      'content',
      'https://example.com/lucky.jpg',
    )
    expect(document.querySelector('meta[name="twitter:image:alt"]')).toHaveAttribute(
      'content',
      'Фото питомца Лаки',
    )
    expect(document.querySelector('link[rel="canonical"]')).toHaveAttribute(
      'href',
      'http://localhost:3000/pets/12-lucky',
    )
    expect(document.getElementById('seo-jsonld')?.textContent).toContain(
      '"@type":"BreadcrumbList"',
    )
  })
})
