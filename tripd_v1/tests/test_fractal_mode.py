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

_load("tripd_pkg.tripd_memory", "tripd_memory.py")
_load("tripd_pkg.tripd_expansion", "tripd_expansion.py")
tripd = _load("tripd_pkg.tripd", "tripd.py")
TripDModel = tripd.TripDModel


def test_selector_differs_between_modes():
    text = "fractal energy"
    deterministic = TripDModel()
    fractal = TripDModel(fractal_metrics=True)
    sel_det = deterministic.metrics(text)["selector"]
    sel_frac = fractal.metrics(text)["selector"]
    assert sel_det != sel_frac


def test_section_differs_between_modes():
    text = "fractal energy"
    deterministic = TripDModel()
    fractal = TripDModel(fractal_metrics=True)
    sec_det = deterministic._choose_section(deterministic.metrics(text))
    sec_frac = fractal._choose_section(fractal.metrics(text))
    assert sec_det != sec_frac
