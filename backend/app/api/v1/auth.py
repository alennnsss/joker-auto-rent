from fastapi import APIRouter

from app.core.deps import AppSettings, CurrentUser, DbSession
from app.schemas.auth import LoginIn, RefreshIn, TokenPair, UserOut
from app.services import auth as auth_service

# Вход только для администратора: клиенты бронируют через WhatsApp без аккаунта
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenPair)
async def login(data: LoginIn, db: DbSession, settings: AppSettings) -> TokenPair:
    return await auth_service.login(db, data, settings)


@router.post("/refresh", response_model=TokenPair)
async def refresh(data: RefreshIn, db: DbSession, settings: AppSettings) -> TokenPair:
    return await auth_service.refresh(db, data.refresh_token, settings)


@router.get("/me", response_model=UserOut)
async def me(user: CurrentUser) -> UserOut:
    return UserOut.model_validate(user)
