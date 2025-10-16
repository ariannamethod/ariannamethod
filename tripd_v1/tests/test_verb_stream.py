import importlib.util
import socket
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

memory = _load("tripd_pkg.tripd_memory", "tripd_memory.py")
expansion = _load("tripd_pkg.tripd_expansion", "tripd_expansion.py")
tripd = _load("tripd_pkg.tripd", "tripd.py")
# verb_stream functionality is now part of tripd.py
TripDModel = tripd.TripDModel
start_verb_stream = tripd.start_verb_stream


def test_unix_socket_stream(tmp_path):
    model = TripDModel()
    sock = tmp_path / "verbs.sock"
    start_verb_stream(model, unix_socket=str(sock))
    time.sleep(0.1)
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.connect(str(sock))
        client.sendall(b"test_verb()\n")
    time.sleep(0.1)
    assert "test_verb()" in model.extra_verbs
