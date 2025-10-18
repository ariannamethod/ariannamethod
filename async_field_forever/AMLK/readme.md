# Arianna Method Linux Kernel

**Arianna Method Linux Kernel (AMLK)** is a deliberately compact operating nucleus engineered from Alpine sources to provide a deterministic base for AI workloads.

Those who want to try the new kernel firsthand can visit the Telegram bot **Terminal Robot** at [https://t.me/methodterminalrobot](https://t.me/methodterminalrobot). Additional screenshots and usage examples will appear there later.

The robot provides a minimal terminal connected to the same kernel as AMLK. It can accept commands, return output, and maintain a shared log with other interfaces.

Future development of the robot aims to expand its capabilities: we plan to add monitoring, resource management, and other interaction methods. Beyond Arianna Method OS, the bot serves as a clean minimalist access point to the new Linux kernel.

**Contributors and any form of collaboration are warmly welcomed.**

---

## Key Features

- Loads with a minimal initramfs (based on Alpine minirootfs), reducing boot complexity to O(1) relative to module count.
- **OverlayFS** for layered filesystems, modeled as a union (U = R ∪ W) for efficient state changes.
- **ext4** as the default persistent store; journaling function J(t) ≈ bounded integral, protecting data under power loss.
- **Namespaces** (Nᵢ) for process/resource isolation, safe multitenancy.
- **Cgroup hierarchies** for resource trees (T), precise CPU/RAM control.
- **Python 3.10+** included, `venv` isolation equals “vector subspaces.”
- **Node.js 18+** for async I/O, modeled as f: E → E.
- **Minimal toolkit:** bash, curl, nano—each is a vertex in the dependency graph, no bloat.
- **CLI terminal (`letsgo.py`):** logging, echo, proof-of-concept for higher reasoning modules.
- **Logs:** `/arianna_core/log`, each entry timestamped (tᵢ, mᵢ) as dialogue chronicle.
- **Build:** downloads kernel/rootfs, verifies checksums, sets config predicates for ext4/overlay/isolation.
- **Make -j n:** parallel build, Amdahl’s law for speedup.
- **Initramfs via cpio+gzip:** filesystem as multiset, serialized and compressed.
- **Final image:** bzImage + initramfs for QEMU, headless/network deploy.
- **QEMU:** console=ttyS0, -nographic; system as linear state machine via stdio.
- **Verification:** `python3 --version`, `node --version` inside QEMU.
- **Project tree:** strict lattice (`kernel/`, `core/`, `cmd/`, `usr/bin/`, `log/`).
- **Comments with `//:` motif** for future extensibility (category morphism).

AMLK is lightweight enough to embed within messaging clients like Telegram, allowing AI agents to inhabit user devices with minimal computational overhead.

---

## Environment Variables

The bridge and HTTP server require several variables to be set before starting `bridge.py`:

- `API_TOKEN` – shared secret for API requests and WebSocket connections
- `TELEGRAM_TOKEN` – token used by the Telegram bot
- `PORT` – port for the HTTP server (defaults to `8000`)

---

## Token Setup

- `API_TOKEN` – token for HTTP and WebSocket. Set it before launch via `export API_TOKEN=...`.
- `TELEGRAM_TOKEN` – Telegram bot token required to enable the bot.
- In the web interface open `arianna_terminal.html` and enter the token in the **Token** field; the value is stored in `localStorage`.

**Example run:**

```bash
API_TOKEN=secret TELEGRAM_TOKEN=123 python bridge.py

Hardware Requirements

The kernel and userland target generic x86_64 CPUs. GPU drivers and libraries are omitted, so the system runs entirely on CPU hardware.

⸻

Continuous Integration

The CI pipeline builds the kernel and boots it in QEMU using only CPU resources. GPU devices and drivers are absent, and QEMU is invoked with software acceleration so the workflow succeeds on generic CPU-only runners.

⸻

Building

First build the trimmed package manager:

./build/build_apk_tools.sh

Then assemble the kernel and userland:

./build/build_ariannacore.sh [--with-python] [--clean] [--test-qemu]

The second script fetches kernel sources, stages arianna_core_root built from the Alpine lineage, and emits a flat image. The optional flags expand the userland, clean previous artifacts or run a QEMU smoke test.
Linting

Run static analysis before pushing changes (install flake8, flake8-pyproject, and black if missing):

./run-tests.sh

This script executes flake8 and black –check followed by the test suite. To run the linters directly:

flake8 .
black --check .

Checksum Verification

For reproducibility the build script verifies downloads against known SHA256 sums using:

echo "<sha256>  <file>" | sha256sum -c -

	•	linux-6.6.4.tar.gz: 43d77b1816942ed010ac5ded8deb8360f0ae9cca3642dc7185898dab31d21396
	•	arianna_core_root-3.19.8-x86_64.tar.gz: 48230b61c9e22523413e3b90b2287469da1d335a11856e801495a896fd955922

If a checksum mismatch occurs the build aborts immediately.

⸻

Running in QEMU

Minimal invocation (headless):

qemu-system-x86_64 -kernel build/kernel/linux-*/arch/x86/boot/bzImage -initrd build/arianna.initramfs.gz -append "console=ttyS0" -nographic

Recommended: set memory to 512M, disable reboot so exit status bubbles up to host. Console directed to ttyS0 for easy piping/tmux/logging.

With --test-qemu, the above is executed automatically; artifacts stay under boot/.

⸻

Future Interfaces
	•	Telegram bridge: Proxies chat messages to letsgo.py terminal. Each chat gets a session log; bot authenticates via API token.
	•	Web UI: Terminal via WebSocket. HTTP as transport; SSL/rate limiting via userland libraries atop initramfs.
	•	Other: serial TTYs, named pipes, custom RPC. The terminal only uses stdio, so any frontend can connect.

⸻

letsgo.py

The terminal, invoked after login, serves as the shell for Arianna Core.
	•	Logs: Each session logs to /arianna_core/log/, stamped with UTC.
	•	max_log_files option in ~/.letsgo/config to limit disk usage.
	•	History: /arianna_core/log/history persists command history, loaded at startup, updated on exit.
	•	Tab completion (readline): suggests built-in verbs — /status, /time, /run, /summarize, /search, /help.
	•	/status: Reports CPU cores, uptime (from /proc/uptime), and current IP.
	•	/summarize: Searches logs (with regex), prints last five matches; --history searches command history; /search <pattern> finds all matches.
	•	/time: Prints current UTC.
	•	/run : Executes shell command.
	•	/help: Lists verbs.
	•	Unrecognized input: echoed back.
	•	Structure ready for more advanced NLP (text hooks dispatch to remote models).

Logs timestamped with ISO-8601, using //: comments, for replay or training.

Minimal dependencies: pure Python stdlib, runs in initramfs even without extra packages.

⸻

Architecture
	•	Deterministic Alpine base: every config scrutinized, minimal subset for ext4, OverlayFS, namespaces.
	•	Build = equation solving: Each Make rule is a constraint; parallel compile = Amdahl’s law speedup.
	•	Boot: bzImage + compressed initramfs = linear product (associativity = reproducible starts).
	•	ext4 journaling ≈ integral, bounded loss under mid-write power cut.
	•	OverlayFS: writable layer (W) atop read-only (R), effective state S = R ∪ W (lookup-time union, O(1) mods).
	•	Namespaces: processes see disjoint sets (Nᵢ), echoing Leibniz’s monads.
	•	Cgroups: resource tree (T) with edge weights wₑ; ∑wₑ ≤ root cap, prevents runaway.
	•	Userland = trimmed Alpine: vector space — each package install = vector addition.
	•	letsgo.py: all commands core, monolithic, UI targets human (prompts), scripting possible (deterministic output).
	•	Async loop: (iₜ, oₜ) mapping, pure except logging.
	•	Logs: [(t₀, m₀), (t₁, m₁), …], ordered, enables conversation replay, time as axis.
	•	Summarize/search = projection π(L → L’), history retrieval = bounded inverse (last n elements).
	•	/status: samples (c, u, a) vector (cores, uptime, IP).
	•	/ping: impulse response f(t)=δ(t), echo pong proves alive.
	•	Concurrency: asyncio.create_subprocess_shell, Amdahl’s law for speedup.
	•	Minimalism = Occam’s razor.
	•	Security: fewer pkgs ≈ measure-zero attack surface.
	•	Extensible: Future bridges = morphisms, core algebra untouched.
	•	Self-reflection: log inspection = recursion, xₙ₊₁=f(xₙ).

⸻

Railway Deployment & Remote Interfaces

An HTTP bridge exposes letsgo.py to web clients and chat platforms. The container image (Dockerfile) starts bridge.py, which spawns the terminal and offers:
	•	REST: POST /run (HTTP basic auth).
	•	WebSocket: /ws?token=<API_TOKEN> (full-duplex terminal).
	•	Telegram: messages forwarded when TELEGRAM_TOKEN is set.
	
railway init
railway up

API_TOKEN secures all endpoints; TELEGRAM_TOKEN enables the bot.

API Example:

curl -u user:$API_TOKEN -X POST https://<host>/run -d cmd="/status"

WebSocket

const ws = new WebSocket(`wss://<host>/ws?token=${API_TOKEN}`);
ws.onmessage = e => console.log(e.data);
ws.onopen = () => ws.send('/time');

arianna_terminal.html in the repo is a mobile-friendly xterm.js console.

One kernel, many clients: Telegram bot and HTML terminal talk to same letsgo.py, share history/context.

License

This project is licensed under the GNU General Public License v3.0.








