# Continuous Integration

The CI workflow is designed to run entirely on CPU-only infrastructure. The build job installs no GPU drivers and passes
`-machine accel=tcg -vga none` to QEMU, forcing software emulation. This ensures that the kernel image can be built and
booted on generic runners without access to GPU hardware.
