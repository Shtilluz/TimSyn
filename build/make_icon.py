#!/usr/bin/env python3
"""
Конвертирует icon.png → timsyn.ico для PyInstaller.
Если icon.png не найден — генерирует иконку с часами.
"""
from PIL import Image
from pathlib import Path

ROOT = Path(__file__).parent.parent


def make_icon(out_path: Path):
    src = ROOT / "icon.png"
    sizes = [16, 24, 32, 48, 64, 128, 256]

    if src.exists():
        img = Image.open(src).convert("RGBA")
        print(f"  Icon: {src.name} ({img.size[0]}x{img.size[1]})")
        frames = [img.resize((s, s), Image.LANCZOS) for s in sizes]
    else:
        print("  icon.png not found — generating default icon")
        from PIL import ImageDraw
        frames = []
        for sz in sizes:
            i = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
            d = ImageDraw.Draw(i)
            pad = max(1, sz // 16)
            d.ellipse([pad, pad, sz-pad, sz-pad],
                      fill="#005cc5", outline="#003a8c", width=max(1, sz//20))
            cx, cy = sz//2, sz//2
            d.line([cx, cy, cx, pad+sz//6], fill="white", width=max(1, sz//16))
            d.line([cx, cy, sz-pad-sz//6, cy], fill="white", width=max(1, sz//20))
            r = max(1, sz//14)
            d.ellipse([cx-r, cy-r, cx+r, cy+r], fill="white")
            frames.append(i)

    frames[0].save(out_path, format="ICO",
                   sizes=[(s, s) for s in sizes],
                   append_images=frames[1:])
    print(f"  Saved -> {out_path}")


if __name__ == "__main__":
    make_icon(Path(__file__).parent / "timsyn.ico")
