import importlib.util
import sys
from pathlib import Path
import asyncio
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
# verb_stream functionality is now part of tripd.py
tg = _load("tripd_pkg.tripd_tg", "tripd_tg.py")
_handle_message = tg._handle_message


class DummyMessage:
    def __init__(self, text: str) -> None:
        self.text = text
        self.replies = []

    async def reply_text(self, text: str, **kwargs) -> None:
        self.replies.append(text)


class DummyUpdate:
    def __init__(self, text: str) -> None:
        self.message = DummyMessage(text)


class DummyContext:
    pass


def test_script_and_metrics_returned():
    update = DummyUpdate("abc")
    context = DummyContext()
    asyncio.run(_handle_message(update, context))
    assert len(update.message.replies) == 2
    assert "def tripd_" in update.message.replies[0]
    assert "entropy" in update.message.replies[1]
    assert "perplexity" in update.message.replies[1]
