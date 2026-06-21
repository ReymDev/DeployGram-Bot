"""
DeployGram Bot - Полный тест всех хендлеров
Запуск: python -m tests.test_all
"""
from __future__ import annotations

import asyncio
import io
import os
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["BOT_TOKEN"] = "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi"
os.environ["ADMIN_IDS"] = "123456789"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Chat, Message, Update, User

from db.engine import engine
from models.base import Base
import models
from bot.main import setup_dispatcher

TOKEN = "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi"
UID = 123456789
ADMIN_UID = 987654321

_original_make_request = AiohttpSession.make_request

async def _fake_make_request(self, bot, method, timeout=None):
    return {"ok": True, "result": True}

AiohttpSession.make_request = _fake_make_request


def mu(uid=UID):
    return User(id=uid, is_bot=False, first_name="Test", username="testuser")

def mm(text, user=None):
    u = user or mu()
    return Message(message_id=1, date=1234567890, chat=Chat(id=u.id, type="private"), from_user=u, text=text)

def mc(data, user=None):
    u = user or mu()
    return CallbackQuery(id="cb1", from_user=u, chat_instance="test", data=data, message=mm("old", u))


class R:
    def __init__(self):
        self.p = self.f = 0
        self.e = []
    def ok(self, n):
        self.p += 1
        print(f"  [OK] {n}")
    def fail(self, n, r):
        self.f += 1
        self.e.append((n, r))
        print(f"  [FAIL] {n}: {r[:150]}")
    def summary(self):
        t = self.p + self.f
        print(f"\n{'='*60}")
        print(f"Result: {self.p}/{t} passed, {self.f} failed")
        if self.e:
            print("\nFailed:")
            for n, r in self.e:
                print(f"  - {n}: {r[:150]}")
        print(f"{'='*60}")


async def setup_db():
    async with engine.begin() as c:
        await c.run_sync(Base.metadata.create_all)

async def teardown_db():
    async with engine.begin() as c:
        await c.run_sync(Base.metadata.drop_all)


async def send_msg(dp, text, r, name, user=None):
    msg = mm(text, user=user)
    u = Update(update_id=1, message=msg)
    try:
        bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        await dp.feed_update(bot, u)
        r.ok(name)
        return True
    except Exception as e:
        r.fail(name, str(e))
        return False


async def send_cb(dp, data, r, name, user=None):
    cb = mc(data, user=user)
    u = Update(update_id=1, callback_query=cb)
    try:
        bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        await dp.feed_update(bot, u)
        r.ok(name)
        return True
    except Exception as e:
        r.fail(name, str(e))
        return False


async def run_tests():
    r = R()
    print("\n[1/3] Setting up DB...")
    await setup_db()

    print("[2/3] Creating dispatcher...")
    dp = setup_dispatcher()
    admin = mu(ADMIN_UID)

    # ─── 1. START & WELCOME ───
    print("\n--- 1. Start & Welcome ---")
    await send_msg(dp, "/start", r, "/start")
    await send_msg(dp, "/start 123", r, "/start_referral")
    await send_cb(dp, "control_panel", r, "control_panel")
    await send_cb(dp, "main_menu", r, "main_menu")

    # ─── 2. BOT LIST ───
    print("\n--- 2. Bot List ---")
    await send_cb(dp, "control_panel", r, "bot_list_empty")
    await send_cb(dp, "bots_page_0", r, "bots_page_0")

    # ─── 3. ADD BOT - SOURCE ───
    print("\n--- 3. Add Bot: Source ---")
    await send_cb(dp, "add_bot", r, "add_bot")
    await send_cb(dp, "create_source_zip", r, "source_zip")
    await send_cb(dp, "create_source_github", r, "source_github")
    await send_cb(dp, "create_back", r, "create_back_1")

    # ─── 4. ADD BOT - PYTHON VERSION ───
    print("\n--- 4. Add Bot: Python Version ---")
    await send_cb(dp, "create_python_3.10", r, "python_310")
    await send_cb(dp, "create_python_3.11", r, "python_311")
    await send_cb(dp, "create_python_3.12", r, "python_312")

    # ─── 5. ADD BOT - ENTRY POINT ───
    print("\n--- 5. Add Bot: Entry Point ---")
    await send_cb(dp, "create_entry_script", r, "entry_script")
    await send_cb(dp, "create_entry_module", r, "entry_module")
    await send_cb(dp, "create_entry_manual", r, "entry_manual")
    await send_cb(dp, "create_entry_file_main.py", r, "entry_file_main")
    await send_cb(dp, "create_confirm", r, "create_confirm")

    # ─── 6. SUBSCRIPTION ───
    print("\n--- 6. Subscription ---")
    await send_cb(dp, "subscription", r, "subscription")
    await send_cb(dp, "subscription_info", r, "subscription_info")
    await send_cb(dp, "subscription_buy", r, "subscription_buy")
    await send_cb(dp, "buy_1_week", r, "buy_1w")
    await send_cb(dp, "buy_1_month", r, "buy_1m")
    await send_cb(dp, "buy_3_months", r, "buy_3m")
    await send_cb(dp, "buy_6_months", r, "buy_6m")
    await send_cb(dp, "buy_12_months", r, "buy_12m")
    await send_cb(dp, "subscription", r, "subscription_back")

    # ─── 7. BACKUPS ───
    print("\n--- 7. Backups ---")
    await send_cb(dp, "backups_list", r, "backups_list")
    await send_cb(dp, "backups_bot_1", r, "backups_bot_1")
    await send_cb(dp, "backup_create_1", r, "backup_create_1")
    await send_cb(dp, "backup_view_1_1", r, "backup_view")

    # ─── 8. BOT MANAGEMENT (need a bot first) ───
    print("\n--- 8. Bot Management ---")
    await send_cb(dp, "bot_view_1", r, "bot_view_1")
    await send_cb(dp, "bot_start_1", r, "bot_start_1")
    await send_cb(dp, "bot_stop_1", r, "bot_stop_1")
    await send_cb(dp, "bot_logs_1", r, "bot_logs_1")
    await send_cb(dp, "logs_file_1", r, "logs_file_1")
    await send_cb(dp, "bot_settings_1", r, "bot_settings_1")

    # ─── 9. BOT SETTINGS ───
    print("\n--- 9. Bot Settings ---")
    await send_cb(dp, "bot_python_1", r, "bot_python_1")
    await send_cb(dp, "set_python_1_3.10", r, "set_python_310")
    await send_cb(dp, "set_python_1_3.12", r, "set_python_312")
    await send_cb(dp, "bot_entry_1", r, "bot_entry_1")
    await send_cb(dp, "set_entry_1_script", r, "set_entry_script")
    await send_cb(dp, "set_entry_1_module", r, "set_entry_module")
    await send_cb(dp, "bot_rename_1", r, "bot_rename_1")
    await send_cb(dp, "bot_files_1", r, "bot_files_1")
    await send_cb(dp, "bot_libs_1", r, "bot_libs_1")
    await send_cb(dp, "lib_add_1", r, "lib_add_1")

    # ─── 10. BOT DELETE ───
    print("\n--- 10. Bot Delete ---")
    await send_cb(dp, "bot_delete_1", r, "bot_delete_1")
    await send_cb(dp, "bot_del_confirm_1", r, "bot_del_confirm_1")

    # ─── 11. ADMIN PANEL ───
    print("\n--- 11. Admin Panel ---")
    await send_msg(dp, "/admin", r, "/admin", user=admin)
    await send_cb(dp, "admin_panel", r, "admin_panel", user=admin)

    # ─── 12. ADMIN USERS ───
    print("\n--- 12. Admin Users ---")
    await send_cb(dp, "admin_users", r, "admin_users", user=admin)
    await send_cb(dp, "admin_users_page_0", r, "admin_users_page", user=admin)
    await send_cb(dp, "admin_user_view_1", r, "admin_user_view", user=admin)
    await send_cb(dp, "admin_user_ban_1", r, "admin_user_ban", user=admin)
    await send_cb(dp, "admin_user_unban_1", r, "admin_user_unban", user=admin)
    await send_cb(dp, "admin_user_tariff_1", r, "admin_user_tariff", user=admin)
    await send_cb(dp, "admin_set_tariff_1_premium", r, "admin_set_tariff", user=admin)
    await send_cb(dp, "admin_user_balance_1", r, "admin_user_balance", user=admin)

    # ─── 13. ADMIN SERVERS ───
    print("\n--- 13. Admin Servers ---")
    await send_cb(dp, "admin_locations", r, "admin_locations", user=admin)
    await send_cb(dp, "admin_servers", r, "admin_servers", user=admin)
    await send_cb(dp, "admin_server_add", r, "admin_server_add", user=admin)
    await send_cb(dp, "admin_server_view_1", r, "admin_server_view", user=admin)
    await send_cb(dp, "admin_sdel_1", r, "admin_server_del", user=admin)
    await send_cb(dp, "admin_sdelyes_1", r, "admin_server_del_yes", user=admin)

    # ─── 14. ADMIN STATS ───
    print("\n--- 14. Admin Stats ---")
    await send_cb(dp, "admin_stats", r, "admin_stats", user=admin)

    # ─── 15. ADMIN PROMOS ───
    print("\n--- 15. Admin Promos ---")
    await send_cb(dp, "admin_promos", r, "admin_promos", user=admin)
    await send_cb(dp, "admin_promo_create", r, "admin_promo_create", user=admin)

    # ─── 16. ADMIN SUBSCRIPTIONS ───
    print("\n--- 16. Admin Subscriptions ---")
    await send_cb(dp, "admin_subscriptions", r, "admin_subscriptions", user=admin)

    # ─── 17. ADMIN REFERRALS ───
    print("\n--- 17. Admin Referrals ---")
    await send_cb(dp, "admin_referrals", r, "admin_referrals", user=admin)

    # ─── 18. ADMIN BROADCAST ───
    print("\n--- 18. Admin Broadcast ---")
    await send_cb(dp, "admin_broadcast", r, "admin_broadcast", user=admin)

    # ─── 19. ADMIN SETTINGS ───
    print("\n--- 19. Admin Settings ---")
    await send_cb(dp, "admin_settings", r, "admin_settings", user=admin)
    await send_cb(dp, "admin_sleep_0", r, "admin_sleep_0", user=admin)
    await send_cb(dp, "admin_sleep_30", r, "admin_sleep_30", user=admin)
    await send_cb(dp, "admin_sleep_60", r, "admin_sleep_60", user=admin)
    await send_cb(dp, "admin_sleep_360", r, "admin_sleep_360", user=admin)
    await send_cb(dp, "admin_sleep_1440", r, "admin_sleep_1440", user=admin)

    # ─── 20. ADMIN PHOTOS ───
    print("\n--- 20. Admin Photos ---")
    await send_cb(dp, "admin_photos", r, "admin_photos", user=admin)
    await send_cb(dp, "admin_photo_set_welcome", r, "admin_photo_welcome", user=admin)
    await send_cb(dp, "admin_photo_set_control_panel", r, "admin_photo_cp", user=admin)

    # ─── 21. EDGE CASES ───
    print("\n--- 21. Edge Cases ---")
    await send_msg(dp, "/unknown", r, "unknown_cmd")
    await send_msg(dp, "/start", r, "/start_2")
    await send_msg(dp, "hello", r, "plain_text")
    await send_cb(dp, "nonexistent_callback", r, "unknown_cb")

    # ─── 22. IMPORTS CHECK ───
    print("\n--- 22. Import Checks ---")
    try:
        from bot.handlers.user.start import router as r1
        from bot.handlers.user.bot_create import router as r2
        from bot.handlers.user.bot_manage import router as r3
        from bot.handlers.user.subscription import router as r4
        from bot.handlers.user.backups import router as r5
        from bot.handlers.admin.panel import router as r6
        from bot.handlers.admin.photos import router as r7
        r.ok("all_routers_import")
    except Exception as e:
        r.fail("all_routers_import", str(e))

    try:
        from bot.config_photos import load_photos, save_photos, get_photo, set_photo, PHOTO_LABELS
        r.ok("photo_config_import")
    except Exception as e:
        r.fail("photo_config_import", str(e))

    try:
        from bot.utils.media import send_photo_or_text, edit_photo_or_text
        r.ok("media_util_import")
    except Exception as e:
        r.fail("media_util_import", str(e))

    try:
        from models.subscription import Subscription, FREE_FEATURES, PREMIUM_FEATURES, PREMIUM_PRICES
        r.ok("subscription_model_import")
    except Exception as e:
        r.fail("subscription_model_import", str(e))

    try:
        from bot.keyboards.user import (
            get_bot_list_keyboard, get_bot_control_keyboard, get_bot_settings_keyboard,
            get_logs_keyboard, get_subscription_keyboard, get_buy_subscription_keyboard,
            get_source_keyboard, get_python_version_keyboard, get_entry_mode_keyboard,
            get_server_select_keyboard, get_backups_list_keyboard, get_backups_keyboard,
            get_libs_keyboard, get_file_manager_keyboard, get_python_change_keyboard,
            get_entry_change_keyboard, get_delete_confirm_keyboard,
        )
        r.ok("all_keyboards_import")
    except Exception as e:
        r.fail("all_keyboards_import", str(e))

    try:
        from services.project import ProjectService
        from services.user import UserService
        from services.backup import BackupService
        from services.monitoring import MonitoringService
        from services.scheduler import SchedulerService
        from services.auto_sleep import AutoSleepService
        from services.rating import RatingService
        from services.notifications import NotificationService
        from services.referral import ReferralService
        from services.promo import PromoService
        from services.github import GitHubService
        r.ok("all_services_import")
    except Exception as e:
        r.fail("all_services_import", str(e))

    try:
        from repositories.user import UserRepository, UserSettingsRepository
        from repositories.project import ProjectRepository, ProjectVersionRepository, ProjectStatsRepository
        from repositories.server import ServerRepository
        from repositories.backup import BackupRepository
        from repositories.promo import PromoRepository
        from repositories.referral import ReferralRepository
        from repositories.coowner import CoOwnerRepository
        r.ok("all_repositories_import")
    except Exception as e:
        r.fail("all_repositories_import", str(e))

    # ─── 23. MODEL CHECKS ───
    print("\n--- 23. Model Checks ---")
    try:
        from models.user import User, UserSettings
        from models.project import Project, ProjectVersion, ProjectStats
        from models.server import Server
        from models.backup import Backup
        from models.promo import PromoCode
        from models.referral import Referral
        from models.coowner import CoOwner
        from models.log import ProjectLog
        from models.subscription import Subscription
        tables = Base.metadata.tables.keys()
        expected = [
            "users", "user_settings", "projects", "project_versions",
            "project_stats", "servers", "backups", "promo_codes",
            "referrals", "coowners", "project_logs", "subscriptions",
        ]
        for t in expected:
            if t in tables:
                r.ok(f"table_{t}")
            else:
                r.fail(f"table_{t}", f"Table {t} not found")
    except Exception as e:
        r.fail("model_checks", str(e))

    # ─── 24. KEYBOARD GENERATION ───
    print("\n--- 24. Keyboard Generation ---")
    try:
        from bot.keyboards.user import get_bot_list_keyboard, get_bot_control_keyboard
        kb1 = get_bot_list_keyboard([])
        assert kb1 is not None
        kb2 = get_bot_control_keyboard(1, "running")
        assert kb2 is not None
        kb3 = get_bot_control_keyboard(1, "stopped")
        assert kb3 is not None
        r.ok("keyboard_generation")
    except Exception as e:
        r.fail("keyboard_generation", str(e))

    # ─── 25. PHOTO CONFIG ───
    print("\n--- 25. Photo Config ---")
    try:
        from bot.config_photos import load_photos, save_photos, get_photo, set_photo
        photos = load_photos()
        assert isinstance(photos, dict)
        assert "welcome" in photos
        set_photo("welcome", "test_file_id")
        assert get_photo("welcome") == "test_file_id"
        set_photo("welcome", None)
        assert get_photo("welcome") is None
        r.ok("photo_config_ops")
    except Exception as e:
        r.fail("photo_config_ops", str(e))

    await teardown_db()
    AiohttpSession.make_request = _original_make_request
    r.summary()
    return r.f == 0

if __name__ == "__main__":
    ok = asyncio.run(run_tests())
    sys.exit(0 if ok else 1)
