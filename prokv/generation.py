"""Stage 1: generate images from a text prompt."""

from __future__ import annotations

import hashlib
import struct
import zlib
from abc import ABC, abstractmethod
from pathlib import Path

from prokv.models import GeneratedImage


class ImageGenerator(ABC):
    """Turns a prompt into image files on disk."""

    @abstractmethod
    def generate(self, prompt: str, count: int, out_dir: Path) -> list[GeneratedImage]:
        ...


class PlaceholderGenerator(ImageGenerator):
    """Offline stand-in: writes solid-colour PNGs derived from the prompt.

    Needs no network, API keys or third-party packages. Replace with a real
    generator once one has been chosen.
    """

    def __init__(self, width: int = 768, height: int = 1024) -> None:
        self.width = width
        self.height = height

    def generate(self, prompt: str, count: int, out_dir: Path) -> list[GeneratedImage]:
        out_dir.mkdir(parents=True, exist_ok=True)
        images = []
        for i in range(count):
            digest = hashlib.sha256(f"{prompt}:{i}".encode()).digest()
            path = out_dir / f"image_{i:02d}.png"
            _write_solid_png(path, self.width, self.height, digest[:3])
            images.append(GeneratedImage(path, prompt, self.width, self.height))
        return images


def _write_solid_png(path: Path, width: int, height: int, rgb: bytes) -> None:
    def chunk(tag: bytes, data: bytes) -> bytes:
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    row = b"\x00" + rgb * width
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(row * height, 9))
        + chunk(b"IEND", b"")
    )
