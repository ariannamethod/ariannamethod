#!/usr/bin/env python3
"""Interactive console terminal for Arianna Core."""

from __future__ import annotations

import os
import socket
import sys
import readline
import atexit
import asyncio
try:
    import importlib.metadata as importlib_metadata
except ImportError:
    # Python 3.7 совместимость
    import importlib_metadata
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import (
    Awaitable,
    Callable,
    Deque,
    Dict,
    Iterable,
    List,
    Tuple,
    Union,
    Optional,
)
from dataclasses import dataclass, asdict
import re
import shutil
from textwrap import dedent

_NO_COLOR_FLAG = "--no-color"
USE_COLOR = (
    os.getenv("LETSGO_NO_COLOR") is None
    and os.getenv("NO_COLOR") is None
    and _NO_COLOR_FLAG not in sys.argv
)
if _NO_COLOR_FLAG in sys.argv:
    sys.argv.remove(_NO_COLOR_FLAG)

os.environ.setdefault("TERM", "xterm")


APP_NAME = "LetsGo"
try:
    APP_VERSION = importlib_metadata.version("letsgo")
except importlib_metadata.PackageNotFoundError:
    APP_VERSION = None


# Configuration
DATA_DIR = Path.home() / ".letsgo"
CONFIG_PATH = DATA_DIR / "config"


@dataclass
class Settings:
    prompt: str = ">> "
    green: str = "\033[32m"
    red: str = "\033[31m"
    cyan: str = "\033[36m"
    reset: str = "\033[0m"
    max_log_files: int = 100
    command_timeout: int = 10
    use_color: bool = True


def _load_settings(path: Path = CONFIG_PATH) -> Settings:
    settings = Settings()
    try:
        with path.open() as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = map(str.strip, line.split("=", 1))
                value = value.strip("\"'")
                value = bytes(value, "utf-8").decode("unicode_escape")
                if hasattr(settings, key):
                    attr = getattr(settings, key)
                    if isinstance(attr, int):
                        try:
                            value = int(value)
                        except ValueError:
                            continue
                    elif isinstance(attr, bool):
                        value_lower = value.lower()
                        if value_lower in {"1", "true", "yes", "on"}:
                            value = True
                        elif value_lower in {"0", "false", "no", "off"}:
                            value = False
                        else:
                            continue
                    setattr(settings, key, value)
    except FileNotFoundError:
        pass
    return settings


SETTINGS = _load_settings()
USE_COLOR = USE_COLOR and SETTINGS.use_color


def _save_settings(path: Optional[Path] = None) -> None:
    path = path or CONFIG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        for key, value in asdict(SETTINGS).items():
            fh.write(f"{key}={value}\n")


def color(text: str, code: str) -> str:
    return f"{code}{text}{SETTINGS.reset}" if USE_COLOR else text


# //: each session logs to its own file under a fixed directory
LOG_DIR = DATA_DIR / "log"
SESSION_ID = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
LOG_PATH = LOG_DIR / f"{SESSION_ID}.log"
HISTORY_PATH = DATA_DIR / "history"
PY_TIMEOUT = 5

ERROR_LOG_PATH = LOG_DIR / "errors.log"

Handler = Callable[[str], Awaitable[Tuple[str, Optional[str]]]]


def _ensure_log_dir() -> None:
    """Ensure that the log directory exists and is writable."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not os.access(LOG_DIR, os.W_OK):
        print(f"No write permission for {LOG_DIR}", file=sys.stderr)
        raise SystemExit(1)
    max_files = getattr(SETTINGS, "max_log_files", 0)
    if max_files > 0:
        logs = sorted(
            LOG_DIR.glob("*.log"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for old in logs[max_files:]:
            try:
                old.unlink()
            except OSError:
                pass


def log(message: str) -> None:
    with LOG_PATH.open("a") as fh:
        fh.write(f"{datetime.utcnow().isoformat()} {message}\n")


def log_error(message: str) -> None:
    with ERROR_LOG_PATH.open("a") as fh:
        fh.write(f"{datetime.utcnow().isoformat()} {message}\n")


def _first_ip() -> str:
    """Return the first non-loopback IP address or 'unknown'."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        try:
            for addr in socket.gethostbyname_ex(socket.gethostname())[2]:
                if not addr.startswith("127."):
                    return addr
        except socket.gaierror:
            pass
    return "unknown"


def status() -> str:
    """Return basic system metrics."""
    cpu = os.cpu_count()
    uptime = Path("/proc/uptime").read_text().split()[0]
    ip = _first_ip()
    return f"CPU cores: {cpu}\nUptime: {uptime}s\nIP: {ip}"


def cpu_load() -> str:
    """Return CPU load averages."""
    load1, load5, load15 = os.getloadavg()
    return f"Load average (1m,5m,15m): {load1:.2f}, {load5:.2f}, {load15:.2f}"


def disk_usage_info() -> str:
    """Return disk usage statistics for the root filesystem."""
    total, used, free = shutil.disk_usage("/")
    to_gib = 1024**3
    return (
        f"Disk /: total {total // to_gib} GiB, "
        f"used {used // to_gib} GiB, free {free // to_gib} GiB"
    )


def _default_gateway() -> str:
    try:
        with open("/proc/net/route") as fh:
            for line in fh.readlines()[1:]:
                fields = line.strip().split()
                if fields[1] != "00000000" or not int(fields[3], 16) & 2:
                    continue
                return socket.inet_ntoa(bytes.fromhex(fields[2])[::-1])
    except OSError:
        pass
    return "unknown"


def network_info() -> str:
    """Return basic network parameters."""
    ip = _first_ip()
    gateway = _default_gateway()
    return f"IP: {ip}\nGateway: {gateway}"


def current_time() -> str:
    """Return the current UTC time."""
    return datetime.utcnow().isoformat()


async def async_input(prompt: str) -> str:
    """Async wrapper around ``input``."""
    import concurrent.futures
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, input, prompt)


async def run_command(
    command: str,
    on_line: Optional[Callable[[str], None]] = None,
    timeout: int = SETTINGS.command_timeout,
) -> Tuple[str, int, float]:
    """Execute ``command`` and return its output, exit code and duration."""

    loop = asyncio.get_running_loop()
    start = loop.time()
    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        output_lines: List[str] = []
        while True:
            remaining = timeout - (loop.time() - start)
            if remaining <= 0:
                proc.kill()
                await proc.communicate()
                duration = loop.time() - start
                return "command timed out", 124, duration
            try:
                line = await asyncio.wait_for(
                    proc.stdout.readline(),
                    timeout=remaining,
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.communicate()
                duration = loop.time() - start
                return "command timed out", 124, duration
            if not line:
                break
            decoded = line.decode().rstrip()
            output_lines.append(decoded)
            if on_line:
                on_line(decoded)
        rc = await proc.wait()
        duration = loop.time() - start
        output = "\n".join(output_lines).strip()
        return output, rc, duration
    except Exception as exc:
        duration = loop.time() - start
        return str(exc), 1, duration


def _format_python(code: str) -> str:
    """Return ``code`` formatted according to Python conventions."""
    formatted = dedent(code).strip()
    try:
        import black

        formatted = black.format_str(formatted, mode=black.FileMode())
    except Exception:
        pass
    return formatted


def _looks_like_python(text: str) -> bool:
    """Heuristically determine if ``text`` is Python code."""
    if "\n" in text:
        return True
    keywords = {
        "import",
        "def",
        "class",
        "for",
        "while",
        "if",
        "else",
        "elif",
        "try",
        "except",
        "with",
        "return",
        "print",
    }
    tokens = set(re.findall(r"\b\w+\b", text))
    return bool(tokens & keywords)


async def run_python(code: str) -> Tuple[str, str | None]:
    """Format and execute Python ``code``."""
    code = _format_python(code)
    if not code:
        reply = "Usage: /py <code>"
        return reply, reply
    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable,
            "-I",
            "-c",
            code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=PY_TIMEOUT)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        reply = "execution timed out"
        return reply, color(reply, SETTINGS.red)
    output = stdout.decode().strip()
    err = stderr.decode().strip()
    if proc.returncode != 0:
        reply = err or "error"
        return reply, color(reply, SETTINGS.red)
    reply = output
    return reply, reply


async def run_shell(command: str) -> Tuple[str, str | None]:
    """Execute a shell ``command`` and return its output."""
    # Executing command silently
    output, rc, duration = await run_command(command)
    if output:
        if rc != 0:
            print(color(output, SETTINGS.red))
        else:
            print(output)
    status = f"exit code: {rc}, duration: {duration:.2f}s"
    if rc != 0:
        print(color(status, SETTINGS.red))
        log_error(f"{command} | {status} | {output}")
    else:
        print(color(status, SETTINGS.green))
    reply = "\n".join(filter(None, [output, status]))
    return reply, None


def clear_screen() -> str:
    """Return the control sequence that clears the terminal."""
    return "\033c"


def history(limit: int = 20) -> str:
    """Return the last ``limit`` commands from ``HISTORY_PATH``."""
    try:
        with HISTORY_PATH.open() as fh:
            lines = [line.rstrip("\n") for line in fh]
    except FileNotFoundError:
        return "no history"
    return "\n".join(lines[-limit:])


def show_history() -> str:
    """Return the entire command history."""
    try:
        with HISTORY_PATH.open() as fh:
            return fh.read()
    except FileNotFoundError:
        return "no history"


def _iter_log_lines() -> Iterable[str]:
    """Yield log lines from all log files in order."""
    for file in sorted(LOG_DIR.glob("*.log")):
        with file.open() as fh:
            for line in fh:
                yield line.rstrip("\n")


def summarize(
    term: str | None = None,
    limit: int = 5,
    history: bool = False,
) -> str:
    """Return the last ``limit`` lines matching ``term``.

    If ``history`` is True, search command history instead of log files.
    ``term`` is treated as a regular expression.
    """
    if history:
        try:
            with HISTORY_PATH.open() as fh:
                iterable = (line.rstrip("\n") for line in fh)
                lines = list(iterable)
        except FileNotFoundError:
            return "no history"
    else:
        if not LOG_DIR.exists():
            return "no logs"
        lines = list(_iter_log_lines())
    try:
        pattern = re.compile(term) if term else None
    except re.error:
        return "invalid pattern"
    matches: Deque[str] = deque(maxlen=limit)
    for line in lines:
        if pattern is None or pattern.search(line):
            matches.append(line)
    return "\n".join(matches) if matches else "no matches"


def search_history(pattern: str) -> str:
    """Return all history lines matching ``pattern`` as regex."""
    try:
        with HISTORY_PATH.open() as fh:
            lines = [line.rstrip("\n") for line in fh]
    except FileNotFoundError:
        return "no history"
    try:
        regex = re.compile(pattern)
    except re.error:
        return "invalid pattern"
    matches = [line for line in lines if regex.search(line)]
    return "\n".join(matches) if matches else "no matches"


async def handle_status(_: str) -> Tuple[str, Optional[str]]:
    reply = status()
    return reply, color(reply, SETTINGS.green)


async def handle_cpu(_: str) -> Tuple[str, Optional[str]]:
    reply = cpu_load()
    return reply, color(reply, SETTINGS.green)


async def handle_disk(_: str) -> Tuple[str, Optional[str]]:
    reply = disk_usage_info()
    return reply, color(reply, SETTINGS.green)


async def handle_net(_: str) -> Tuple[str, Optional[str]]:
    reply = network_info()
    return reply, color(reply, SETTINGS.green)


async def handle_time(_: str) -> Tuple[str, Optional[str]]:
    reply = current_time()
    return reply, reply


async def handle_run(user: str) -> Tuple[str, Optional[str]]:
    command = user.partition(" ")[2]
    return await run_shell(command)


async def handle_py(user: str) -> Tuple[str, Optional[str]]:
    code = user.partition(" ")[2]
    return await run_python(code)


async def handle_clear(_: str) -> Tuple[str, Optional[str]]:
    print(clear_screen(), end="")
    reply = "Cleared."
    return reply, reply


async def handle_history(user: str) -> Tuple[str, Optional[str]]:
    parts = user.split()
    if len(parts) > 1 and parts[1].isdigit():
        reply = history(int(parts[1]))
    else:
        reply = show_history()
    return reply, reply


async def handle_help(user: str) -> Tuple[str, Optional[str]]:
    parts = user.split(maxsplit=1)

    lines = [f"{cmd} - {desc}" for cmd, (_, desc) in sorted(COMMAND_MAP.items())]
    reply = "\n".join(lines)

    if len(parts) > 1:
        cmd = parts[1]
        help_text = COMMAND_HELP.get(cmd)
        if help_text:
            reply = f"{reply}\n\n{help_text}"
        else:
            reply = f"{reply}\n\nNo help available for {cmd}"

    return reply, reply


async def handle_summarize(user: str) -> Tuple[str, Optional[str]]:
    parts = user.split()[1:]
    history_mode = False
    if "--history" in parts:
        parts.remove("--history")
        history_mode = True
    limit = 5
    if parts and parts[-1].isdigit():
        limit = int(parts[-1])
        parts = parts[:-1]
    term = " ".join(parts) if parts else None
    reply = summarize(term, limit, history=history_mode)
    return reply, reply


async def handle_search(user: str) -> Tuple[str, Optional[str]]:
    pattern = user.partition(" ")[2]
    reply = search_history(pattern)
    return reply, reply


async def handle_ping(_: str) -> Tuple[str, Optional[str]]:
    reply = "pong"
    return reply, reply


CORE_COMMANDS: Dict[str, Tuple[Handler, str]] = {
    "/status": (handle_status, "show system metrics"),
    "/cpu": (handle_cpu, "show CPU load"),
    "/disk": (handle_disk, "disk usage"),
    "/net": (handle_net, "network parameters"),
    "/time": (handle_time, "curent UTC time"),
    "/run": (handle_run, "shell command"),
    "/py": (handle_py, "execute Python code"),
    "/summarize": (handle_summarize, "log entries"),
    "/clear": (handle_clear, "clear the terminal"),
    "/history": (handle_history, "command history"),
    "/help": (handle_help, "help message"),
    "/search": (handle_search, "search command history"),
    "/ping": (handle_ping, "reply with pong"),
}

COMMAND_HELP: Dict[str, str] = {
    "/status": "Usage: /status\nShow system metrics.",
    "/cpu": "Usage: /cpu\nShow CPU load averages.",
    "/disk": "Usage: /disk\nShow disk usage information.",
    "/net": "Usage: /net\nShow network parameters.",
    "/time": "Usage: /time\nDisplay the current UTC time.",
    "/run": "Usage: /run <command>\nRun a shell command and return its output.",
    "/py": "Usage: /py <code>\nExecute Python code and print the result.",
    "/summarize": (
        "Usage: /summarize [--history] [limit]"
        "\nSummarize recent log entries or command history."
    ),
    "/clear": "Usage: /clear\nClear the terminal.",
    "/history": "Usage: /history [n]\nShow the last n commands.",
    "/help": "Usage: /help [command]\nList commands or show detailed help.",
    "/search": "Usage: /search <pattern>\nSearch the command history.",
    "/ping": "Usage: /ping\nReply with pong.",
}

COMMAND_HANDLERS: Dict[str, Handler] = {
    cmd: func for cmd, (func, _) in CORE_COMMANDS.items()
}
COMMANDS: List[str] = list(COMMAND_HANDLERS.keys())
COMMAND_MAP: Dict[str, Tuple[Handler, str]] = dict(CORE_COMMANDS)


def register_core(commands: List[str], handlers: Dict[str, Handler]) -> None:
    commands.extend(CORE_COMMANDS.keys())
    handlers.update(COMMAND_HANDLERS)
    COMMAND_MAP.update(CORE_COMMANDS)


async def main() -> None:
    _ensure_log_dir()
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        readline.read_history_file(str(HISTORY_PATH))
    except (FileNotFoundError, PermissionError):
        # Игнорируем ошибки доступа к history файлу
        pass

    command_summary = " ".join(sorted(COMMAND_HANDLERS))

    readline.parse_and_bind("tab: complete")
    readline.parse_and_bind(r'"\e[A": history-search-backward')
    readline.parse_and_bind(r'"\e[B": history-search-forward')
    readline.parse_and_bind(r'"\C-r": reverse-search-history')

    def completer(text: str, state: int) -> Optional[str]:
        buffer = readline.get_line_buffer()
        if buffer.startswith("/run "):
            path = Path(text)
            directory = path.parent if path.parent != Path(".") else Path(".")
            try:
                entries = os.listdir(directory)
            except OSError:
                matches: List[str] = []
            else:
                matches = [
                    str(directory / entry) if directory != Path(".") else entry
                    for entry in entries
                    if entry.startswith(path.name)
                ]
        else:
            matches = [cmd for cmd in COMMAND_HANDLERS if cmd.startswith(text)]
        return matches[state] if state < len(matches) else None

    readline.set_completer(completer)
    atexit.register(readline.write_history_file, str(HISTORY_PATH))
    atexit.register(_save_settings)

    log("session_start")
    version = f" v{APP_VERSION}" if APP_VERSION else ""
    header = f"{APP_NAME}{version}"
    print(color(header, SETTINGS.green))
    print(color("Commands:", SETTINGS.cyan), command_summary)
    print("Type 'exit' to quit.")
    while True:
        try:
            user = await async_input(color(SETTINGS.prompt, SETTINGS.cyan))
        except EOFError:
            break
        if user.strip().lower() in {"exit", "quit"}:
            break
        log(f"user:{user}")
        base = user.split()[0]
        handler = COMMAND_HANDLERS.get(base)
        if handler:
            reply, colored = await handler(user)
        else:
            if _looks_like_python(user):
                reply, colored = await run_python(user)
            else:
                reply, colored = await run_shell(user)
        if colored is not None:
            print(colored)
        log(f"letsgo:{reply}")
    log("session_end")


if __name__ == "__main__":
    asyncio.run(main())
