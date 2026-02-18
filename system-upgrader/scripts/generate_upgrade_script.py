#!/usr/bin/env python3
"""
Generate optimized upgrade_system.sh from upgrade.md

Reads upgrade.md, classifies commands by parallelization potential,
and generates a standalone bash script with optimal execution strategy.
"""

import re
import sys
from pathlib import Path


def parse_upgrade_md(filepath):
    """Extract bash commands from upgrade.md"""
    content = Path(filepath).read_text()

    # Find bash code block
    bash_block_pattern = r'```bash\n(.*?)\n```'
    matches = re.findall(bash_block_pattern, content, re.DOTALL)

    if not matches:
        print("Error: No bash code block found in upgrade.md", file=sys.stderr)
        sys.exit(1)

    # Get commands from first bash block
    commands_text = matches[0]
    lines = commands_text.strip().split('\n')

    commands = []
    for line in lines:
        line = line.strip()
        # Skip shebang, empty lines, and comments
        if line and not line.startswith('#!') and not line.startswith('#'):
            # Remove inline comments
            cmd = re.sub(r'\s+#.*$', '', line)
            if cmd:
                commands.append(cmd)

    return commands


def classify_command(cmd):
    """Classify command as 'system' or 'user-space'"""
    cmd_stripped = cmd.strip()

    # System-level commands (require sudo or modify system packages)
    if cmd_stripped.startswith('sudo'):
        return 'system'

    # Remove environment variables from the beginning (e.g., "https_proxy= bun upgrade")
    # to get the actual command
    cmd_without_env = re.sub(r'^(\w+=\S*\s+)+', '', cmd_stripped)

    # User-space package managers and tools
    user_tools = ['flatpak', 'bun', 'pnpm', 'npm', 'yarn', 'cargo', 'uv',
                  'claude', 'pipx', 'rustup', 'nvm', 'pyenv', 'gh']

    for tool in user_tools:
        if cmd_without_env.startswith(tool):
            return 'user-space'

    # Default to system if unsure (safer)
    return 'system'


def generate_script(commands, output_path):
    """Generate optimized upgrade_system.sh"""

    # Classify commands
    system_cmds = []
    userspace_cmds = []

    for cmd in commands:
        if classify_command(cmd) == 'system':
            system_cmds.append(cmd)
        else:
            userspace_cmds.append(cmd)

    # Generate script
    script = """#!/usr/bin/env bash
#
# System Upgrader - Auto-generated from upgrade.md
# Optimized for parallel execution on multi-core systems
#

set -e  # Exit on error
trap 'echo "❌ Upgrade failed at line $LINENO"' ERR

echo "🚀 Starting system upgrade..."
echo ""

# Track failures via temp dir so background subshells can write to it
FAIL_DIR=$(mktemp -d)
trap 'rm -rf "$FAIL_DIR"' EXIT

# Function to run command and track status
run_cmd() {
    local cmd="$1"
    local name="$2"
    echo "▶ Running: $name"
    if eval "$cmd"; then
        echo "✅ $name completed"
    else
        echo "❌ $name failed"
        echo "$name" > "$FAIL_DIR/$(echo "$name" | tr ' ' '_')"
    fi
}

"""

    # Add system commands (sequential)
    if system_cmds:
        script += """# ===================================
# Phase 1: System-level updates (sequential)
# ===================================
echo "📦 Phase 1: System-level updates"
echo ""

"""
        for cmd in system_cmds:
            script += f'run_cmd "{cmd}" "System package update"\n'

        script += '\necho ""\n\n'

    # Add user-space commands (parallel)
    if userspace_cmds:
        script += """# ===================================
# Phase 2: User-space tools (parallel)
# ===================================
echo "🔧 Phase 2: User-space tool updates (parallel)"
echo ""

# Run user-space updates in parallel
"""
        for i, cmd in enumerate(userspace_cmds):
            # Extract tool name for display (skip env vars like https_proxy=)
            cmd_without_env = re.sub(r'^(\w+=\S*\s+)+', '', cmd.strip())
            tool_name = cmd_without_env.split()[0]
            script += f'run_cmd "{cmd}" "{tool_name}" &\n'

        script += """
# Wait for all parallel jobs
wait

echo ""
"""

    # Add summary
    script += """
# ===================================
# Summary
# ===================================
echo ""
echo "✨ System upgrade completed!"

# Collect failures written by background subshells
declare -a FAILED_COMMANDS=()
for f in "$FAIL_DIR"/*; do
    [ -f "$f" ] && FAILED_COMMANDS+=("$(cat "$f")")
done

if [ ${#FAILED_COMMANDS[@]} -eq 0 ]; then
    echo "✅ All commands succeeded"
    exit 0
else
    echo "❌ Some commands failed:"
    for cmd in "${FAILED_COMMANDS[@]}"; do
        echo "  - $cmd"
    done
    exit 1
fi
"""

    # Write script
    Path(output_path).write_text(script)
    Path(output_path).chmod(0o755)  # Make executable

    print(f"✅ Generated: {output_path}")
    print(f"   System commands: {len(system_cmds)}")
    print(f"   User-space commands: {len(userspace_cmds)} (parallel)")


def main():
    # Determine paths
    if len(sys.argv) > 1:
        upgrade_md_path = sys.argv[1]
    else:
        # Default: look for upgrade.md in parent directory
        upgrade_md_path = Path(__file__).parent.parent.parent / "upgrade.md"

    if not Path(upgrade_md_path).exists():
        print(f"Error: upgrade.md not found at {upgrade_md_path}", file=sys.stderr)
        print("Usage: python3 generate_upgrade_script.py [path/to/upgrade.md]", file=sys.stderr)
        sys.exit(1)

    output_path = Path(__file__).parent / "upgrade_system.sh"

    print(f"📖 Reading: {upgrade_md_path}")
    commands = parse_upgrade_md(upgrade_md_path)

    print(f"📝 Found {len(commands)} commands")
    generate_script(commands, output_path)
    print("")
    print(f"🎉 Done! Run the script: {output_path}")


if __name__ == "__main__":
    main()
