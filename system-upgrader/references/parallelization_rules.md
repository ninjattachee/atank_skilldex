# Parallelization Rules for System Upgrades

## Command Classification

### System-Level Commands (Sequential)
Commands that require elevated privileges or modify system-wide state should run sequentially:
- `sudo dnf update/upgrade` - System package manager
- `sudo apt update/upgrade` - Debian/Ubuntu package manager
- `sudo pacman -Syu` - Arch package manager
- Any command with `sudo` that modifies system packages

**Why sequential**: These may affect system libraries that user-space tools depend on.

### User-Space Tools (Parallel)
Commands that update user-level tools can run in parallel:
- Package managers: `bun`, `pnpm`, `npm`, `yarn`, `cargo`, `pip`, `pipx`, `uv`
- Application updates: `flatpak`, `snap`, `appimage`
- CLI tools: `claude`, `gh`, `docker` (user-level)
- Language version managers: `rustup`, `nvm`, `pyenv`

**Why parallel**: Independent tools with separate caches/installations.

## Dependency Detection

### Sequential Indicators
- Uses `sudo`
- Updates system packages (`/usr/bin`, `/usr/lib`)
- Modifies shared system state

### Parallel Indicators
- User-space only (`~/.local`, `~/.cargo`, `~/.bun`, etc.)
- Independent tool ecosystems
- No shared state between commands

## Grouping Strategy

1. **Phase 1**: System updates (sequential)
2. **Phase 2**: User-space tools (parallel, max concurrency = CPU cores)

## Error Handling

- Continue on error for individual tools
- Report all successes and failures at end
- Exit with error code if any command fails
