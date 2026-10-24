import asyncio
import logging
import smtplib
import sys
from email.message import EmailMessage

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


def _send_sync(settings: Settings, to: str, subject: str, body: str) -> None:
    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    # 465 — SSL с первого байта, 587 — обычное подключение + STARTTLS
    if settings.smtp_port == 465:
        smtp: smtplib.SMTP = smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=15)
    else:
        smtp = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15)
    with smtp:
        if settings.smtp_port != 465 and settings.smtp_tls:
            smtp.starttls()
        if settings.smtp_user:
            smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(message)


async def send_email(settings: Settings, to: str, subject: str, body: str) -> None:
    """Отправляет письмо. Без SMTP_HOST (разработка) — пишет письмо в лог."""
    if not settings.smtp_host:
        logger.warning("SMTP is not configured, email to %s:\n%s\n%s", to, subject, body)
        return
    await asyncio.to_thread(_send_sync, settings, to, subject, body)


if __name__ == "__main__":
    # Проверка настроек почты: python -m app.services.email you@example.com
    if len(sys.argv) != 2:
        sys.exit("Usage: python -m app.services.email <recipient>")
    settings = get_settings()
    if not settings.smtp_host:
        sys.exit("SMTP_HOST is empty — fill SMTP_* in .env first")
    _send_sync(
        settings,
        sys.argv[1],
        "Проверка почты Joker Auto Rent",
        "Если вы видите это письмо, отправка кодов подтверждения настроена верно.",
    )
    print(f"Sent via {settings.smtp_host}:{settings.smtp_port} to {sys.argv[1]}")
