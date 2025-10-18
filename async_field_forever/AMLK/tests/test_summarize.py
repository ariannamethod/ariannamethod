import sys
from pathlib import Path

from tests.utils import _write_log

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import letsgo  # noqa: E402


def test_summarize_large_log(tmp_path, monkeypatch):
    log_dir = tmp_path / "log"
    log_dir.mkdir()
    # create large log file with many matching lines
    lines = [f"{i} match" for i in range(10000)]
    _write_log(log_dir, "big", lines)
    monkeypatch.setattr(letsgo, "LOG_DIR", log_dir)
    result = letsgo.summarize("match")
    expected = "\n".join(lines[-5:])
    assert result == expected
