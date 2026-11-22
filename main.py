#!/usr/bin/env python3
"""Entry program for news-image-20261121 rev-2.

Reads the bundled front page (image.png, next to this file), walks its
PNG chunks to make sure the file is whole and exactly 1024x1024, then
writes the same bytes to $MAKEFUN_OUTPUT_DIR/entry.png (default
/output) and reads the output back to confirm it matches byte for byte.

A PNG is a signature followed by chunks; each chunk is a 4-byte length,
a 4-byte type, that many data bytes and a 4-byte CRC. This program checks
the signature, the first chunk (IHDR: 13 data bytes, the right size, a
matching CRC) and that the last chunk is an empty IEND with a matching
CRC. It also walks every chunk in between so a truncated or padded file
cannot slip through.

Standard library only. No network, no randomness, no clock: two runs
write identical bytes.
"""
import binascii
import os
import struct
import sys

IMAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image.png")
LIMIT = 1048576
SIDE = 1024
SIGNATURE = b"\x89PNG\r\n\x1a\n"


def abort(reason):
    print("error: " + reason, file=sys.stderr)
    sys.exit(1)


def crc(chunk_type, payload):
    return binascii.crc32(chunk_type + payload) & 0xFFFFFFFF


def walk_chunks(blob):
    """Yield (type, payload) for every chunk; abort on any defect."""
    if blob[:8] != SIGNATURE:
        abort("missing PNG signature")
    pos = 8
    seen = []
    while pos < len(blob):
        if pos + 8 > len(blob):
            abort("truncated chunk header at offset %d" % pos)
        size, ctype = struct.unpack(">I4s", blob[pos:pos + 8])
        end = pos + 12 + size
        if end > len(blob):
            abort("truncated %s chunk" % ctype.decode("latin-1"))
        payload = blob[pos + 8:pos + 8 + size]
        stored = struct.unpack(">I", blob[pos + 8 + size:end])[0]
        if crc(ctype, payload) != stored:
            abort("%s chunk CRC mismatch" % ctype.decode("latin-1"))
        seen.append((ctype, payload))
        pos = end
    if not seen or seen[0][0] != b"IHDR":
        abort("first chunk is not IHDR")
    if seen[-1] != (b"IEND", b""):
        abort("last chunk is not an empty IEND")
    return seen


def check_image(blob):
    if len(blob) > LIMIT:
        abort("image is %d bytes, over the %d byte limit" % (len(blob), LIMIT))
    chunks = walk_chunks(blob)
    ihdr = chunks[0][1]
    if len(ihdr) != 13:
        abort("IHDR is %d bytes, expected 13" % len(ihdr))
    width, height = struct.unpack(">II", ihdr[:8])
    if (width, height) != (SIDE, SIDE):
        abort("image is %dx%d, expected %dx%d"
              % (width, height, SIDE, SIDE))
    depth, colour = ihdr[8], ihdr[9]
    if depth != 8 or colour != 2:
        abort("unexpected IHDR colour layout: depth %d, type %d"
              % (depth, colour))


def main():
    try:
        with open(IMAGE, "rb") as handle:
            blob = handle.read()
    except OSError as exc:
        abort("cannot read %s: %s" % (IMAGE, exc))
    check_image(blob)
    dest_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, "entry.png")
    with open(dest, "wb") as handle:
        handle.write(blob)
    with open(dest, "rb") as handle:
        back = handle.read()
    if back != blob:
        abort("output differs from the bundled image")
    print("wrote %s (%d bytes, %dx%d, %d chunks)"
          % (dest, len(blob), SIDE, SIDE, len(walk_chunks(blob))))


if __name__ == "__main__":
    main()
