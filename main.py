#!/usr/bin/env python3
"""Entry program for make.fun news-image-20261121.

Writes the bundled front-page image to $MAKEFUN_OUTPUT_DIR/entry.png
(default /output). Standard library only: no network, no clock, no
randomness. The bundled image is validated first (PNG magic, size and
IHDR dimensions within the competition limits), then copied, and the
written file is re-read and checked byte-for-byte against the source,
so the two graded runs produce identical bytes.
"""

import hashlib
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "image.png")
MAX_BYTES = 1048576
MAX_DIMENSION = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def fail(message):
    print("error: %s" % message, file=sys.stderr)
    sys.exit(1)


def check_image(data):
    if len(data) > MAX_BYTES:
        fail("image is %d bytes, over the 1048576 limit" % len(data))
    if data[:8] != PNG_MAGIC:
        fail("image is not a PNG (bad magic bytes)")
    if len(data) < 33 or data[12:16] != b"IHDR":
        fail("image has no IHDR chunk")
    width, height = struct.unpack(">II", data[16:24])
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        fail("image is %dx%d, over the 1024x1024 limit" % (width, height))
    if data[-12:] != b"\x00\x00\x00\x00IEND\xaeB`\x82":
        fail("image has no IEND trailer chunk")
    return width, height


def main():
    try:
        with open(SOURCE, "rb") as handle:
            data = handle.read()
    except OSError as exc:
        fail("cannot read %s: %s" % (SOURCE, exc))

    width, height = check_image(data)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    try:
        with open(out_path, "wb") as handle:
            handle.write(data)
    except OSError as exc:
        fail("cannot write %s: %s" % (out_path, exc))

    try:
        with open(out_path, "rb") as handle:
            written = handle.read()
    except OSError as exc:
        fail("cannot re-read %s: %s" % (out_path, exc))
    if written != data:
        fail("written file differs from the bundled image")

    print("wrote %s  %dx%d  %d bytes  sha256 %s"
          % (out_path, width, height, len(data),
             hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
