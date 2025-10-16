import importlib.util
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, BASE / file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Load memory first to satisfy expansion's relative import
_load("tripd_pkg.tripd_memory", "tripd_memory.py")
expansion = _load("tripd_pkg.tripd_expansion", "tripd_expansion.py")


def test_training_log_accumulates(monkeypatch, tmp_path):
    log_path = tmp_path / "train.log"
    monkeypatch.setattr(expansion, "_TRAIN_LOG", log_path)

    expansion._train_on_scripts(["a"])
    expansion._train_on_scripts(["b", "c"])

    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2

    t1, c1 = lines[0].split("\t")
    t2, c2 = lines[1].split("\t")
    assert int(c1) == 1
    assert int(c2) == 2
    dt1 = datetime.fromisoformat(t1)
    dt2 = datetime.fromisoformat(t2)
    assert dt2 >= dt1
