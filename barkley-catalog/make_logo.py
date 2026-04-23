"""
Gera logo_source.png tipográfico premium para Barkley Cigar.
Usa apenas texto (sem silhueta) até o logo.pdf real estar disponível.
Layout: "BARKLEY" em serif bold vertical + ornamento + tagline vertical.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

GOLD  = (191, 155, 48, 255)
TRANS = (0, 0, 0, 0)
W, H  = 500, 720
BASE  = Path(__file__).parent

FONT_BOLD   = "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"
FONT_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf"
FONT_REG    = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"


def vtext(text: str, font, color=(191, 155, 48, 255), pad: int = 6) -> Image.Image:
    """Texto horizontal → rotacionado 90° (lê de baixo para cima)."""
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bb = dummy.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    img = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((pad - bb[0], pad - bb[1]), text, font=font, fill=color)
    return img.rotate(90, expand=True)


def hline(draw: ImageDraw.Draw, x: int, y: int, w: int, thick: int = 2) -> None:
    draw.rectangle([x, y, x + w, y + thick], fill=GOLD)


def build() -> Image.Image:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        f_large = ImageFont.truetype(FONT_BOLD, 150)
        f_mid   = ImageFont.truetype(FONT_REG, 34)
        f_tag   = ImageFont.truetype(FONT_ITALIC, 22)
    except Exception:
        f_large = f_mid = f_tag = ImageFont.load_default()

    # ── "BARKLEY" vertical (bloco central-esquerdo) ───────────────────────
    bk = vtext("BARKLEY", f_large)
    bk_x = 60
    bk_y = (H - bk.height) // 2
    img.alpha_composite(bk, (bk_x, bk_y))

    # ── Linha ornamental à esquerda de BARKLEY ─────────────────────────────
    hline(draw, 20, H // 2 - 2, 34, 2)

    # ── Linha ornamental à direita de BARKLEY ─────────────────────────────
    right_edge = bk_x + bk.width + 8
    hline(draw, right_edge, H // 2 - 2, 20, 2)

    # ── "CIGAR" vertical (bloco à direita) ────────────────────────────────
    cg = vtext("CIGAR", f_mid)
    cg_x = bk_x + bk.width + 16
    cg_y = (H - cg.height) // 2
    img.alpha_composite(cg, (cg_x, cg_y))

    # ── Tagline vertical (bloco mais à direita) ───────────────────────────
    tg = vtext("The Art of Smoking Excellence", f_tag)
    tg_x = cg_x + cg.width + 10
    tg_y = (H - tg.height) // 2
    if tg_x + tg.width < W:
        img.alpha_composite(tg, (tg_x, tg_y))

    # ── Traço fino no topo e base do bloco BARKLEY ────────────────────────
    hline(draw, bk_x, bk_y - 6, bk.width, 1)
    hline(draw, bk_x, bk_y + bk.height + 4, bk.width, 1)

    return img


def main():
    logo = build()
    out = BASE / "logo_source.png"
    # Salvar com fundo branco para o extract_logo.py funcionar
    bg = Image.new("RGBA", logo.size, (255, 255, 255, 255))
    bg.alpha_composite(logo)
    bg.save(str(out), "PNG")
    print(f"Salvo: {out}  ({logo.width}x{logo.height})")


if __name__ == "__main__":
    main()
