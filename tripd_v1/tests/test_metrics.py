import importlib.util
import math
import sys
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parent.parent


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, BASE / file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

# Load modules under a package name to satisfy relative imports
_load("tripd_pkg.tripd_memory", "tripd_memory.py")
_load("tripd_pkg.tripd_expansion", "tripd_expansion.py")
tripd = _load("tripd_pkg.tripd", "tripd.py")
TripDModel = tripd.TripDModel


def test_public_metrics():
    model = TripDModel()
    metrics = model.metrics("abc")
    assert metrics["entropy"] == pytest.approx(math.log2(3), abs=1e-12)
    assert metrics["perplexity"] == pytest.approx(3.0, abs=1e-12)
    assert metrics["resonance"] == pytest.approx(0.294, abs=1e-12)


def test_resonance_differs_for_texts():
    model = TripDModel()
    r1 = model.metrics("abc")["resonance"]
    r2 = model.metrics("abd")["resonance"]
    assert r1 != r2
