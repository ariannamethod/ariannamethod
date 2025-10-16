import importlib.util
import sys
from pathlib import Path
import asyncio

from telegram import InlineKeyboardMarkup

BASE = Path(__file__).resolve().parent.parent


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, BASE / file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_load("tripd_pkg.tripd_memory", "tripd_memory.py")
_load("tripd_pkg.tripd_expansion", "tripd_expansion.py")
_load("tripd_pkg.tripd", "tripd.py")
tg = _load("tripd_pkg.tripd_tg", "tripd_tg.py")
_show_menu = tg._show_menu


class DummyMessage:
    def __init__(self):
        self.replies = []

    async def reply_text(self, text: str, **kwargs):
        self.replies.append((text, kwargs))


class DummyCallbackQuery:
    def __init__(self):
        self.answered = False
        self.edits = []

    async def answer(self):
        self.answered = True

    async def edit_message_text(self, text: str, **kwargs):
        self.edits.append((text, kwargs))


class DummyUpdateCommand:
    def __init__(self):
        self.message = DummyMessage()
        self.callback_query = None


class DummyUpdateCallback:
    def __init__(self):
        self.message = None
        self.callback_query = DummyCallbackQuery()


class DummyContext:
    pass


def test_show_menu_command():
    update = DummyUpdateCommand()
    asyncio.run(_show_menu(update, DummyContext()))
    assert update.message.replies
    text, kwargs = update.message.replies[0]
    assert text == "True Recursive Intelligent Python Dialect"
    markup = kwargs.get("reply_markup")
    assert isinstance(markup, InlineKeyboardMarkup)
    assert markup.inline_keyboard


def test_show_menu_callback():
    update = DummyUpdateCallback()
    asyncio.run(_show_menu(update, DummyContext()))
    assert update.callback_query.answered
    assert update.callback_query.edits
    text, kwargs = update.callback_query.edits[0]
    assert text == "True Recursive Intelligent Python Dialect"
    markup = kwargs.get("reply_markup")
    assert isinstance(markup, InlineKeyboardMarkup)
    assert markup.inline_keyboard
