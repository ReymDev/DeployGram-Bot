from aiogram.fsm.state import State, StatesGroup


class ProjectCreateStates(StatesGroup):
    waiting_name = State()
    waiting_source = State()
    waiting_github_url = State()
    waiting_zip = State()
    waiting_python = State()
    waiting_entry = State()
    waiting_entry_module = State()
    waiting_server = State()
    confirming = State()


class BroadcastStates(StatesGroup):
    waiting_for_message = State()


class AdminUserStates(StatesGroup):
    waiting_tariff = State()
    waiting_balance = State()


class AdminServerStates(StatesGroup):
    waiting_name = State()
    waiting_country = State()
    waiting_ip = State()
    waiting_port = State()
    waiting_slots = State()
    waiting_api_key = State()


class AdminPromoStates(StatesGroup):
    waiting_code = State()
    waiting_reward_type = State()
    waiting_reward_value = State()
    waiting_max_activations = State()
    waiting_expiry = State()


class EditorStates(StatesGroup):
    editing = State()
