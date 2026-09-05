#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
BUILD_DIR="${PINOUT_TEST_BUILD_DIR:-${REPO_ROOT}/build/pinout-tests}"

lint_self()
{
    if command -v shellcheck >/dev/null 2>&1; then
        shellcheck "${BASH_SOURCE[0]}"
    else
        echo "WARNING: shellcheck not found; self-lint skipped." >&2
    fi
}

require_file()
{
    local path="$1"

    if [[ ! -s "${path}" ]]; then
        echo "ERROR: expected non-empty file: ${path}" >&2
        return 1
    fi
}

compare_files()
{
    local expected="$1"
    local actual="$2"

    if ! cmp -s "${expected}" "${actual}"; then
        echo "ERROR: regenerated file differs from committed file:" >&2
        echo "  expected: ${expected}" >&2
        echo "  actual:   ${actual}" >&2
        diff -u "${expected}" "${actual}" || true
        return 1
    fi
}


test_stylesheet_compatibility()
{
    local matches

    matches="$(grep -nE 'rgb\([[:space:]]*[0-9]+[[:space:]]+[0-9]+[[:space:]]+[0-9]+[[:space:]]*\)' styles.css || true)"
    if [[ -n "${matches}" ]]; then
        echo "ERROR: styles.css contains space-separated rgb() colors." >&2
        echo "The pinout PNG exporter requires comma-separated rgb() or hex colors:" >&2
        printf '%s\n' "${matches}" >&2
        return 1
    fi
}

test_board_list()
{
    local expected actual

    expected=$'ulx3s\nulx4m-ld'

    actual="$("${PYTHON_BIN}" generate-pinout.py --list-boards)"
    if [[ "${actual}" != "${expected}" ]]; then
        echo "ERROR: generate-pinout.py --list-boards returned unexpected output:" >&2
        printf '%s\n' "${actual}" >&2
        return 1
    fi

    actual="$("${PYTHON_BIN}" generate-data-from-lpf.py --list-boards)"
    if [[ "${actual}" != "${expected}" ]]; then
        echo "ERROR: generate-data-from-lpf.py --list-boards returned unexpected output:" >&2
        printf '%s\n' "${actual}" >&2
        return 1
    fi
}

test_default_data()
{
    local output_dir="${BUILD_DIR}/default-data"

    mkdir -p "${output_dir}/ulx3s" "${output_dir}/ulx4m-ld"

    "${PYTHON_BIN}" generate-data-from-lpf.py ulx3s \
        -o "${output_dir}/ulx3s/data.py" \
        --include aliases \
        --markdown "${output_dir}/ulx3s/PIN-MAPPING.md"

    "${PYTHON_BIN}" generate-data-from-lpf.py ulx4m-ld \
        -o "${output_dir}/ulx4m-ld/data.py" \
        --markdown "${output_dir}/ulx4m-ld/PIN-MAPPING.md"

    compare_files boards/ulx3s/data.py "${output_dir}/ulx3s/data.py"
    compare_files boards/ulx4m-ld/data.py "${output_dir}/ulx4m-ld/data.py"

    require_file "${output_dir}/ulx3s/PIN-MAPPING.md"
    require_file "${output_dir}/ulx4m-ld/PIN-MAPPING.md"
}

test_all_constraints()
{
    local lpf stem output_dir

    output_dir="${BUILD_DIR}/constraint-sweep"
    mkdir -p "${output_dir}/ulx3s" "${output_dir}/ulx4m-ld"

    for lpf in boards/ulx3s/constraints/*.lpf; do
        stem="$(basename "${lpf}" .lpf)"
        echo "Testing ULX3S constraint: ${lpf}"
        "${PYTHON_BIN}" generate-data-from-lpf.py ulx3s "${lpf}" \
            -o "${output_dir}/ulx3s/${stem}.py" \
            --markdown "${output_dir}/ulx3s/${stem}.md"
        require_file "${output_dir}/ulx3s/${stem}.py"
        require_file "${output_dir}/ulx3s/${stem}.md"
    done

    for lpf in boards/ulx4m-ld/constraints/*.lpf; do
        stem="$(basename "${lpf}" .lpf)"
        echo "Testing ULX4M-LD constraint: ${lpf}"
        "${PYTHON_BIN}" generate-data-from-lpf.py ulx4m-ld "${lpf}" \
            -o "${output_dir}/ulx4m-ld/${stem}.py" \
            --markdown "${output_dir}/ulx4m-ld/${stem}.md"
        require_file "${output_dir}/ulx4m-ld/${stem}.py"
        require_file "${output_dir}/ulx4m-ld/${stem}.md"
    done

    "${PYTHON_BIN}" generate-data-from-lpf.py ulx3s \
        boards/ulx3s/constraints/ulx3s_v316.lpf \
        -o "${output_dir}/ulx3s/ulx3s_v316_aliases.py" \
        --include aliases
    require_file "${output_dir}/ulx3s/ulx3s_v316_aliases.py"
}

test_rendering()
{
    local output_dir="${BUILD_DIR}/rendered"

    mkdir -p "${output_dir}"

    echo "Rendering ULX3S SVG and PNG..."
    "${PYTHON_BIN}" generate-pinout.py ulx3s \
        --output "${output_dir}/pinout_ulx3s.svg"
    "${PYTHON_BIN}" generate-pinout.py ulx3s \
        --format png \
        --output "${output_dir}/pinout_ulx3s.png"

    echo "Rendering ULX4M-LD SVG and PNG..."
    "${PYTHON_BIN}" generate-pinout.py ulx4m-ld \
        --output "${output_dir}/pinout_ulx4m_ld.svg"
    "${PYTHON_BIN}" generate-pinout.py ulx4m-ld \
        --format png \
        --output "${output_dir}/pinout_ulx4m_ld.png"

    require_file "${output_dir}/pinout_ulx3s.svg"
    require_file "${output_dir}/pinout_ulx3s.png"
    require_file "${output_dir}/pinout_ulx4m_ld.svg"
    require_file "${output_dir}/pinout_ulx4m_ld.png"

    grep -q '<svg' "${output_dir}/pinout_ulx3s.svg"
    grep -q '<svg' "${output_dir}/pinout_ulx4m_ld.svg"

    "${PYTHON_BIN}" - "${output_dir}" <<'PYVERIFY'
from pathlib import Path
import sys

from PIL import Image

output_dir = Path(sys.argv[1])
expected = (
    output_dir / "pinout_ulx3s.png",
    output_dir / "pinout_ulx4m_ld.png",
)

for path in expected:
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        if image.format != "PNG":
            raise SystemExit(f"ERROR: expected PNG image: {path}")
        width, height = image.size
        if width <= 0 or height <= 0:
            raise SystemExit(f"ERROR: invalid image dimensions {width}x{height}: {path}")
        print(f"Verified PNG: {path} ({width}x{height})")
PYVERIFY
}

main()
{
    lint_self

    cd "${REPO_ROOT}"

    if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
        echo "ERROR: Python interpreter not found: ${PYTHON_BIN}" >&2
        return 1
    fi

    if [[ ! -x generate-data-from-lpf.py ]]; then
        echo "ERROR: generate-data-from-lpf.py is not executable." >&2
        return 1
    fi
    if [[ ! -x generate-pinout.py ]]; then
        echo "ERROR: generate-pinout.py is not executable." >&2
        return 1
    fi

    rm -rf -- "${BUILD_DIR:?}"
    mkdir -p "${BUILD_DIR}"
    export PYTHONDONTWRITEBYTECODE=1

    echo "Python: $("${PYTHON_BIN}" --version 2>&1)"
    echo "Build directory: ${BUILD_DIR}"

    "${PYTHON_BIN}" - <<'PY'
from pathlib import Path

paths = [
    Path("generate-data-from-lpf.py"),
    Path("generate-pinout.py"),
    Path("pinout_common.py"),
]
for board_dir in (Path("boards/ulx3s"), Path("boards/ulx4m-ld")):
    paths.extend(sorted(board_dir.glob("*.py")))

for path in paths:
    compile(path.read_bytes(), str(path), "exec")

print(f"Syntax-checked {len(paths)} Python files.")
PY

    "${PYTHON_BIN}" generate-data-from-lpf.py --help >/dev/null
    "${PYTHON_BIN}" generate-data-from-lpf.py ulx3s --help >/dev/null
    "${PYTHON_BIN}" generate-data-from-lpf.py ulx4m-ld --help >/dev/null
    "${PYTHON_BIN}" generate-pinout.py --help >/dev/null
    "${PYTHON_BIN}" generate-data-from-lpf.py ulx3s --list-fields >/dev/null

    test_board_list
    test_stylesheet_compatibility
    test_rendering
    test_default_data
    test_all_constraints

    echo "Pinout script tests passed."
}

main "$@"
