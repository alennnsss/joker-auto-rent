const WIDTHS = [400, 800, 1200, 1600]

function isUnsplash(url: string) {
  return url.startsWith('https://images.unsplash.com/')
}

function withWidth(url: string, width: number) {
  const u = new URL(url)
  u.searchParams.set('w', String(width))
  u.searchParams.set('fm', 'webp')
  u.searchParams.delete('auto')
  return u.toString()
}

/** src + srcset для фото авто. Для CDN с ресайзом — несколько ширин в WebP. */
export function imageSources(url: string | undefined, maxWidth = 1200) {
  if (!url) return { src: '', srcset: undefined }
  if (!isUnsplash(url)) return { src: url, srcset: undefined }
  const widths = WIDTHS.filter((w) => w <= maxWidth)
  return {
    src: withWidth(url, maxWidth),
    srcset: widths.map((w) => `${withWidth(url, w)} ${w}w`).join(', '),
  }
}
