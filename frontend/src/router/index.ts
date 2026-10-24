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
        path: 'about',
        name: 'about',
        component: () => import('@/views/AboutView.vue'),
        meta: { title: 'about' },
      },
      {
        path: 'rules',
        name: 'rules',
        component: () => import('@/views/RulesView.vue'),
        meta: { title: 'rules' },
      },
      {
        path: 'contacts',
        name: 'contacts',
        component: () => import('@/views/ContactsView.vue'),
        meta: { title: 'contacts' },
      },
    ],
  },
  {
    path: '/admin/login',
    component: () => import('@/layouts/DefaultLayout.vue'),
    children: [
      {
        path: '',
        name: 'admin-login',
        component: () => import('@/views/admin/AdminLoginView.vue'),
        meta: { title: 'adminLogin', guestOnly: true },
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

    // Вход есть только у администратора
    if (to.meta.requiresAuth && !auth.isAuthenticated) {
      return { name: 'admin-login', query: { redirect: to.fullPath } }
    }
    if (to.meta.guestOnly && auth.isAdmin) {
      return { name: 'admin' }
    }
    if (to.meta.role === 'admin' && !auth.isAdmin) {
      return { name: 'home' }
    }
  })

  router.afterEach((to) => applyTitle(to))

  return router
}

export default createAppRouter()
