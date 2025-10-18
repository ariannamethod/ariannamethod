#!/usr/bin/env python3
"""Launch letsgo on login."""
import subprocess
from pathlib import Path

LETSGO = Path(__file__).resolve().parent.parent / "letsgo.py"


def main() -> None:
    subprocess.run(["python3", str(LETSGO)])


if __name__ == "__main__":
    main()
