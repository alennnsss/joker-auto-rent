// Данные с карточки компании в 2ГИС.
// Адрес на экране и режим работы — в словарях i18n (contacts.*); здесь адрес на русском
// нужен как неизменное значение места выдачи «Офис: …», которое сохраняется в брони.
export const contacts = {
  phone: '+7 (708) 006-05-06',
  whatsapp: '77080060506',
  instagram: 'https://www.instagram.com/joker_autorent/',
  twoGis: 'https://2gis.kz/almaty/firm/70000001060239372',
  address: 'ул. Казыбек би, 117, БЦ Galianos, 8 этаж, офис 803',
  map: { lat: 43.255733, lon: 76.929377, zoom: 16 },
}

export const whatsappLink = `https://wa.me/${contacts.whatsapp}`

/** Ссылка на чат WhatsApp с заранее заполненным сообщением. */
export function whatsappMessageLink(text: string): string {
  return `${whatsappLink}?text=${encodeURIComponent(text)}`
}
