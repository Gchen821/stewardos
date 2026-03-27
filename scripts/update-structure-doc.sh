#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
README_FILE="$ROOT_DIR/README.md"
START_MARKER="<!-- STRUCTURE:START -->"
END_MARKER="<!-- STRUCTURE:END -->"

tmp_tree="$(mktemp)"
tmp_readme="$(mktemp)"
trap 'rm -f "$tmp_tree" "$tmp_readme"' EXIT

items=(
  "apps"
  "configs"
  "docs"
  "infra"
  "packages"
  "scripts"
  "tests"
  ".env.example"
  "docker-compose.yml"
  "package.json"
  "Makefile"
  "pnpm-workspace.yaml"
  "turbo.json"
  "tsconfig.base.json"
)

{
  echo "."
  for item in "${items[@]}"; do
    path="$ROOT_DIR/$item"
    [ -e "$path" ] || continue

    echo "- $item"

    if [ -d "$path" ]; then
      find "$path" \
        -mindepth 1 \
        -maxdepth 4 \
        \( \
          -name node_modules -o \
          -name .next -o \
          -name __pycache__ -o \
          -name .venv -o \
          -name .git -o \
          -name .pnpm-store \
        \) -prune -o -print \
        | sed "s|$ROOT_DIR/||" \
        | sort \
        | awk -F/ '
          {
            indent = ""
            for (i = 2; i <= NF; i++) {
              indent = indent "  "
            }
            print indent "- " $NF
          }
        '
    fi
  done
} >"$tmp_tree"

awk -v start="$START_MARKER" -v end="$END_MARKER" -v tree_file="$tmp_tree" '
  BEGIN { in_block=0 }
  {
    if ($0 == start) {
      print $0
      while ((getline line < tree_file) > 0) {
        print line
      }
      close(tree_file)
      in_block=1
      next
    }
    if ($0 == end) {
      in_block=0
      print $0
      next
    }
    if (!in_block) {
      print $0
    }
  }
' "$README_FILE" >"$tmp_readme"

cat "$tmp_readme" >"$README_FILE"
echo "README structure block updated."
