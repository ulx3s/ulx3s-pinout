#!/usr/bin/env python3

"""Dispatch LPF-to-data generation to a board-specific parser."""

import argparse
import sys

from pinout_common import SUPPORTED_BOARDS, board_dir, load_python_module


def print_help():
    parser = argparse.ArgumentParser(
        description="Generate board-specific pinout data from an LPF file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("board", choices=SUPPORTED_BOARDS, help="Board definition to use.")
    parser.add_argument(
        "board_options",
        nargs=argparse.REMAINDER,
        help="Options passed to the selected board generator.",
    )
    parser.epilog = (
        "Examples:\n"
        "  ./generate-data-from-lpf.py ulx3s --include aliases\n"
        "  ./generate-data-from-lpf.py ulx4m-ld\n"
        "  ./generate-data-from-lpf.py ulx4m-ld --markdown output/ulx4m-ld/PIN-MAPPING.md\n"
        "\nUse '<board> --help' for board-specific options."
    )
    parser.print_help()


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)

    if not argv or argv[0] in ("-h", "--help"):
        print_help()
        return 0

    if argv[0] == "--list-boards":
        for board in SUPPORTED_BOARDS:
            print(board)
        return 0

    board = argv[0]
    if board not in SUPPORTED_BOARDS:
        print(
            f"ERROR: unsupported board {board!r}; choose: "
            + ", ".join(SUPPORTED_BOARDS),
            file=sys.stderr,
        )
        return 2

    generator_path = board_dir(board) / "generator.py"
    generator = load_python_module(
        generator_path,
        module_name="pinout_generator_" + board.replace("-", "_"),
    )
    if not hasattr(generator, "main"):
        print(f"ERROR: generator has no main(): {generator_path}", file=sys.stderr)
        return 1

    result = generator.main(argv[1:])
    return 0 if result is None else int(result)


if __name__ == "__main__":
    raise SystemExit(main())
