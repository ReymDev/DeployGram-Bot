"""
Автоматические тесты DeployGram бота.
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
        self.p = self.f = 0; self.e = []
    def ok(self, n):
        self.p += 1; print(f"  [OK] {n}")
    def fail(self, n, r):
        self.f += 1; self.e.append((n,r)); print(f"  [FAIL] {n}: {r[:120]}")
    def summary(self):
        t = self.p + self.f
        print(f"\n{'='*50}\nResult: {self.p}/{t} passed")
        if self.e:
            print("Failed:")
            for n,r in self.e: print(f"  - {n}: {r[:120]}")
        print(f"{'='*50}")


async def setup_db():
    async with engine.begin() as c: await c.run_sync(Base.metadata.create_all)

async def teardown_db():
    async with engine.begin() as c: await c.run_sync(Base.metadata.drop_all)


async def send_msg(dp, text, r, name, user=None):
    msg = mm(text, user=user)
    u = Update(update_id=1, message=msg)
    try:
        bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        await dp.feed_update(bot, u)
        r.ok(name); return True
    except Exception as e:
        r.fail(name, str(e)); return False


async def send_cb(dp, data, r, name, user=None):
    cb = mc(data, user=user)
    u = Update(update_id=1, callback_query=cb)
    try:
        bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        await dp.feed_update(bot, u)
        r.ok(name); return True
    except Exception as e:
        r.fail(name, str(e)); return False


async def run_tests():
    r = R()
    print("\n[1/2] Setting up DB...")
    await setup_db()
    print("[2/2] Starting bot...")
    dp = setup_dispatcher()
    admin = mu(UID)

    print("\n--- User: /start & Menu ---")
    await send_msg(dp, "/start", r, "/start")
    await send_cb(dp, "my_projects", r, "my_projects")
    await send_cb(dp, "profile", r, "profile")
    await send_cb(dp, "settings", r, "settings")
    await send_cb(dp, "toggle_notify_container_stopped", r, "toggle_notify")
    await send_cb(dp, "main_menu", r, "main_menu")

    print("\n--- Project Creation ---")
    await send_cb(dp, "create_project", r, "create_project")
    await send_cb(dp, "create_type_zip", r, "create_type_zip")
    await send_cb(dp, "create_type_github", r, "create_type_github")
    await send_cb(dp, "create_python_3.12", r, "python_version")
    await send_cb(dp, "create_entry_script", r, "entry_script")
    await send_cb(dp, "create_entry_module", r, "entry_module")
    await send_cb(dp, "main_menu", r, "back_menu")

    print("\n--- Locations ---")
    await send_cb(dp, "locations", r, "locations")
    print("\n--- Referrals ---")
    await send_cb(dp, "referrals", r, "referrals")
    print("\n--- Promo ---")
    await send_cb(dp, "promo_activate", r, "promo")
    await send_cb(dp, "main_menu", r, "back_menu_2")

    print("\n--- Admin Panel ---")
    await send_msg(dp, "/admin", r, "/admin", user=admin)
    await send_cb(dp, "admin_users", r, "admin_users", user=admin)
    await send_cb(dp, "admin_stats", r, "admin_stats", user=admin)
    await send_cb(dp, "admin_promos", r, "admin_promos", user=admin)
    await send_cb(dp, "admin_settings", r, "admin_settings", user=admin)
    await send_cb(dp, "admin_locations", r, "admin_locations", user=admin)
    await send_cb(dp, "admin_panel", r, "admin_panel", user=admin)
    await send_cb(dp, "admin_broadcast", r, "admin_broadcast", user=admin)
    await send_cb(dp, "admin_servers", r, "admin_servers", user=admin)
    await send_cb(dp, "admin_referrals", r, "admin_referrals", user=admin)
    await send_cb(dp, "admin_sleep_30", r, "admin_sleep_30", user=admin)
    await send_cb(dp, "admin_sleep_0", r, "admin_sleep_0", user=admin)

    print("\n--- Edge Cases ---")
    await send_msg(dp, "/unknown", r, "unknown_cmd")
    await send_msg(dp, "/start", r, "/start_2")

    await teardown_db()
    AiohttpSession.make_request = _original_make_request
    r.summary()
    return r.f == 0

if __name__ == "__main__":
    ok = asyncio.run(run_tests())
    sys.exit(0 if ok else 1)
