"""Create PHISHEYE shield-and-eye icons without extra dependencies."""
from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "assets"
INK = (245, 245, 245, 255)
RED = (255, 0, 0, 255)
WHITE = (255, 255, 255, 255)
CLEAR = (0, 0, 0, 0)


def write_png(path: Path, width: int, height: int, pixels: list[tuple[int, int, int, int]]) -> None:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = b""
    i = 0
    for _y in range(height):
        raw += b"\x00"
        for _x in range(width):
            raw += bytes(pixels[i])
            i += 1
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def in_shield(x: float, y: float) -> bool:
    if y < 0.10 or y > 0.92:
        return False
    if y <= 0.50:
        return 0.18 <= x <= 0.82
    width = 0.32 * (0.92 - y) / 0.42
    return abs(x - 0.50) <= width


def in_eye(x: float, y: float) -> bool:
    return ((x - 0.50) / 0.28) ** 2 + ((y - 0.48) / 0.16) ** 2 <= 1.0


def stroke(fn, x: float, y: float, thickness: float) -> bool:
    if not fn(x, y):
        return False
    for dx, dy in ((thickness, 0), (-thickness, 0), (0, thickness), (0, -thickness)):
        if not fn(x + dx, y + dy):
            return True
    return False


def make_icon(size: int) -> list[tuple[int, int, int, int]]:
    thickness = 0.055 if size <= 16 else 0.04
    pixels = []
    for y in range(size):
        for x in range(size):
            nx = (x + 0.5) / size
            ny = (y + 0.5) / size
            color = CLEAR
            if stroke(in_shield, nx, ny, thickness):
                color = INK
            if stroke(in_eye, nx, ny, thickness * 0.9):
                color = INK
            if math.hypot(nx - 0.50, ny - 0.48) <= (0.10 if size > 16 else 0.12):
                color = RED
            if size >= 32 and math.hypot(nx - 0.54, ny - 0.44) <= 0.03:
                color = WHITE
            pixels.append(color)
    return pixels


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    for size in (16, 32, 48, 128):
        write_png(ROOT / f"icon{size}.png", size, size, make_icon(size))
    print(f"Wrote icons to {ROOT}")


if __name__ == "__main__":
    main()
