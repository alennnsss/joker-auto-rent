import { defineStore } from 'pinia'
import { ref } from 'vue'

import { OFFICE_LOCATION } from '@/config/locations'
import { clampTerm } from '@/config/terms'
import { addDays, todayIso } from '@/utils/date'

/** Параметры поездки: где и когда забрать автомобиль и на сколько суток. */
export interface Trip {
  pickupLocation: string
  pickupDate: string
  pickupTime: string
  days: number
}

export function defaultTrip(): Trip {
  return {
    pickupLocation: OFFICE_LOCATION,
    pickupDate: addDays(todayIso(), 1),
    pickupTime: '10:00',
    days: 1,
  }
}

/** Дата возврата: получение + срок. Показывается только в итоге брони. */
export function returnDate(trip: Pick<Trip, 'pickupDate' | 'days'>): string {
  return trip.pickupDate ? addDays(trip.pickupDate, trip.days) : ''
}

/** Черновик брони (переносится между каталогом и карточкой авто). */
export const useBookingStore = defineStore('booking', () => {
  const trip = ref<Trip>(defaultTrip())

  function setTerm(start: string, days: number) {
    trip.value = { ...trip.value, pickupDate: start || trip.value.pickupDate, days: clampTerm(days) }
  }

  function reset() {
    trip.value = defaultTrip()
  }

  return { trip, setTerm, reset }
})
