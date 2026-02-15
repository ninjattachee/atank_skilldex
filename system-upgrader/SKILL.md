---
name: system-upgrader
description: Comprehensive system upgrade automation that updates system packages and user-space tools with optimized parallel execution. Use when the user requests system updates, package upgrades, or maintenance tasks. Triggers include requests like "update my system", "upgrade the OS", "keep my system up to date", "run system maintenance", or "I've updated upgrade.md, please sync the upgrade script".
---

# System Upgrader

Automate system-wide upgrades with intelligent parallelization for multi-core CPUs. Upgrades system packages (dnf/apt) and user-space tools (flatpak, bun, pnpm, uv, claude, etc.) while maximizing efficiency.

## Core Capabilities

### 1. Run System Upgrade

Execute the standalone upgrade script to update all system components:

```bash
/home/atank/Code/github.com/ninjattachee/system_upgrader/system-upgrader/scripts/upgrade_system.sh
```

**When to use**: User requests "update my system", "upgrade packages", "run system maintenance"

**What it does**:
- Phase 1: System-level updates (sequential) - dnf/apt with sudo
- Phase 2: User-space tools (parallel) - flatpak, bun, pnpm, uv, claude, etc.
- Reports success/failure for each component
- Exits with error if any command fails

### 2. Sync with upgrade.md

When the user modifies `upgrade.md` with new commands, regenerate the upgrade script:

```bash
python3 scripts/generate_upgrade_script.py /path/to/upgrade.md
```

**When to use**: User says "I've added commands to upgrade.md", "update the upgrade script", "sync the upgrade configuration"

**What it does**:
- Parses commands from `upgrade.md`
- Classifies commands using parallelization rules
- Regenerates optimized `upgrade_system.sh`
- Reports command grouping (system vs user-space)

### 3. Standalone Script Distribution

The generated `scripts/upgrade_system.sh` is fully standalone and can be:
- Copied to any location
- Run independently without the skill
- Shared with other systems
- Added to cron/systemd for automation

## Parallelization Strategy

Commands are classified using `references/parallelization_rules.md`:

**System-level (Sequential)**:
- Commands with `sudo`
- System package managers (dnf, apt, pacman)
- Shared system state modifications

**User-space (Parallel)**:
- Package managers: bun, pnpm, npm, yarn, cargo, uv, pipx
- Applications: flatpak, snap
- CLI tools: claude, gh
- Version managers: rustup, nvm, pyenv

## File Locations

- **upgrade.md**: Source of truth for upgrade commands (in project root)
- **scripts/generate_upgrade_script.py**: Parser and generator
- **scripts/upgrade_system.sh**: Generated standalone upgrade script
- **references/parallelization_rules.md**: Classification heuristics

## Workflow Examples

**Example 1: Run upgrade**
```
User: "Please update my system"
→ Execute scripts/upgrade_system.sh
→ Report results
```

**Example 2: Add new tool**
```
User: "I've added 'cargo update' to upgrade.md, please sync"
→ Read upgrade.md
→ Run generate_upgrade_script.py
→ Confirm regeneration with classification results
```

**Example 3: Customize parallelization**
```
User: "The gh command should run sequentially, not in parallel"
→ Read references/parallelization_rules.md
→ Update classification logic in generate_upgrade_script.py
→ Regenerate upgrade_system.sh
→ Test the changes
```

## Error Handling

The upgrade script uses `set -e` but continues on individual command failures to ensure all tools are attempted. Final exit code indicates overall success/failure.

Individual tool failures are tracked and reported in the summary.
