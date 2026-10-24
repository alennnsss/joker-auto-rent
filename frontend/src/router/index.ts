import {
  createRouter,
  createWebHistory,
  type RouteLocationNormalizedLoaded,
  type RouteRecordRaw,
} from 'vue-router'

import { i18n } from '@/i18n'
import type { MessageSchema } from '@/i18n/locales/ru'
import { useAuthStore } from '@/stores/auth'

declare module 'vue-router' {
  interface RouteMeta {
    /** Ключ из словаря titles.* */
    title?: keyof MessageSchema['titles']
    requiresAuth?: boolean
    guestOnly?: boolean
    role?: 'admin'
  }
}

const SITE_NAME = 'Joker Auto Rent'

/** Заголовок вкладки на текущем языке; App.vue вызывает его и при смене языка. */
export function applyTitle(route: RouteLocationNormalizedLoaded) {
  const key = route.meta.title
  document.title = key ? `${i18n.global.t(`titles.${key}`)} — ${SITE_NAME}` : SITE_NAME
}

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('@/views/HomeView.vue'),
        meta: { title: 'home' },
      },
      {
        path: 'cars',
        name: 'cars',
        component: () => import('@/views/CarsView.vue'),
        meta: { title: 'cars' },
      },
      {
        path: 'cars/:id(\\d+)',
        name: 'car-detail',
        component: () => import('@/views/CarDetailView.vue'),
        props: (route) => ({ id: Number(route.params.id) }),
        meta: { title: 'car' },
      },
      {
        path: 'booking/:carId(\\d+)',
        name: 'booking',
        component: () => import('@/views/BookingView.vue'),
        props: (route) => ({ carId: Number(route.params.carId) }),
        meta: { title: 'booking', requiresAuth: true },
      },
      {
        path: 'about',
        name: 'about',
        component: () => import('@/views/AboutView.vue'),
        meta: { title: 'about' },
      },
      {
        path: 'contacts',
        name: 'contacts',
        component: () => import('@/views/ContactsView.vue'),
        meta: { title: 'contacts' },
      },
      {
        path: 'login',
        name: 'login',
        component: () => import('@/views/LoginView.vue'),
        meta: { title: 'login', guestOnly: true },
      },
      {
        path: 'register',
        name: 'register',
        component: () => import('@/views/RegisterView.vue'),
        meta: { title: 'register', guestOnly: true },
      },
      {
        path: 'verify-email',
        name: 'verify-email',
        component: () => import('@/views/VerifyEmailView.vue'),
        meta: { title: 'verify', requiresAuth: true },
      },
      {
        path: 'payment/success',
        name: 'payment-success',
        component: () => import('@/views/PaymentResultView.vue'),
        props: { success: true },
        meta: { title: 'paymentSuccess', requiresAuth: true },
      },
      {
        path: 'payment/fail',
        name: 'payment-fail',
        component: () => import('@/views/PaymentResultView.vue'),
        props: { success: false },
        meta: { title: 'paymentFail', requiresAuth: true },
      },
      {
        path: 'payment/:bookingId(\\d+)',
        name: 'payment',
        component: () => import('@/views/PaymentView.vue'),
        props: (route) => ({ bookingId: Number(route.params.bookingId) }),
        meta: { title: 'payment', requiresAuth: true },
      },
      {
        path: 'account',
        component: () => import('@/layouts/AccountLayout.vue'),
        meta: { requiresAuth: true },
        children: [
          {
            path: '',
            name: 'account',
            component: () => import('@/views/AccountView.vue'),
            meta: { title: 'account' },
          },
          {
            path: 'bookings',
            name: 'account-bookings',
            component: () => import('@/views/AccountBookingsView.vue'),
            meta: { title: 'accountBookings' },
          },
        ],
      },
    ],
  },
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      { path: '', name: 'admin', redirect: { name: 'admin-bookings' } },
      {
        path: 'bookings',
        name: 'admin-bookings',
        component: () => import('@/views/admin/AdminBookingsView.vue'),
        meta: { title: 'adminBookings' },
      },
      {
        path: 'cars',
        name: 'admin-cars',
        component: () => import('@/views/admin/AdminCarsView.vue'),
        meta: { title: 'adminCars' },
      },
      {
        path: 'cars/new',
        name: 'admin-car-new',
        component: () => import('@/views/admin/AdminCarEditView.vue'),
        meta: { title: 'adminCarNew' },
      },
      {
        path: 'cars/:id(\\d+)',
        name: 'admin-car-edit',
        component: () => import('@/views/admin/AdminCarEditView.vue'),
        props: (route) => ({ id: Number(route.params.id) }),
        meta: { title: 'adminCarEdit' },
      },
      {
        path: 'users',
        name: 'admin-users',
        component: () => import('@/views/admin/AdminUsersView.vue'),
        meta: { title: 'adminUsers' },
      },
      {
        path: 'payments',
        name: 'admin-payments',
        component: () => import('@/views/admin/AdminPaymentsView.vue'),
        meta: { title: 'adminPayments' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    component: () => import('@/layouts/DefaultLayout.vue'),
    children: [
      {
        path: '',
        name: 'not-found',
        component: () => import('@/views/NotFoundView.vue'),
        meta: { title: 'notFound' },
      },
    ],
  },
]

export function createAppRouter() {
  const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes,
    scrollBehavior(to, _from, savedPosition) {
      if (savedPosition) return savedPosition
      if (to.hash) return { el: to.hash, top: 80 }
      return { top: 0 }
    },
  })

  router.beforeEach(async (to) => {
    const auth = useAuthStore()
    await auth.init()

    if (to.meta.requiresAuth && !auth.isAuthenticated) {
      return { name: 'login', query: { redirect: to.fullPath } }
    }
    if (to.meta.guestOnly && auth.isAuthenticated) {
      return { name: 'home' }
    }
    if (to.meta.role === 'admin' && !auth.isAdmin) {
      return { name: 'home' }
    }
  })

  router.afterEach((to) => applyTitle(to))

  return router
}

export default createAppRouter()
