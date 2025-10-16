import importlib.util
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, BASE / file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_log_rotation(monkeypatch, tmp_path):
    memory = _load("tripd_pkg.tripd_memory", "tripd_memory.py")
    log_path = tmp_path / "scripts.log"
    monkeypatch.setattr(memory, "_LOG_PATH", log_path)
    monkeypatch.setattr(memory, "_LOG_MAX_BYTES", 100)
    memory._SCRIPTS_INDEX.clear()
    memory._SCRIPT_LIST.clear()
    memory._CACHE_LOADED = False
    memory._load_cache()

    for i in range(20):
        memory.log_script(f"script_{i}")

    rotated = log_path.with_suffix(log_path.suffix + ".1")
    assert rotated.exists()
    assert log_path.exists()
    assert any("script_19" in line for line in log_path.read_text().splitlines())
