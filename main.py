#!/usr/bin/env python3
"""Cheeseburger Melt: the make.fun food-picture-01 entry.

The bundled picture is a juicy cheeseburger, shot close up with a glossy
toasted sesame bun and cheddar melting down the patty. This program copies
that picture to the output directory the grader provides and verifies it
fits the bounty limits before it leaves: no more than 1 MiB, no side
longer than 1024 pixels, PNG or JPEG. Only the standard library is used,
and every run writes the same bytes.
"""

import os
import shutil
import struct

MAX_BYTES = 1_048_576
MAX_SIDE = 1024
PICTURE_NAME = "entry.png"
# Entry title: "Cheeseburger Melt".


def bundled_picture() -> str:
    """Absolute path of the picture shipped next to this program."""
    folder = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(folder, PICTURE_NAME)


def jpeg_dimensions(blob: bytes) -> tuple[int, int]:
    """Width and height of a JPEG, found by walking its markers."""
    cursor = 2
    while cursor + 1 < len(blob):
        if blob[cursor] != 0xFF:
            cursor += 1
            continue
        marker = blob[cursor + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            height, width = struct.unpack_from(">HH", blob, cursor + 5)
            return width, height
        (segment,) = struct.unpack_from(">H", blob, cursor + 2)
        cursor += 2 + segment
    raise ValueError("JPEG has no start-of-frame marker")


def png_dimensions(blob: bytes) -> tuple[int, int]:
    """Width and height of a PNG, read from its IHDR chunk."""
    if blob[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("picture is neither JPEG nor PNG")
    width, height = struct.unpack_from(">II", blob, 16)
    return width, height


# Deterministic by construction: copy plus checks only, no randomness.
def run() -> None:
    """Copy the picture out and check it against the bounty limits."""
    destination_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(destination_dir, exist_ok=True)
    destination = os.path.join(destination_dir, PICTURE_NAME)
    shutil.copyfile(bundled_picture(), destination)
    with open(destination, "rb") as picture_file:
        blob = picture_file.read()
    if len(blob) > MAX_BYTES:
        raise SystemExit(f"picture is {len(blob)} bytes, over the 1 MiB cap")
    if blob[:2] == b"\xff\xd8":
        width, height = jpeg_dimensions(blob)
    else:
        width, height = png_dimensions(blob)
    if width > MAX_SIDE or height > MAX_SIDE:
        raise SystemExit(f"picture is {width}x{height}, over the 1024 cap")


if __name__ == "__main__":
    run()
