from __future__ import annotations

from bot.utils.emojis import Emoji


def start_text(username: str) -> str:
    return (
        f"{Emoji.SMILE} Добро пожаловать, <b>{username}</b>!\n\n"
        f"Я — <b>DeployGram</b>, платформа для хостинга Python-проектов.\n\n"
        f"Загружай код, я запущу его в изолированном Docker-контейнере."
    )


def profile_text(
    username: str,
    tariff: str,
    projects_count: int,
    max_projects: int,
    balance: float,
    referral_link: str,
) -> str:
    tariff_emoji = "🆓" if tariff == "free" else "💎"
    return (
        f"{Emoji.PROFILE} <b>Профиль</b>\n\n"
        f"👤 {username}\n"
        f"📦 Проектов: <b>{projects_count}/{max_projects}</b>\n"
        f"{tariff_emoji} Тариф: <b>{tariff.title()}</b>\n"
        f"💰 Баланс: <b>{balance:.2f}</b>\n\n"
        f"🔗 Реферальная ссылка:\n<code>{referral_link}</code>"
    )


def project_card(
    name: str,
    status: str,
    python_version: str,
    entry_point: str,
    cpu: float = 0.0,
    ram: float = 0.0,
    uptime: str = "0m",
    restarts: int = 0,
) -> str:
    from bot.utils.formatters import format_status

    status_text = format_status(status)
    return (
        f"{Emoji.FILE} <b>{name}</b>\n\n"
        f"Статус: {status_text}\n"
        f"Python: {python_version}\n"
        f"Entry: <code>{entry_point}</code>\n\n"
        f"📊 Мониторинг:\n"
        f"  CPU: {cpu:.1f}%\n"
        f"  RAM: {ram:.1f} MB\n"
        f"  Uptime: {uptime}\n"
        f"  Рестартов: {restarts}"
    )


def admin_panel_text(users_count: int, projects_count: int, servers_count: int) -> str:
    return (
        f"{Emoji.SETTINGS} <b>Админ-панель</b>\n\n"
        f"👤 Пользователей: {users_count}\n"
        f"📦 Проектов: {projects_count}\n"
        f"🌍 Серверов: {servers_count}"
    )


def server_card(
    name: str,
    country: str,
    free_slots: int,
    total_slots: int,
    rating: float,
    ping: int,
    load_cpu: float,
    load_ram: float,
) -> str:
    return (
        f"{Emoji.HOME} <b>{name}</b>\n"
        f"🌍 {country}\n"
        f"📊 Слоты: {free_slots}/{total_slots}\n"
        f"⭐ Рейтинг: {rating:.1f}\n"
        f"📡 Пинг: {ping}ms\n"
        f"💻 CPU: {load_cpu:.1f}%\n"
        f"🧠 RAM: {load_ram:.1f}%"
    )
