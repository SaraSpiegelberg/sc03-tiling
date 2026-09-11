# -*- coding: utf-8 -*-
"""CLI do sc03-tile — divisão tileada de imagens para impressão térmica SC03."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

DEFAULT_WRAPPER = r"C:\Users\Pichau\Desktop\.opencode\tools\timiniprint\print-sc03.ps1"


def main(argv: list[str] | None = None):
    ap = argparse.ArgumentParser(
        prog="sc03-tile",
        description="Divide uma imagem em tiras para impressão tileada na SC03h.",
    )
    ap.add_argument("image", help="Caminho da imagem (png/jpg)")
    ap.add_argument("--width-cm", type=float, required=True, help="Largura desejada em cm")
    ap.add_argument("--height-cm", type=float, required=True, help="Altura desejada em cm")
    ap.add_argument("--printable-mm", type=float, default=48.0, help="Largura impressivel por tira (mm, padrao 48)")
    ap.add_argument("--overlap-mm", type=float, default=2.0, help="Sobreposicao entre tiras (mm, padrao 2)")
    ap.add_argument("--out", type=str, default="out", help="Pasta de saida")
    ap.add_argument("--preset", choices=["fraco","medio","forte","max"], default="forte")
    ap.add_argument("--darkness", type=int, default=5)
    ap.add_argument("--dry-run", action="store_true", help="Gera planos e tiles mas nao imprime")
    ap.add_argument("--print", action="store_true", help="Imprime as tiras via wrapper")
    ap.add_argument("--print-plan", action="store_true", help="Imprime o plano.txt via wrapper")
    ap.add_argument("--wrapper", type=str, default=DEFAULT_WRAPPER, help="Caminho do wrapper print-sc03.ps1")
    args = ap.parse_args(argv)

    from .tiler import run
    plan_, tiles, layout, txt = run(args.image, args.width_cm, args.height_cm, args.out,
                                    args.printable_mm, args.overlap_mm)
    print(txt)
    print(f"\nLayout preview: {layout}")
    print(f"Tiras geradas em: {args.out}/")
    for t in tiles:
        print(f"  {t}")

    if args.dry_run or not (args.print or args.print_plan):
        return

    wrapper = Path(args.wrapper)
    if not wrapper.exists():
        print(f"AVISO: wrapper nao encontrado em {wrapper}", file=sys.stderr)
        return

    if args.print_plan:
        plan_file = Path(args.out) / "plano.txt"
        if plan_file.exists():
            _run_wrapper([str(plan_file)], wrapper)

    if args.print:
        for tile in tiles:
            print(f"Imprimindo {tile.name}...")
            _run_wrapper(["-File", str(tile), "-Preset", args.preset, "-Darkness", str(args.darkness)], wrapper)


def _run_wrapper(extra: list[str], wrapper: Path):
    cmd = [
        "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", str(wrapper),
    ] + extra
    subprocess.run(cmd, check=False)


if __name__ == "__main__":
    main()