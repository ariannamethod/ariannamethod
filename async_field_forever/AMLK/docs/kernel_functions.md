### Kernel Function Overview

The boot sequence begins when the processor leaves its reset vector and executes the kernel's entry point. Early code sets up a minimal stack, enables paging, and uncompresses the rest of the image so higher layers can run without firmware assistance.

Process scheduling follows the Completely Fair Scheduler which models runnable tasks as nodes on a red–black tree. Each task receives virtual runtime proportional to CPU usage, keeping latency bounded even as the number of processes grows.

Physical memory is abstracted through paging. Pages form fixed‑size frames that can be mapped, unmapped, or swapped, allowing the system to overcommit memory and isolate processes from one another.

Virtual memory mapping lets the kernel present each process with an independent address space. Page tables translate virtual addresses to physical frames and control access bits, preventing user code from touching kernel data.

The filesystem layer provides a unified API over disparate storage backends. Inodes represent files, dentries link them into directories, and the VFS routes operations to the appropriate driver, whether ext4 or procfs.

Ext4 supplies a journaling mechanism that groups writes into transactions. The journal acts like a write‑ahead log so if power fails mid‑operation, replaying the log restores the filesystem to a consistent state.

OverlayFS enables union mounts where a read‑only lower layer merges with an upper writable layer. The lower tier stays untouched while the upper records deltas, giving container workloads copy‑on‑write semantics.

Device drivers abstract hardware into kernel objects. They register with subsystems such as PCI or USB and expose file descriptors or network interfaces so user programs can interact without knowing device specifics.

The network stack implements the OSI layers from link through transport. Packets traverse routing tables, pass through firewalls, and surface as sockets, letting applications exchange bytes over TCP, UDP, or raw protocols.

System calls serve as the gateway between user mode and kernel mode. The `syscall` instruction triggers a controlled privilege transition, handing execution to vetted handlers that validate parameters before touching shared resources.

Interprocess communication relies on primitives like signals, pipes, and Unix domain sockets. These mechanisms provide synchronisation channels that avoid busy waiting and keep concurrency predictable.

Security enforcement leans on discretionary permissions and capabilities. Permissions gate file access while capabilities split superuser powers into fine‑grained bits that can be granted or dropped at runtime.

Namespaces carve the system into isolated views. Each namespace instance redefines a global resource such as the process table or network interfaces so containers operate as if they own the machine.

Control groups, or cgroups, apply resource limits using a hierarchical model. CPU shares, memory ceilings, and I/O weights cascade down the tree, ensuring that one workload cannot starve others.

Timekeeping is handled by high‑resolution timers and clock sources. The kernel maintains monotonic counters and exposes both wall‑clock and monotonic time so applications can measure intervals accurately.

Power management hooks allow the kernel to enter sleep states or throttle frequencies. Governors evaluate load and thermal data to trade off performance for energy savings when possible.

Build configuration trims unused options to reduce attack surface and binary size. By selecting only required drivers and features, the resulting image boots quickly and fits within constrained environments.

Logging and tracing facilities, such as `dmesg` and `ftrace`, record kernel events. Developers can study these streams to diagnose deadlocks, performance regressions, or driver misbehaviour.

Module loading lets the kernel extend itself at runtime. Loadable modules carry compiled code that can be inserted or removed without rebooting, enabling experiments and driver updates on the fly.

The minimal userland pairs with the kernel to deliver a cohesive platform. Busybox, Python, and the letsgo terminal provide just enough tools to launch services, inspect state, and iterate quickly.

