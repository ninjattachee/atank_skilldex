#!/usr/bin/env bash
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

# ===================================
# Phase 1: System-level updates (sequential)
# ===================================
echo "📦 Phase 1: System-level updates"
echo ""

run_cmd "sudo dnf update" "System package update"

echo ""

# ===================================
# Phase 2: User-space tools (parallel)
# ===================================
echo "🔧 Phase 2: User-space tool updates (parallel)"
echo ""

# Run user-space updates in parallel
run_cmd "flatpak update" "flatpak" &
run_cmd "https_proxy= bun upgrade && https_proxy= bun update -g" "bun" &
run_cmd "pnpm self-update && pnpm up -g" "pnpm" &
run_cmd "uv self update && uv tool upgrade --all" "uv" &
run_cmd "claude update" "claude" &

# Wait for all parallel jobs
wait

echo ""

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
