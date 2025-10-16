"""Utility functions for tracking generated TRIPD scripts.

This module stores each produced script in a JSON lines log file so that
scripts are never repeated. The log also provides a simple count used by
training routines to trigger periodic fine‑tuning once enough examples have
been collected.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import json
from typing import List, Set

_LOG_PATH = Path(__file__).resolve().parent / "scripts.log"
_LOG_MAX_BYTES = 5_000_000  # Rotate at ~5MB to avoid runaway growth.

# In-memory cache of previously seen script hashes and their original text.
# The cache is populated once when the module is imported and then kept in
# sync as new scripts are logged.
_SCRIPTS_INDEX: Set[str] = set()
_SCRIPT_LIST: List[str] = []
_CACHE_LOADED = False


def _hash_script(script: str) -> str:
    """Return a stable hash for *script* used for fast lookups."""
    return hashlib.sha256(script.encode("utf-8")).hexdigest()


def _ensure_log() -> None:
    """Create the log file if it does not yet exist."""
    if not _LOG_PATH.exists():
        _LOG_PATH.touch()


def _rotate_log() -> None:
    """Rotate the log file if it exceeds the configured size limit."""
    if not _LOG_PATH.exists():
        return
    if _LOG_PATH.stat().st_size <= _LOG_MAX_BYTES:
        return
    backup = _LOG_PATH.with_suffix(_LOG_PATH.suffix + ".1")
    if backup.exists():
        backup.unlink()
    _LOG_PATH.rename(backup)
    _LOG_PATH.touch()


def _load_cache() -> None:
    """Populate the in-memory index from disk if not already loaded."""
    global _CACHE_LOADED
    if _CACHE_LOADED:
        return
    _ensure_log()
    with _LOG_PATH.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                script = data.get("script", "")
                _SCRIPT_LIST.append(script)
                _SCRIPTS_INDEX.add(data.get("hash") or _hash_script(script))
            except Exception:
                # Ignore malformed lines while keeping the log readable.
                continue
    _CACHE_LOADED = True


def load_scripts() -> List[str]:
    """Return a list of all previously generated scripts.

    The result is a shallow copy of the in-memory list so callers can mutate
    it without affecting the cache.
    """
    return list(_SCRIPT_LIST)


def log_script(script: str) -> None:
    """Persist *script* if it has not been seen before.

    Membership checks are serviced entirely from the in-memory index so the
    log file is not re-read on each call.
    """
    script_hash = _hash_script(script)
    if script_hash in _SCRIPTS_INDEX:
        return
    _ensure_log()
    _rotate_log()
    with _LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"hash": script_hash, "script": script}) + "\n")
    _SCRIPTS_INDEX.add(script_hash)
    _SCRIPT_LIST.append(script)


def get_log_count() -> int:
    """Return how many unique scripts have been recorded."""
    return len(_SCRIPTS_INDEX)


# Load existing scripts once at import time so that applications start with a
# warm cache and do not repeatedly read the log file.
_load_cache()
