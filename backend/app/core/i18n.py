"""Перевод текстов ошибок API на казахский.

Сервисы пишут detail на русском (это исходный текст). На границе API обработчики
исключений переводят его на язык из заголовка Accept-Language, который присылает фронтенд.
Неизвестный текст возвращается как есть — по-русски.
"""

import re
from typing import Literal

Lang = Literal["ru", "kk"]

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

# Тексты с подставляемыми значениями: (шаблон по русскому тексту, казахский шаблон)
KK_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"^Нельзя перевести бронь из статуса «(.+)» в «(.+)»$"),
        r"Брондауды «\1» мәртебесінен «\2» мәртебесіне ауыстыруға болмайды",
    ),
]

# Причины ошибок валидации Pydantic (по error type)
VALIDATION_REASONS: dict[str, dict[Lang, str]] = {
    "missing": {"ru": "обязательное поле", "kk": "міндетті өріс"},
    "string_too_short": {"ru": "слишком короткое значение", "kk": "мәні тым қысқа"},
    "string_too_long": {"ru": "слишком длинное значение", "kk": "мәні тым ұзын"},
    "value_error": {"ru": "некорректное значение", "kk": "мәні қате"},
    "date_from_datetime_parsing": {"ru": "некорректная дата", "kk": "күні қате"},
    "date_parsing": {"ru": "некорректная дата", "kk": "күні қате"},
    "int_parsing": {"ru": "ожидается целое число", "kk": "бүтін сан күтіледі"},
    "decimal_parsing": {"ru": "ожидается число", "kk": "сан күтіледі"},
    "enum": {"ru": "недопустимое значение", "kk": "рұқсат етілмеген мән"},
    "greater_than": {"ru": "значение слишком маленькое", "kk": "мәні тым кіші"},
    "greater_than_equal": {"ru": "значение слишком маленькое", "kk": "мәні тым кіші"},
    "less_than_equal": {"ru": "значение слишком большое", "kk": "мәні тым үлкен"},
}


def parse_lang(accept_language: str | None) -> Lang:
    """«kk», «kk-KZ», «kk,ru;q=0.8» → kk; всё остальное — ru."""
    first = (accept_language or "").split(",")[0].strip().lower()
    return "kk" if first.split("-")[0] == "kk" else "ru"


def translate(text: str, lang: Lang) -> str:
    if lang == "ru":
        return text
    if text in KK:
        return KK[text]
    for pattern, template in KK_PATTERNS:
        if pattern.match(text):
            return pattern.sub(template, text)
    return text


def validation_detail(field: str | None, error_type: str, lang: Lang) -> str:
    """Сообщение для поля, не прошедшего валидацию Pydantic."""
    reasons = VALIDATION_REASONS.get(error_type, VALIDATION_REASONS["value_error"])
    if lang == "kk":
        return f"«{field or 'сұраныс'}» өрісі: {reasons['kk']}"
    return f"Поле «{field or 'запрос'}»: {reasons['ru']}"
