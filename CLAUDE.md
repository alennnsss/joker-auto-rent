# CLAUDE.md — Joker Auto Rent

Сайт проката автомобилей **Joker Auto Rent**.
Instagram: https://www.instagram.com/joker_autorent/

Город — **Алматы, Казахстан**. Указывать город в SEO (title/description: «Аренда авто в Алматы»), разметке Schema.org `AutoRental` и на странице контактов (карта 2GIS или Яндекс.Карты). Валюта — **тенге (KZT, ₸)**, формат цены: `15 000 ₸` (пробел между разрядами, знак после числа). Телефоны в формате `+7 (7XX) XXX-XX-XX`. Часовой пояс — `Asia/Almaty`; даты на сайте — `ДД.ММ.ГГГГ`.

Язык интерфейса — **только русский**. Код, имена переменных, коммиты — на английском; комментарии в коде допускаются на русском.

---

## Стек

| Слой | Технологии |
|------|-----------|
| Frontend | Vue 3 (Composition API, `<script setup>`), TypeScript, Vite, **vue-router 4**, Pinia, Axios, SCSS |
| Backend | Python 3.12+, **FastAPI**, SQLAlchemy 2.0 (async), Alembic, Pydantic v2, asyncpg |
| База данных | **PostgreSQL 16** |
| Авторизация | JWT (access + refresh), пароли — bcrypt (`passlib`) |
| Оплата | Через абстракцию `PaymentProvider`; пока работает `MockPaymentProvider` + оплата при получении (см. «Оплата») |
| Инфраструктура | Docker Compose (postgres, backend, frontend), `.env` для секретов |
| Тесты | Backend — pytest + httpx; Frontend — Vitest + Vue Test Utils |

---

## Структура проекта

```
joker-auto-rent/
├── CLAUDE.md
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── migrations/              # Alembic миграции
│   └── app/
│       ├── main.py              # создание FastAPI-приложения, CORS, роутеры
│       ├── core/                # config (pydantic-settings), security, deps
│       ├── db/                  # engine, session, Base
│       ├── models/              # SQLAlchemy модели
│       ├── schemas/             # Pydantic-схемы (вход/выход API)
│       ├── api/v1/              # роутеры: auth, cars, bookings, payments, admin
│       ├── services/            # бизнес-логика (бронирование, оплата)
│       └── tests/
└── frontend/
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── main.ts
        ├── App.vue
        ├── router/index.ts      # vue-router
        ├── stores/              # Pinia: auth, cars, booking
        ├── api/                 # axios-инстанс и функции запросов
        ├── views/               # страницы (по одной на маршрут)
        ├── components/          # переиспользуемые компоненты
        ├── layouts/             # DefaultLayout, AdminLayout, AccountLayout
        └── styles/              # _variables.scss, _mixins.scss, main.scss
```

---

## Функциональность

1. **Каталог автомобилей** — список с фильтрами (класс, коробка, цена, количество мест, доступность на даты), карточка авто с галереей.
2. **Бронирование** — выбор дат начала/окончания, расчёт стоимости, проверка доступности, оформление заявки.
3. **Личный кабинет клиента** — регистрация/вход, профиль, история и статус бронирований, отмена брони.
4. **Оплата** — на старте: оплата при получении авто и тестовая онлайн-оплата (`mock`). Реальный провайдер подключается позже без изменений в остальном коде (см. раздел «Оплата»).
5. **Админ-панель** — CRUD автомобилей и фото, управление ценами, просмотр/подтверждение/отмена бронирований, список клиентов, платежи.

---

## Маршруты (vue-router)

Используется `createWebHistory()`. Все страницы подключаются лениво: `component: () => import('@/views/...')`.

| Путь | Имя | Доступ |
|------|-----|--------|
| `/` | `home` | все |
| `/cars` | `cars` | все |
| `/cars/:id` | `car-detail` | все |
| `/booking/:carId` | `booking` | авторизованные |
| `/about` | `about` | все |
| `/contacts` | `contacts` | все |
| `/login`, `/register` | `login`, `register` | только гости |
| `/account` | `account` | авторизованные |
| `/account/bookings` | `account-bookings` | авторизованные |
| `/payment/:bookingId` | `payment` | авторизованные |
| `/payment/success`, `/payment/fail` | — | авторизованные |
| `/admin/*` | `admin-*` | роль `admin` |
| `/:pathMatch(.*)*` | `not-found` | все |

Защита маршрутов — через `meta: { requiresAuth, guestOnly, role }` и глобальный `router.beforeEach`, который читает состояние из Pinia-стора `auth`. Включить `scrollBehavior` (прокрутка наверх при смене страницы).

---

## База данных (PostgreSQL)

Основные таблицы:

- `users` — id, email (unique), phone, full_name, password_hash, role (`client` | `admin`), created_at
- `car_categories` — id, name (эконом, комфорт, бизнес, SUV, …)
- `cars` — id, brand, model, year, category_id, transmission, fuel, seats, price_per_day, deposit, description, is_active, created_at
- `car_images` — id, car_id, url, sort_order
- `bookings` — id, user_id, car_id, start_date, end_date, total_price, payment_method (`cash` | `online`), status (`pending` | `confirmed` | `active` | `completed` | `cancelled`), created_at
- `payments` — id, booking_id, amount, provider, provider_payment_id, status (`pending` | `succeeded` | `failed` | `refunded`), created_at

Правила:
- Все изменения схемы — **только через Alembic-миграции** (`alembic revision --autogenerate`), никогда не править БД вручную.
- Деньги хранить в `NUMERIC(10, 2)`, не во `float`.
- Пересечение бронирований одного авто запрещено — проверка в сервисе + exclusion constraint в PostgreSQL (`btree_gist`, `daterange`).
- Индексы на `bookings(car_id, start_date, end_date)` и внешние ключи.

---

## Backend API (FastAPI)

Все эндпоинты под префиксом `/api/v1`. Swagger доступен на `/docs`.

- `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `GET /auth/me`
- `GET /cars` (фильтры через query), `GET /cars/{id}`, `GET /cars/{id}/availability`
- `POST /bookings`, `GET /bookings/my`, `POST /bookings/{id}/cancel`
- `POST /payments/{booking_id}/create`, `POST /payments/webhook`
- `/admin/cars`, `/admin/bookings`, `/admin/users`, `/admin/payments` — только для роли `admin`

Правила:
- Роутеры тонкие: валидация через Pydantic, логика — в `services/`.
- Зависимости (`Depends`) для сессии БД, текущего пользователя и проверки роли.
- Цена брони считается **только на сервере**, клиентской сумме не доверять.
- Webhook оплаты проверяет подпись провайдера и идемпотентен.
- Ошибки возвращать через `HTTPException` с понятным `detail` на русском (показывается пользователю).
- CORS разрешает только адрес фронтенда из `.env`.

---

## Оплата

Платёжный провайдер **ещё не выбран** (зависит от страны работы и договора владельца). Поэтому оплата строится так, чтобы провайдера можно было заменить, не трогая остальной код.

- `backend/app/services/payments/base.py` — абстрактный класс `PaymentProvider`:
  - `create_payment(booking, amount) -> PaymentInit` (id платежа у провайдера + `redirect_url`)
  - `verify_webhook(headers, body) -> bool`
  - `parse_webhook(body) -> PaymentEvent` (provider_payment_id, status)
  - `refund(payment) -> None`
- `backend/app/services/payments/mock.py` — `MockPaymentProvider` для разработки: сразу возвращает `redirect_url` на `/payment/success?booking=...` и помечает платёж `succeeded`. Webhook-подпись не проверяет. **Запрещён при `ENV=production`** — приложение должно падать на старте.
- `backend/app/services/payments/__init__.py` — фабрика `get_payment_provider()`, выбирает реализацию по `PAYMENT_PROVIDER` (`mock` | `cash` | позже один из казахстанских: `kaspi`, `freedompay`, `halyk`, `cloudpayments`).
- Способ оплаты при бронировании: `payment_method` в `bookings` — `cash` (при получении) или `online`. Пока онлайн-провайдер не настроен, на фронте доступен только `cash` (флаг приходит с бэкенда `GET /api/v1/config`).
- Бронь с `cash` создаётся со статусом `pending` и подтверждается администратором вручную.
- Роутеры и фронтенд **не знают** о конкретном провайдере — работают только через `PaymentProvider` и свои эндпоинты.

Чтобы подключить реального провайдера: добавить файл `services/payments/<provider>.py`, реализовать 4 метода, зарегистрировать в фабрике, прописать ключи в `.env`, написать тесты на webhook.

---

## Дизайн: черно-золотая тема

Стиль — премиальный, тёмный фон, золотые акценты. Все цвета задаются **только через переменные** в `src/styles/_variables.scss` / CSS custom properties, хардкод цветов в компонентах запрещён.

```scss
:root {
  --color-bg:            #0b0b0b;   // основной фон
  --color-surface:       #161616;   // карточки, шапка
  --color-surface-2:     #1f1f1f;   // ховеры, инпуты
  --color-gold:          #d4af37;   // основной акцент
  --color-gold-light:    #f1d27a;   // ховер / градиент
  --color-gold-dark:     #a8862a;   // нажатие / границы
  --color-text:          #f5f5f5;
  --color-text-muted:    #a3a3a3;
  --color-border:        #2a2a2a;
  --color-danger:        #e5484d;
  --color-success:       #3fb950;
  --gradient-gold: linear-gradient(135deg, #a8862a 0%, #d4af37 50%, #f1d27a 100%);
}
```

- Кнопки CTA («Забронировать») — золотой градиент, тёмный текст.
- Заголовки — шрифт с засечками или строгий display (например, Playfair Display / Montserrat), основной текст — Inter / Montserrat, с поддержкой кириллицы.
- Контраст текста — не ниже WCAG AA.
- Анимации сдержанные (150–300 мс), уважать `prefers-reduced-motion`.

---

## Адаптивная вёрстка

Подход **mobile-first**: базовые стили для телефона, расширение через `min-width`.

```scss
$bp-sm: 576px;   // большие телефоны
$bp-md: 768px;   // планшеты
$bp-lg: 1024px;  // ноутбуки
$bp-xl: 1280px;  // десктоп
$bp-xxl: 1536px; // большие экраны
```

- Миксин `@include media(md) { ... }` в `_mixins.scss`, сырые media-запросы в компонентах не писать.
- Сетка каталога: 1 колонка → 2 (md) → 3 (lg) → 4 (xxl).
- На мобильных — бургер-меню, фиксированная кнопка «Позвонить / WhatsApp», нижние отступы под safe-area (`env(safe-area-inset-bottom)`).
- Высоту экрана задавать через `100dvh`, а не `100vh`.
- Размер шрифта в инпутах ≥ 16px (чтобы iOS не зумил страницу).
- Тач-цели не меньше 44×44px.
- Изображения — `loading="lazy"`, `srcset`, формат WebP.
- Проверять на ширинах: 360, 390, 768, 1024, 1440, 1920.

---

## Команды

```bash
# Всё окружение
docker compose up -d

# Backend
cd backend
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload          # http://localhost:8000, docs: /docs
pytest
ruff check . && ruff format .

# Frontend
cd frontend
npm install
npm run dev                            # http://localhost:5173
npm run build
npm run test
npm run lint
```

Vite проксирует `/api` на `http://localhost:8000` (`server.proxy` в `vite.config.ts`).

---

## Переменные окружения (`.env.example`)

```
DATABASE_URL=postgresql+asyncpg://joker:joker@localhost:5432/joker_auto_rent
JWT_SECRET=change-me
JWT_ACCESS_TTL_MIN=30
JWT_REFRESH_TTL_DAYS=30
ENV=development                  # development | production
FRONTEND_URL=http://localhost:5173
CURRENCY=KZT
TIMEZONE=Asia/Almaty
PAYMENT_PROVIDER=mock            # mock | cash | позже: kaspi | freedompay | halyk | cloudpayments
PAYMENT_API_KEY=
PAYMENT_WEBHOOK_SECRET=
```

Реальный `.env` не коммитить.

---

## Соглашения

- Vue: только Composition API и `<script setup lang="ts">`, компоненты в PascalCase, один компонент — один файл.
- Стили компонентов — `<style scoped lang="scss">`.
- Запросы к API — только через модули в `src/api/`, не вызывать axios прямо из компонентов.
- Python: type hints везде, `ruff` для линтинга и форматирования.
- Перед завершением задачи: прогнать линтеры и тесты, проверить вёрстку на мобильной и десктопной ширине.
- Не добавлять новые зависимости без необходимости.

---

## Открытые вопросы

- [ ] Платёжный провайдер (Казахстан) — выбирает владелец после заключения договора: Kaspi Pay, Freedom Pay (бывш. PayBox), Halyk ePay или CloudPayments KZ. До этого — `mock` + оплата при получении.
- [ ] Контакты в Алматы (телефон, WhatsApp, Telegram, адрес выдачи авто) — взять из Instagram или у владельца.
- [ ] Логотип и фирменные шрифты Joker Auto Rent.
- [ ] Хостинг и домен.
