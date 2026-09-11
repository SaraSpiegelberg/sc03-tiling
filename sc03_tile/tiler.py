# -*- coding: utf-8 -*-
"""Core de tiling: divide imagem em tiras que cabem na impressora (384px/48mm),
gera o layout (mapa mental) e o plano de consumo de papel."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

DPMM = 8  # dots por mm (203 dpi)
STRIP_WIDTH_MM = 48  # largura impressivel ~48mm (papel 58mm)

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\arial.ttf",
]


@dataclass
class TilePlan:
    img_w_cm: float
    img_h_cm: float
    strip_w_px: int
    overlap_px: int
    n_strips: int
    per_strip_cm: float
    total_cm: float
    strip_heights_px: list[int] = field(default_factory=list)


def _load_font(size: int):
    for p in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def load_scaled(path: str | Path, width_cm: float, height_cm: float) -> Image.Image:
    img = Image.open(path).convert("RGB")
    return img.resize((round(width_cm * 10 * DPMM), round(height_cm * 10 * DPMM)), Image.LANCZOS)


def plan(img: Image.Image, strip_width_mm: int = STRIP_WIDTH_MM, overlap_mm: float = 2.0) -> TilePlan:
    W, H = img.size
    strip_px = round(strip_width_mm * DPMM)
    step = max(1, strip_px - round(overlap_mm * DPMM))
    n = max(1, math.ceil(W / step))
    heights = []
    for i in range(n):
        x0 = i * step
        x1 = min(x0 + strip_px, W)
        heights.append(H)
    cm = H / DPMM / 10
    cut = 1.2
    total = n * (cm + cut)
    return TilePlan(
        img_w_cm=W / DPMM / 10,
        img_h_cm=H / DPMM / 10,
        strip_w_px=strip_px,
        overlap_px=round(overlap_mm * DPMM),
        n_strips=n,
        per_strip_cm=cm + cut,
        total_cm=total,
        strip_heights_px=heights,
    )


def tile_image(img: Image.Image, plan_: TilePlan, out_dir: Path, prefix: str = "tile") -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    W, H = img.size
    step = max(1, plan_.strip_w_px - plan_.overlap_px)
    paths: list[Path] = []
    for i in range(plan_.n_strips):
        x0 = i * step
        x1 = min(x0 + plan_.strip_w_px, W)
        crop = img.crop((x0, 0, x1, H))
        crop = crop.resize((plan_.strip_w_px, H), Image.LANCZOS)
        p = out_dir / f"{prefix}_{i+1:02d}_of_{plan_.n_strips:02d}.png"
        crop.save(p)
        paths.append(p)
    return paths


def build_layout(img: Image.Image, plan_: TilePlan, out_dir: Path, max_preview_px: int = 600) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    W, H = img.size
    step = max(1, plan_.strip_w_px - plan_.overlap_px)
    canvas = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(canvas)
    font = _load_font(max(8, round(H / plan_.n_strips * 0.25)))
    for i in range(plan_.n_strips):
        x0 = i * step
        x1 = min(x0 + plan_.strip_w_px, W)
        crop = img.crop((x0, 0, x1, H)).resize((x1 - x0, H), Image.LANCZOS)
        canvas.paste(crop, (x0, 0))
        d.rectangle([(x0, 0), (x1 - 1, H - 1)], outline="black", width=2)
        d.text((x0 + 6, 6), f"{i+1}/{plan_.n_strips}", font=font, fill="red")
    # salva preview
    ratio = max_preview_px / max(W, H)
    preview = canvas.resize((round(W * ratio), round(H * ratio)), Image.LANCZOS) if ratio < 1 else canvas
    p = out_dir / "layout_preview.png"
    preview.save(p)
    return p


def build_plan_txt(plan_: TilePlan) -> str:
    lines = [
        f"=== Plano de impressão tileada ===",
        f"Imagem: {plan_.img_w_cm:.1f} x {plan_.img_h_cm:.1f} cm",
        f"Tiras: {plan_.n_strips} x ~{plan_.strip_w_px/DPMM:.1f}mm de largura",
        f"Cada tira: {plan_.img_h_cm:.1f}cm de comprimento + 1.2cm de corte = {plan_.per_strip_cm:.1f}cm",
        f"Total estimado de papel: {plan_.total_cm:.1f}cm (~{plan_.total_cm/100:.1f}m)",
        f"",
        f"Ordem de colagem (da esquerda pra direita):",
    ]
    for i in range(plan_.n_strips):
        lines.append(f"  Tira {i+1:02d} -> cola na direita da tira {i:02d}")
    return "\n".join(lines)


def run(src: str | Path, width_cm: float, height_cm: float,
        out_dir: str | Path, strip_width_mm: int = STRIP_WIDTH_MM, overlap_mm: float = 2.0,
        max_preview_px: int = 600) -> tuple[TilePlan, list[Path], Path, str]:
    img = load_scaled(src, width_cm, height_cm)
    p = plan(img, strip_width_mm, overlap_mm)
    tiles = tile_image(img, p, Path(out_dir))
    layout = build_layout(img, p, Path(out_dir), max_preview_px)
    txt = build_plan_txt(p)
    (Path(out_dir) / "plano.txt").write_text(txt, encoding="utf-8")
    return p, tiles, layout, txt