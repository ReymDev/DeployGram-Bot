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
    tariff_text = f"{Emoji.BOX} Free" if tariff == "free" else f"{Emoji.GIFT} Premium"
    return (
        f"{Emoji.PROFILE} <b>Профиль</b>\n\n"
        f"{Emoji.PROFILE} {username}\n"
        f"{Emoji.FILE} Проектов: <b>{projects_count}/{max_projects}</b>\n"
        f"{tariff_text} Тариф: <b>{tariff.title()}</b>\n"
        f"{Emoji.COIN} Баланс: <b>{balance:.2f}</b>\n\n"
        f"{Emoji.LINK} Реферальная ссылка:\n<code>{referral_link}</code>"
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
        f"{Emoji.GRAPH_STATS} Мониторинг:\n"
        f"  CPU: {cpu:.1f}%\n"
        f"  RAM: {ram:.1f} MB\n"
        f"  Uptime: {uptime}\n"
        f"  Рестартов: {restarts}"
    )


def admin_panel_text(users_count: int, projects_count: int, servers_count: int) -> str:
    return (
        f"{Emoji.SETTINGS} <b>Админ-панель</b>\n\n"
        f"{Emoji.PROFILE} Пользователей: {users_count}\n"
        f"{Emoji.FILE} Проектов: {projects_count}\n"
        f"{Emoji.HOME} Серверов: {servers_count}"
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
        f"{Emoji.PIN} {country}\n"
        f"{Emoji.GRAPH_STATS} Слоты: {free_slots}/{total_slots}\n"
        f"{Emoji.INFO} Рейтинг: {rating:.1f}\n"
        f"{Emoji.SEND} Пинг: {ping}ms\n"
        f"{Emoji.CODE} CPU: {load_cpu:.1f}%\n"
        f"{Emoji.GRAPH_UP} RAM: {load_ram:.1f}%"
    )
