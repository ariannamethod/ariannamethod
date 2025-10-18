from pathlib import Path


def _write_log(log_dir: Path, name: str, lines: list[str]) -> Path:
    path = log_dir / f"{name}.log"
    with path.open("w") as fh:
        for line in lines:
            fh.write(line + "\n")
    return path
