from fastapi import APIRouter, status

from app.core.deps import AppSettings, CurrentUser, DbSession, RequestLang
from app.schemas.auth import (
    LoginIn,
    RefreshIn,
    RegisterIn,
    TokenPair,
    UserOut,
    UserUpdate,
    VerifyEmailIn,
)
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterIn, db: DbSession, settings: AppSettings, lang: RequestLang
) -> TokenPair:
    return await auth_service.register(db, data, settings, lang)


@router.post("/login", response_model=TokenPair)
async def login(data: LoginIn, db: DbSession, settings: AppSettings) -> TokenPair:
    return await auth_service.login(db, data, settings)


@router.post("/refresh", response_model=TokenPair)
async def refresh(data: RefreshIn, db: DbSession, settings: AppSettings) -> TokenPair:
    return await auth_service.refresh(db, data.refresh_token, settings)


@router.get("/me", response_model=UserOut)
async def me(user: CurrentUser) -> UserOut:
    return UserOut.model_validate(user)


@router.post("/verify-email", response_model=UserOut)
async def verify_email(
    data: VerifyEmailIn, user: CurrentUser, db: DbSession, settings: AppSettings
) -> UserOut:
    return UserOut.model_validate(await auth_service.verify_email(db, user, data.code, settings))


@router.post("/resend-verification", status_code=status.HTTP_204_NO_CONTENT)
async def resend_verification(
    user: CurrentUser, db: DbSession, settings: AppSettings, lang: RequestLang
) -> None:
    await auth_service.resend_verification(db, user, settings, lang)


@router.patch("/me", response_model=UserOut)
async def update_me(data: UserUpdate, user: CurrentUser, db: DbSession) -> UserOut:
    return UserOut.model_validate(await auth_service.update_profile(db, user, data))
