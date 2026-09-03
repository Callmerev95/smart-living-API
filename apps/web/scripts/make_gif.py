"""Gabungkan frame PNG menjadi GIF animasi untuk README (`T-P6-08`).

Dijalankan setelah `pnpm capture`:

    uv run --with pillow python scripts/make_gif.py

Pillow diambil ke cache `uv`; tidak ada `pyproject.toml` maupun `.venv` yang
ditulis di `apps/web`.

Kenapa Pillow, bukan ffmpeg: ffmpeg bawaan Playwright hanya membawa encoder
`png` dan `libvpx` tanpa filter `palettegen`/`paletteuse`, sehingga tidak bisa
menghasilkan GIF. Memasang ffmpeg lengkap berarti ~100 MB untuk satu berkas.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ASSETS_DIR = Path(__file__).resolve().parents[3] / "docs" / "assets"
FRAMES_DIR = ASSETS_DIR / ".frames"
OUTPUT = ASSETS_DIR / "demo.gif"

MAX_BYTES = 3 * 1024 * 1024

# Lebar yang dicoba berurutan sampai ukuran berkas masuk anggaran.
WIDTHS = (1000, 900, 800, 720)

# Durasi tampil per frame (ms). Frame mengetik cepat; frame hasil dan detail
# ditahan agar pembaca punya waktu membacanya sebelum loop berulang.
FAST_MS = 320
HOLD_MS = 2600


# Dua frame terakhir (hasil rekomendasi dan detail resep) adalah yang ingin
# dibaca; sisanya hanya transisi mengetik.
HELD_TAIL_FRAMES = 2


def frame_durations(count: int) -> list[int]:
    """Frame yang perlu dibaca ditahan; frame transisi berjalan cepat.

    Urutan frame dari `capture.mts`: 1 awal, 3 mengetik, 1 hasil, 1 detail.
    """
    durations = [FAST_MS] * count
    for index in range(max(0, count - HELD_TAIL_FRAMES), count):
        durations[index] = HOLD_MS
    # Frame pertama ditahan supaya loop tidak terasa terpotong saat berulang.
    if durations:
        durations[0] = HOLD_MS
    return durations


def load_frames(width: int) -> list[Image.Image]:
    paths = sorted(FRAMES_DIR.glob("*.png"))
    if not paths:
        sys.exit(f"Tidak ada frame di {FRAMES_DIR}. Jalankan `pnpm capture` dulu.")

    frames: list[Image.Image] = []
    for path in paths:
        with Image.open(path) as source:
            image = source.convert("RGB")
            height = round(image.height * width / image.width)
            resized = image.resize((width, height), Image.LANCZOS)
            # Palet adaptif: UI ini hampir seluruhnya solid color, kuantisasi
            # hampir tanpa kehilangan. 256 warna masih muat di anggaran.
            frames.append(resized.convert("P", palette=Image.ADAPTIVE, colors=256))
    return frames


def write_gif(frames: list[Image.Image]) -> int:
    durations = frame_durations(len(frames))
    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=2,
    )
    return OUTPUT.stat().st_size


def main() -> None:
    for width in WIDTHS:
        size = write_gif(load_frames(width))
        mib = size / 1024 / 1024
        status = "OK" if size <= MAX_BYTES else "terlalu besar"
        print(f"  lebar {width}px -> {mib:.2f} MiB ({status})")

        if size <= MAX_BYTES:
            print(f"\n{OUTPUT.relative_to(ASSETS_DIR.parents[1])} siap.")
            return

    sys.exit(f"GIF masih di atas {MAX_BYTES / 1024 / 1024:.0f} MiB pada lebar terkecil.")


if __name__ == "__main__":
    main()
