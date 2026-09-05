#!/usr/bin/env python3

"""Shared helpers for the ULX pinout generators."""

import base64
import html
import importlib.util
import io
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
SUPPORTED_BOARDS = ("ulx3s", "ulx4m-ld")


def board_dir(board):
    """Return the directory containing one board definition."""
    if board not in SUPPORTED_BOARDS:
        raise ValueError(f"unsupported board: {board}")
    return REPO_ROOT / "boards" / board


def board_output_dir(board):
    """Return the default output directory for one board."""
    return REPO_ROOT / "output" / board


def stylesheet_path():
    """Return the shared stylesheet path."""
    return REPO_ROOT / "styles.css"


def load_python_module(path, module_name=None):
    """Load a Python module from an explicit filesystem path."""
    path = Path(path).resolve()
    if module_name is None:
        safe_stem = re.sub(r"[^A-Za-z0-9_]", "_", path.stem)
        safe_parent = re.sub(r"[^A-Za-z0-9_]", "_", path.parent.name)
        module_name = f"pinout_{safe_parent}_{safe_stem}"

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"unable to load Python module: {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_board_data(layout_file):
    """Load data.py next to a board layout module."""
    path = Path(layout_file).resolve().parent / "data.py"
    return load_python_module(path)


def normalized_png_data_uri(path, expected_size=None):
    """Return an EXIF-normalized image as a self-contained PNG data URI."""
    try:
        from PIL import Image as PILImage
        from PIL import ImageOps
    except ImportError as exc:
        raise RuntimeError(
            "Pillow is required for image orientation normalization. "
            "Install it with: python3 -m pip install --user pillow"
        ) from exc

    path = Path(path)
    with PILImage.open(path) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        if expected_size is not None and image.size != tuple(expected_size):
            width, height = expected_size
            raise ValueError(
                f"Expected {width}x{height} image, got "
                f"{image.size[0]}x{image.size[1]}: {path}"
            )

        output = io.BytesIO()
        image.save(output, format="PNG", optimize=True)

    encoded = base64.b64encode(output.getvalue()).decode("ascii")
    return "data:image/png;base64," + encoded


def escape_svg(value):
    """Escape a value for inclusion in SVG markup."""
    return html.escape(str(value), quote=True)


def interpolate_point(start, end, index, count):
    """Interpolate one point from inclusive endpoints."""
    if count < 2:
        raise ValueError("interpolation count must be at least 2")
    if not 0 <= index < count:
        raise ValueError(f"interpolation index {index} outside 0..{count - 1}")

    fraction = index / (count - 1)
    return (
        start[0] + (end[0] - start[0]) * fraction,
        start[1] + (end[1] - start[1]) * fraction,
    )
