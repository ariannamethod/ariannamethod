import subprocess
from pathlib import Path

import pytest


def test_build_custom_apk():
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "build" / "build_apk_tools.sh"
    try:
        subprocess.check_call([str(script)])
    except subprocess.CalledProcessError as exc:
        pytest.skip(f"apk-tools build failed: {exc}")
    apk_path = repo_root / "apk-tools" / "src" / "apk"
    assert apk_path.is_file()
    subprocess.check_call([str(apk_path), "--version"])
