"""
Barkley Cigar — Catálogo PDF Premium
A4 Landscape (841 × 595 pt) · ReportLab canvas
"""

import random
import textwrap
import math
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.utils import ImageReader

# ── Caminhos ────────────────────────────────────────────────────────────────
BASE      = Path(__file__).parent
LOGO_W    = BASE / "logo_white.png"
LOGO_G    = BASE / "logo_gold.png"
OUT_PDF   = Path("/mnt/user-data/outputs/Barkley_Cigar_Catalogo_Final.pdf")

# ── Página ───────────────────────────────────────────────────────────────────
W, H = landscape(A4)   # 841.89 × 595.28 pt

# ── Paleta ───────────────────────────────────────────────────────────────────
BG       = HexColor("#0C0B09")
SURF1    = HexColor("#181610")
SURF2    = HexColor("#1E1C16")
GOLD     = HexColor("#BF9B30")
GOLD_BR  = HexColor("#D4AF50")
GOLD_LT  = HexColor("#E8D490")
TXT      = HexColor("#F6F2E8")
CREAM    = HexColor("#ECE8DC")
MIST     = HexColor("#6A6455")
SMOKE    = HexColor("#3A3830")


# ════════════════════════════════════════════════════════════════════════════
# HELPERS GLOBAIS
# ════════════════════════════════════════════════════════════════════════════

def set_alpha(c: canvas.Canvas, color: HexColor, alpha: float) -> Color:
    """Retorna Color com alpha; aplica fill e devolve."""
    r, g, b = color.red, color.green, color.blue
    return Color(r, g, b, alpha=alpha)


def grain_texture(c: canvas.Canvas, page_seed: int) -> None:
    """800 retângulos dourados minúsculos espalhados pela página."""
    rng = random.Random(page_seed * 7 + 13)
    c.saveState()
    for _ in range(800):
        x  = rng.uniform(0, W)
        y  = rng.uniform(0, H)
        rw = rng.uniform(1, 3)
        rh = rng.uniform(1, 3)
        a  = rng.uniform(0.01, 0.04)
        c.setFillColor(Color(GOLD.red, GOLD.green, GOLD.blue, alpha=a))
        c.rect(x, y, rw, rh, stroke=0, fill=1)
    c.restoreState()


def ghost_diagonals(c: canvas.Canvas, page_seed: int) -> None:
    """20 linhas diagonais em tom dourado ultra-suave."""
    rng = random.Random(page_seed * 3 + 7)
    c.saveState()
    for _ in range(20):
        x0 = rng.uniform(-100, W)
        y0 = rng.uniform(-100, H + 100)
        ang = rng.uniform(55, 70)
        length = rng.uniform(200, max(W, H) * 1.5)
        a  = rng.uniform(0.03, 0.08)
        ang_r = math.radians(ang)
        x1 = x0 + length * math.cos(ang_r)
        y1 = y0 + length * math.sin(ang_r)
        c.setStrokeColor(Color(GOLD.red, GOLD.green, GOLD.blue, alpha=a))
        c.setLineWidth(0.5)
        c.line(x0, y0, x1, y1)
    c.restoreState()


def page_watermark(c: canvas.Canvas, num: int) -> None:
    """Número da página em 280pt dourado fantasma — canto inferior esquerdo."""
    c.saveState()
    c.setFillColor(Color(GOLD.red, GOLD.green, GOLD.blue, alpha=0.025))
    c.setFont("Helvetica-Bold", 280)
    c.drawString(20, -40, str(num))
    c.restoreState()


def section_header_band(c: canvas.Canvas, section_name: str) -> None:
    """Faixa dourada 3px no topo + nome da seção em caps à direita."""
    c.saveState()
    c.setFillColor(GOLD)
    c.rect(0, H - 28, W, 3, stroke=0, fill=1)
    c.setFillColor(CREAM)
    c.setFont("Helvetica", 7)
    c.drawRightString(W - 16, H - 22, section_name.upper())
    c.restoreState()


def folio_footer(c: canvas.Canvas) -> None:
    """Linha dourada + rodapé centralizado."""
    c.saveState()
    footer_y = 18
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.5)
    c.line(30, footer_y + 10, W - 30, footer_y + 10)
    c.setFillColor(MIST)
    c.setFont("Helvetica", 6.5)
    c.drawCentredString(W / 2, footer_y, "BARKLEY CIGAR  ·  barkleycigar.com  ·  @barkley.oficial")
    c.restoreState()


def apply_global_fx(c: canvas.Canvas, page_num: int, section: str) -> None:
    """Aplica grain + diagonais + watermark + header + footer."""
    grain_texture(c, page_num)
    ghost_diagonals(c, page_num)
    page_watermark(c, page_num)
    section_header_band(c, section)
    folio_footer(c)


def draw_corner_marks(c: canvas.Canvas, x: float, y: float,
                      w: float, h: float, size: float = 20) -> None:
    """Desenha marcas em L nos 4 cantos de uma caixa."""
    c.saveState()
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    # BL
    c.line(x, y, x + size, y)
    c.line(x, y, x, y + size)
    # BR
    c.line(x + w, y, x + w - size, y)
    c.line(x + w, y, x + w, y + size)
    # TL
    c.line(x, y + h, x + size, y + h)
    c.line(x, y + h, x, y + h - size)
    # TR
    c.line(x + w, y + h, x + w - size, y + h)
    c.line(x + w, y + h, x + w, y + h - size)
    c.restoreState()


def draw_text_block(c: canvas.Canvas, text: str, x: float, y: float,
                    width: float, font: str, size: float,
                    color, leading: float = 0, char_width_est: float = 0.55) -> float:
    """Word-wrap manual. Retorna y final (após último baseline)."""
    if leading == 0:
        leading = size * 1.65
    chars_per_line = max(1, int(width / (size * char_width_est)))
    lines = []
    for para in text.split("\n"):
        if para.strip() == "":
            lines.append("")
        else:
            lines.extend(textwrap.wrap(para, chars_per_line) or [""])
    c.saveState()
    c.setFillColor(color)
    c.setFont(font, size)
    cur_y = y
    for line in lines:
        c.drawString(x, cur_y, line)
        cur_y -= leading
    c.restoreState()
    return cur_y


def draw_image_centered(c: canvas.Canvas, img_path: Path,
                        cx: float, cy: float, target_w: float,
                        alpha: float = 1.0) -> None:
    """Desenha imagem centralizada em (cx, cy) com largura target_w."""
    if not img_path.exists():
        return
    ir = ImageReader(str(img_path))
    iw, ih = ir.getSize()
    scale = target_w / iw
    tw = target_w
    th = ih * scale
    c.saveState()
    if alpha < 1.0:
        c.setFillAlpha(alpha)
    c.drawImage(str(img_path), cx - tw / 2, cy - th / 2, tw, th,
                mask="auto", preserveAspectRatio=True)
    c.restoreState()


def draw_spaced_string(c: canvas.Canvas, text: str, cx: float, y: float,
                       font: str, size: float, color,
                       spacing: float = 8.0, anchor: str = "center") -> None:
    """Desenha texto com espaçamento extra entre letras."""
    c.saveState()
    c.setFillColor(color)
    c.setFont(font, size)
    total_w = sum(c.stringWidth(ch, font, size) for ch in text)
    total_w += spacing * (len(text) - 1)
    if anchor == "center":
        x = cx - total_w / 2
    else:
        x = cx
    for ch in text:
        c.drawString(x, y, ch)
        x += c.stringWidth(ch, font, size) + spacing
    c.restoreState()


# ════════════════════════════════════════════════════════════════════════════
# PÁGINAS (esqueleto — conteúdo será adicionado iterativamente)
# ════════════════════════════════════════════════════════════════════════════

def draw_page1(c: canvas.Canvas) -> None:
    """Capa."""
    # Fundo
    c.setFillColor(BG)
    c.rect(0, 0, W, H, stroke=0, fill=1)

    apply_global_fx(c, 1, "Catálogo Oficial 2025")


def draw_page2(c: canvas.Canvas) -> None:
    """Sobre a Marca."""
    c.setFillColor(BG)
    c.rect(0, 0, W, H, stroke=0, fill=1)

    apply_global_fx(c, 2, "Sobre a Marca")


def draw_page3(c: canvas.Canvas) -> None:
    """Nossa Composição."""
    c.setFillColor(BG)
    c.rect(0, 0, W, H, stroke=0, fill=1)

    apply_global_fx(c, 3, "Nossa Composição")


def draw_page4(c: canvas.Canvas) -> None:
    """Linha de Produtos."""
    c.setFillColor(BG)
    c.rect(0, 0, W, H, stroke=0, fill=1)

    apply_global_fx(c, 4, "Linha de Produtos")


def draw_page5(c: canvas.Canvas) -> None:
    """Origem & Terroir."""
    c.setFillColor(BG)
    c.rect(0, 0, W, H, stroke=0, fill=1)

    apply_global_fx(c, 5, "Origem & Terroir")


def draw_page6(c: canvas.Canvas) -> None:
    """Encerramento."""
    c.setFillColor(BG)
    c.rect(0, 0, W, H, stroke=0, fill=1)

    apply_global_fx(c, 6, "Encerramento")


# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

def main() -> None:
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT_PDF), pagesize=(W, H))

    draw_page1(c); c.showPage()
    draw_page2(c); c.showPage()
    draw_page3(c); c.showPage()
    draw_page4(c); c.showPage()
    draw_page5(c); c.showPage()
    draw_page6(c); c.showPage()

    c.save()
    print(f"PDF salvo em: {OUT_PDF}")


if __name__ == "__main__":
    main()
