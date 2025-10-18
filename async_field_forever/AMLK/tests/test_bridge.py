import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import bridge


def test_help_command_shows_start(monkeypatch):
    monkeypatch.setattr(bridge, "COMMAND_MAP", {"/foo": (None, "bar")})
    monkeypatch.setattr(bridge, "build_main_keyboard", lambda: "keyboard")
    reply_text = AsyncMock()
    update = SimpleNamespace(message=SimpleNamespace(reply_text=reply_text))
    context = SimpleNamespace(args=[])
    asyncio.run(bridge.help_command(update, context))
    reply_text.assert_called_once()
    text = reply_text.call_args[0][0]
    assert "Welcome! Available commands:" in text
    assert "/foo - bar" in text
