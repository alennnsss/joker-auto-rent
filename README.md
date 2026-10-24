# Joker Auto Rent

Сайт проката автомобилей в Алматы: каталог, онлайн-бронирование, личный кабинет, оплата
(пока `mock` и оплата при получении) и админ-панель. Требования и соглашения — в [CLAUDE.md](CLAUDE.md).

## Быстрый старт (Docker)

```bash
cp .env.example .env
docker compose up -d
docker compose exec backend python -m app.seed   # категории, админ, демо-авто
```

- Сайт: http://localhost:5173
- API и Swagger: http://localhost:8000/docs
- Админ: `admin@joker.kz` / `admin12345` (меняется через `ADMIN_EMAIL` / `ADMIN_PASSWORD`)

## Локально без Docker

```bash
# Backend (нужен PostgreSQL 16 с базой из DATABASE_URL)
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Проверки

```bash
cd backend && pytest && ruff check . && ruff format --check .
cd frontend && npm run type-check && npm run test && npm run lint
```

Тесты бэкенда по умолчанию идут на SQLite. Чтобы проверить их на PostgreSQL, задайте
`TEST_DATABASE_URL=postgresql+asyncpg://…` (отдельная тестовая база — она очищается).

## Что нужно от владельца

См. «Открытые вопросы» в CLAUDE.md: платёжный провайдер, реальные контакты
(`frontend/src/config/contacts.ts`), логотип, хостинг и домен.
