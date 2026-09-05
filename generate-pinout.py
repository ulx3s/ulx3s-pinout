#!/usr/bin/env python3

"""Generate pinout diagrams for supported ULX boards."""

import argparse
import sys
from pathlib import Path

from pinout_common import REPO_ROOT, SUPPORTED_BOARDS, board_dir, board_output_dir


DEFAULT_BASENAME = {
    "ulx3s": "pinout_ulx3s",
    "ulx4m-ld": "pinout_ulx4m_ld",
}
EXPORT_FORMATS = ("svg", "png", "pdf", "ps")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a ULX board pinout from its board definition."
    )
    parser.add_argument(
        "board",
        nargs="?",
        choices=SUPPORTED_BOARDS + ("all",),
        help="Board to generate, or all supported boards.",
    )
    parser.add_argument(
        "--format",
        choices=EXPORT_FORMATS,
        default="svg",
        help="Output format (default: svg).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help=(
            "Output file. Valid only for one board. By default output is "
            "written below output/<board>/."
        ),
    )
    parser.add_argument(
        "--no-overwrite",
        action="store_true",
        help="Let pinout.manager choose a unique output name instead of overwriting.",
    )
    parser.add_argument(
        "--list-boards",
        action="store_true",
        help="List supported board names and exit.",
    )
    return parser.parse_args()


def default_output(board, output_format):
    return board_output_dir(board) / f"{DEFAULT_BASENAME[board]}.{output_format}"


def export_one(board, output_format, output, overwrite):
    try:
        from pinout.manager import export_diagram
    except ImportError as exc:
        raise RuntimeError(
            "The pinout package is required. Install dependencies with: "
            "python3 -m pip install --user --upgrade pinout cairosvg pillow"
        ) from exc

    layout = (board_dir(board) / "layout.py").resolve()
    if not layout.is_file():
        raise FileNotFoundError(f"board layout not found: {layout}")

    output = Path(output).resolve()
    expected_suffix = "." + output_format
    if output.suffix.lower() != expected_suffix:
        raise ValueError(
            f"output extension {output.suffix or '<none>'!r} does not match "
            f"--format {output_format!r}; expected {expected_suffix}"
        )
    output.parent.mkdir(parents=True, exist_ok=True)

    # pinout.manager reports some export failures on stderr without raising an
    # exception. Remove the previous target when overwriting, then verify that
    # this invocation actually created a non-empty file. This prevents a stale
    # artifact (or a swallowed converter error) from being reported as success.
    if overwrite and output.exists():
        output.unlink()

    export_diagram(layout, output, overwrite=overwrite)

    if overwrite and (not output.is_file() or output.stat().st_size == 0):
        raise RuntimeError(f"pinout export did not create output: {output}")


def main():
    args = parse_args()

    if args.list_boards:
        for board in SUPPORTED_BOARDS:
            print(board)
        return 0

    if args.board is None:
        print("ERROR: board is required unless --list-boards is used", file=sys.stderr)
        return 2

    boards = SUPPORTED_BOARDS if args.board == "all" else (args.board,)
    if args.output is not None and len(boards) != 1:
        print("ERROR: --output can only be used when generating one board", file=sys.stderr)
        return 2

    try:
        for board in boards:
            output = args.output or default_output(board, args.format)
            export_one(
                board,
                args.format,
                output,
                overwrite=not args.no_overwrite,
            )
            print(f"Board: {board}")
            print(f"Output: {Path(output)}")
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
