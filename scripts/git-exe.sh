#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# File:        git-exe.sh
# Path:        scripts/git-exe.sh
#
# -----------------------------------------------------------------------------

set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $(basename "$0") <full-path-to-file>" >&2
    exit 2
fi

file_path="$1"

if [[ ! -f "$file_path" ]]; then
    echo "Error: file does not exist: $file_path" >&2
    exit 1
fi

file_dir="$(cd -- "$(dirname -- "$file_path")" && pwd -P)"
file_name="$(basename -- "$file_path")"
full_path="$file_dir/$file_name"

repo_root="$(git -C "$file_dir" rev-parse --show-toplevel 2>/dev/null)" || {
    echo "Error: file is not inside a Git repository: $full_path" >&2
    exit 1
}

case "$full_path" in
    "$repo_root"/*)
        relative_path="${full_path#"$repo_root"/}"
        ;;
    *)
        echo "Error: unable to determine repository-relative path for: $full_path" >&2
        exit 1
        ;;
esac

if ! git -C "$repo_root" ls-files --error-unmatch -- "$relative_path" >/dev/null 2>&1; then
    echo "Error: file is not tracked by Git: $relative_path" >&2
    exit 1
fi

git -C "$repo_root" update-index --chmod=+x -- "$relative_path"

echo "Git executable flag set:"
echo "  repository: $repo_root"
echo "  file:       $relative_path"

git -C "$repo_root" ls-files --stage -- "$relative_path"
