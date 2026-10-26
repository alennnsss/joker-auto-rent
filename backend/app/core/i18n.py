"""Перевод текстов ошибок API на казахский и английский.

Сервисы пишут detail на русском (это исходный текст). На границе API обработчики
исключений переводят его на язык из заголовка Accept-Language, который присылает фронтенд.
Неизвестный текст возвращается как есть — по-русски.
"""

import re
from typing import Literal

Lang = Literal["ru", "kk", "en"]

KK: dict[str, str] = {
    # core/deps.py
    "Требуется авторизация": "Авторизация қажет",
    "Недостаточно прав": "Құқық жеткіліксіз",
    # schemas
    "Дата окончания должна быть позже даты начала": (
        "Аяқталу күні басталу күнінен кейін болуы керек"
    ),
    "Укажите обе даты: начала и окончания аренды": (
        "Жалға алудың басталу және аяқталу күндерін көрсетіңіз"
    ),
    # services/auth.py
    "Неверный email или пароль": "Email немесе құпиясөз қате",
    "Сессия истекла, войдите снова": "Сеанс мерзімі өтті, қайта кіріңіз",
    # services/bookings.py
    "Бронирование не найдено": "Брондау табылмады",
    "Автомобиль не найден": "Көлік табылмады",
    # services/cars.py
    "Такая категория уже существует": "Мұндай класс бар",
    "Категория не найдена": "Класс табылмады",
    "У автомобиля есть бронирования — удалить нельзя, сделайте его неактивным": (
        "Көліктің брондаулары бар — жоюға болмайды, оны белсенді емес етіңіз"
    ),
    "Допустимые форматы: WebP, JPEG, PNG": "Рұқсат етілген форматтар: WebP, JPEG, PNG",
    "Файл больше 10 МБ": "Файл 10 МБ-тан үлкен",
    "Фото не найдено": "Сурет табылмады",
}

EN: dict[str, str] = {
    # core/deps.py
    "Требуется авторизация": "Authorization required",
    "Недостаточно прав": "Insufficient permissions",
    # schemas
    "Дата окончания должна быть позже даты начала": (
        "The end date must be later than the start date"
    ),
    "Укажите обе даты: начала и окончания аренды": "Specify both the rental start and end dates",
    # services/auth.py
    "Неверный email или пароль": "Invalid email or password",
    "Сессия истекла, войдите снова": "Session expired, please log in again",
    # services/bookings.py
    "Бронирование не найдено": "Booking not found",
    "Автомобиль не найден": "Car not found",
    # services/cars.py
    "Такая категория уже существует": "This class already exists",
    "Категория не найдена": "Class not found",
    "У автомобиля есть бронирования — удалить нельзя, сделайте его неактивным": (
        "The car has bookings and cannot be deleted — make it inactive instead"
    ),
    "Допустимые форматы: WebP, JPEG, PNG": "Allowed formats: WebP, JPEG, PNG",
    "Файл больше 10 МБ": "The file is larger than 10 MB",
    "Фото не найдено": "Photo not found",
}

# Тексты с подставляемыми значениями: (шаблон по русскому тексту, перевод)
KK_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"^Нельзя перевести бронь из статуса «(.+)» в «(.+)»$"),
        r"Брондауды «\1» мәртебесінен «\2» мәртебесіне ауыстыруға болмайды",
    ),
]

EN_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"^Нельзя перевести бронь из статуса «(.+)» в «(.+)»$"),
        r"Cannot change the booking status from “\1” to “\2”",
    ),
]

DICTIONARIES: dict[Lang, tuple[dict[str, str], list[tuple[re.Pattern[str], str]]]] = {
    "kk": (KK, KK_PATTERNS),
    "en": (EN, EN_PATTERNS),
}

# Причины ошибок валидации Pydantic (по error type)
VALIDATION_REASONS: dict[str, dict[Lang, str]] = {
    "missing": {"ru": "обязательное поле", "kk": "міндетті өріс", "en": "required field"},
    "string_too_short": {
        "ru": "слишком короткое значение",
        "kk": "мәні тым қысқа",
        "en": "value is too short",
    },
    "string_too_long": {
        "ru": "слишком длинное значение",
        "kk": "мәні тым ұзын",
        "en": "value is too long",
    },
    "value_error": {"ru": "некорректное значение", "kk": "мәні қате", "en": "invalid value"},
    "date_from_datetime_parsing": {
        "ru": "некорректная дата",
        "kk": "күні қате",
        "en": "invalid date",
    },
    "date_parsing": {"ru": "некорректная дата", "kk": "күні қате", "en": "invalid date"},
    "int_parsing": {
        "ru": "ожидается целое число",
        "kk": "бүтін сан күтіледі",
        "en": "an integer is expected",
    },
    "decimal_parsing": {
        "ru": "ожидается число",
        "kk": "сан күтіледі",
        "en": "a number is expected",
    },
    "enum": {
        "ru": "недопустимое значение",
        "kk": "рұқсат етілмеген мән",
        "en": "value is not allowed",
    },
    "greater_than": {
        "ru": "значение слишком маленькое",
        "kk": "мәні тым кіші",
        "en": "value is too small",
    },
    "greater_than_equal": {
        "ru": "значение слишком маленькое",
        "kk": "мәні тым кіші",
        "en": "value is too small",
    },
    "less_than_equal": {
        "ru": "значение слишком большое",
        "kk": "мәні тым үлкен",
        "en": "value is too large",
    },
}


def parse_lang(accept_language: str | None) -> Lang:
    """«kk», «kk-KZ», «kk,ru;q=0.8» → kk; «en», «en-US» → en; всё остальное — ru."""
    first = (accept_language or "").split(",")[0].strip().lower().split("-")[0]
    if first == "kk":
        return "kk"
    if first == "en":
        return "en"
    return "ru"


def translate(text: str, lang: Lang) -> str:
    if lang == "ru":
        return text
    words, patterns = DICTIONARIES[lang]
    if text in words:
        return words[text]
    for pattern, template in patterns:
        if pattern.match(text):
            return pattern.sub(template, text)
    return text


def validation_detail(field: str | None, error_type: str, lang: Lang) -> str:
    """Сообщение для поля, не прошедшего валидацию Pydantic."""
    reasons = VALIDATION_REASONS.get(error_type, VALIDATION_REASONS["value_error"])
    if lang == "kk":
        return f"«{field or 'сұраныс'}» өрісі: {reasons['kk']}"
    if lang == "en":
        return f"Field “{field or 'request'}”: {reasons['en']}"
    return f"Поле «{field or 'запрос'}»: {reasons['ru']}"
