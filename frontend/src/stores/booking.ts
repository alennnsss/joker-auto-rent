import { defineStore } from 'pinia'
import { ref } from 'vue'

import { OFFICE_LOCATION } from '@/config/locations'
import { addDays, todayIso } from '@/utils/date'

/** Параметры поездки: где и когда забрать и вернуть автомобиль. */
export interface Trip {
  pickupLocation: string
  pickupDate: string
  pickupTime: string
  returnLocation: string
  returnDate: string
  returnTime: string
}

export function defaultTrip(): Trip {
  const start = addDays(todayIso(), 1)
  return {
    pickupLocation: OFFICE_LOCATION,
    pickupDate: start,
    pickupTime: '10:00',
    returnLocation: OFFICE_LOCATION,
    returnDate: addDays(start, 3),
    returnTime: '10:00',
  }
}

/** Черновик брони (переносится между главной, каталогом и карточкой авто). */
export const useBookingStore = defineStore('booking', () => {
  const trip = ref<Trip>(defaultTrip())

  function setDates(start: string, end: string) {
    trip.value = { ...trip.value, pickupDate: start, returnDate: end }
  }

  function reset() {
    trip.value = defaultTrip()
  }


  return { trip, setDates, reset }
})
