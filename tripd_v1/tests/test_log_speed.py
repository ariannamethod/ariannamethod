import importlib.util
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, BASE / file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_log_script_speed(monkeypatch, tmp_path):
    memory = _load("tripd_pkg.tripd_memory", "tripd_memory.py")
    log_path = tmp_path / "scripts.log"
    monkeypatch.setattr(memory, "_LOG_PATH", log_path)
    memory._SCRIPTS_INDEX.clear()
    memory._CACHE_LOADED = False
    memory._load_cache()

    for i in range(5000):
        memory.log_script(f"script_{i}")

    start = time.perf_counter()
    memory.log_script("final_script")
    duration = time.perf_counter() - start

    assert duration < 0.05
