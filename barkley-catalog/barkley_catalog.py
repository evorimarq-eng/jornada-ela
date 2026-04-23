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
                        alpha: float = 1.0, max_h: float = None) -> None:
    """Desenha imagem centralizada em (cx, cy) respeitando target_w e max_h."""
    if not img_path.exists():
        return
    ir = ImageReader(str(img_path))
    iw, ih = ir.getSize()
    scale_w = target_w / iw
    scale_h = (max_h / ih) if max_h else scale_w
    scale   = min(scale_w, scale_h)
    tw = iw * scale
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
    LEFT_W = W * 0.44
    RIGHT_X = LEFT_W + 2        # após a barra dourada
    RIGHT_W = W - RIGHT_X

    # ── Fundos dos painéis ───────────────────────────────────────────────
    c.setFillColor(SURF1)
    c.rect(0, 0, LEFT_W, H, stroke=0, fill=1)
    c.setFillColor(BG)
    c.rect(RIGHT_X, 0, RIGHT_W, H, stroke=0, fill=1)

    # ── Texturas globais (sobre os painéis) ──────────────────────────────
    apply_global_fx(c, 1, "Catálogo Oficial 2025")

    # ── Barra dourada divisória ──────────────────────────────────────────
    c.setFillColor(GOLD)
    c.rect(LEFT_W, 0, 2, H, stroke=0, fill=1)

    # ── Ghost logo dourado (painel direito, levemente maior, 6% opacity) ─
    ghost_w = RIGHT_W * 0.60
    draw_image_centered(c, LOGO_G,
                        RIGHT_X + RIGHT_W / 2, H / 2,
                        ghost_w, alpha=0.06, max_h=H * 0.75)

    # ── Logo branco centralizado no painel direito ───────────────────────
    logo_w = RIGHT_W * 0.55
    draw_image_centered(c, LOGO_W,
                        RIGHT_X + RIGHT_W / 2, H / 2,
                        logo_w, alpha=1.0, max_h=H * 0.75)

    # ── Corner marks no painel direito ──────────────────────────────────
    draw_corner_marks(c, RIGHT_X + 12, 12, RIGHT_W - 24, H - 24, size=20)

    # ── Painel esquerdo — conteúdo ───────────────────────────────────────
    left_cx = LEFT_W / 2

    # "BARKLEY" rotacionado 90° — ocupa a faixa central-vertical do painel
    # A 68pt, "BARKLEY" tem ~310pt de largura → rotacionado fica ~310pt alto
    # Faixa y: H/2 ± 155  →  aprox 142 a 452
    c.saveState()
    c.setFillColor(GOLD_LT)
    c.setFont("Helvetica-Bold", 68)
    c.translate(left_cx + 6, H / 2)
    c.rotate(90)
    barkley_w = c.stringWidth("BARKLEY", "Helvetica-Bold", 68)
    c.drawString(-barkley_w / 2, 0, "BARKLEY")
    c.restoreState()

    # "CIGAR" com tracking — zona inferior do painel (abaixo da faixa do BARKLEY)
    cigar_y = 112
    draw_spaced_string(c, "CIGAR", left_cx, cigar_y,
                       "Helvetica", 18, TXT, spacing=8.0)

    # Tagline em itálico — imediatamente abaixo de CIGAR
    tagline_y = cigar_y - 18
    c.saveState()
    c.setFillColor(MIST)
    c.setFont("Helvetica-Oblique", 9)
    tagline = "The Art of Smoking Excellence"
    tw = c.stringWidth(tagline, "Helvetica-Oblique", 9)
    c.drawString(left_cx - tw / 2, tagline_y, tagline)
    c.restoreState()

    # Badge inferior do painel esquerdo
    badge_h = 22
    badge_y = 32
    badge_pad = 14
    c.saveState()
    c.setFillColor(SMOKE)
    c.rect(badge_pad, badge_y, LEFT_W - badge_pad * 2, badge_h, stroke=0, fill=1)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.5)
    c.rect(badge_pad, badge_y, LEFT_W - badge_pad * 2, badge_h, stroke=1, fill=0)
    c.setFillColor(CREAM)
    c.setFont("Helvetica", 7)
    badge_txt = "@barkley.oficial  ·  barkleycigar.com"
    bw = c.stringWidth(badge_txt, "Helvetica", 7)
    c.drawString(left_cx - bw / 2, badge_y + 8, badge_txt)
    c.restoreState()

    # Faixa de info no topo esquerdo
    c.saveState()
    c.setFillColor(MIST)
    c.setFont("Helvetica", 6)
    c.drawString(16, H - 22, "CATÁLOGO OFICIAL 2025")
    c.restoreState()


def draw_page2(c: canvas.Canvas) -> None:
    """Sobre a Marca."""
    c.setFillColor(BG)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    apply_global_fx(c, 2, "Sobre a Marca")

    MARGIN_L = 44
    MARGIN_R = 44
    TEXT_W   = W * 0.62          # coluna de texto (painel esquerdo)
    TOP_Y    = H - 52

    # ── Headline impacto ────────────────────────────────────────────────
    c.saveState()
    c.setFont("Helvetica-Bold", 36)
    c.setFillColor(TXT)
    c.drawString(MARGIN_L, TOP_Y, "Autenticidade não se declara.")
    c.setFillColor(GOLD_BR)
    c.drawString(MARGIN_L, TOP_Y - 44, "Se sente em cada trago.")
    c.restoreState()

    # ── Parágrafos ──────────────────────────────────────────────────────
    p1 = ("A Barkley Cigar nasceu de uma convicção simples e inabalável: o charuto é uma das "
          "experiências mais genuínas que um ser humano pode vivenciar. Cada folha carrega décadas "
          "de tradição, cada blend é uma declaração de intenção, e cada acender é um ritual que "
          "merece ser celebrado com o que há de mais autêntico.")
    p2 = ("Nossa marca foi construída sobre o compromisso de oferecer charutos que honram a tradição "
          "cubana — tabacos Criollo e Corojo envolvidos por uma sedosa capa Habano — sem abrir mão de "
          "uma identidade própria, ousada e reconhecível. A Barkley não imita. A Barkley cria.")
    p3 = ("Ser a marca mais autêntica do mercado nacional e internacional não é uma meta — é uma "
          "escolha diária. A escolha de nunca ceder ao ordinário.")

    y = TOP_Y - 100
    for para in (p1, p2, p3):
        y = draw_text_block(c, para, MARGIN_L, y, TEXT_W,
                            "Helvetica", 8.5, CREAM, leading=14)
        y -= 10

    # ── Linha divisória antes dos pilares ────────────────────────────────
    pillar_top = H * 0.40
    c.saveState()
    c.setStrokeColor(SMOKE)
    c.setLineWidth(0.5)
    c.line(MARGIN_L, pillar_top + 6, W - MARGIN_R, pillar_top + 6)
    c.restoreState()

    # ── 3 Pilares ────────────────────────────────────────────────────────
    pillars = [
        ("01", "AUTENTICIDADE", "O charuto como expressão genuína de quem você é."),
        ("02", "EXCELÊNCIA",    "Cada detalhe, do blend ao acabamento, é inegociável."),
        ("03", "RITUAL",        "Acender um Barkley é um momento que merece ser celebrado."),
    ]
    pillar_w = (W - MARGIN_L - MARGIN_R) / 3
    for i, (num, title, body) in enumerate(pillars):
        px = MARGIN_L + i * pillar_w

        # Número ghost
        c.saveState()
        c.setFillColor(Color(GOLD.red, GOLD.green, GOLD.blue, alpha=0.15))
        c.setFont("Helvetica-Bold", 48)
        c.drawString(px, pillar_top - 38, num)
        c.restoreState()

        # Título
        c.saveState()
        c.setFillColor(TXT)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(px, pillar_top - 52, title)
        c.restoreState()

        # Linha separadora
        c.saveState()
        c.setStrokeColor(SMOKE)
        c.setLineWidth(0.5)
        c.line(px, pillar_top - 58, px + pillar_w - 16, pillar_top - 58)
        c.restoreState()

        # Texto
        draw_text_block(c, body, px, pillar_top - 72, pillar_w - 16,
                        "Helvetica", 7.5, CREAM, leading=12)

    # ── Logo dourado pequeno — margem direita, meio da página ─────────────
    logo_right_cx = W - 70
    draw_image_centered(c, LOGO_G, logo_right_cx, H / 2 - 10, 60, alpha=0.85, max_h=150)


def draw_page3(c: canvas.Canvas) -> None:
    """Nossa Composição."""
    c.setFillColor(BG)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    apply_global_fx(c, 3, "Nossa Composição")

    MARGIN = 36
    TOP_Y  = H - 50

    # ── Headline ────────────────────────────────────────────────────────
    c.saveState()
    c.setFont("Helvetica-Bold", 38)
    c.setFillColor(TXT)
    c.drawString(MARGIN, TOP_Y, "O blend que")
    c.setFillColor(GOLD)
    c.drawString(MARGIN, TOP_Y - 46, "nos define.")
    c.restoreState()

    # ── Parágrafo intro ──────────────────────────────────────────────────
    intro = ("Cada Barkley é construído a partir de uma seleção rigorosa de três tabacos que, juntos, "
             "criam um blend único — complexo o suficiente para surpreender, equilibrado o suficiente "
             "para nunca cansar.")
    draw_text_block(c, intro, MARGIN, TOP_Y - 104, W * 0.70,
                    "Helvetica", 8, CREAM, leading=13)

    # ── 3 Cards ──────────────────────────────────────────────────────────
    CARD_Y      = H * 0.44       # topo dos cards
    CARD_H      = H * 0.38
    CARD_GAP    = 10
    CARD_W      = (W - MARGIN * 2 - CARD_GAP * 2) / 3

    cards = [
        ("01", "CRIOLLO",       "Semente Nativa · desde 1930",
         "Um dos tabacos cubanos originais, utilizado na fabricação de charutos desde 1930. "
         "Foi um dos tabacos cubanos originais que surgiram na época de Colombo e significa "
         "semente nativa. Confere ao blend complexidade histórica e profundidade de sabor."),
        ("02", "COROJO",        "Resistência & Equilíbrio",
         "Foi o substituto direto do tabaco Criollo devido a sua resistência, elasticidade, "
         "doçura e picância, e hoje é utilizado já renovado por diversas marcas. É o coração "
         "pulsante do blend Barkley."),
        ("03", "CAPA HABANO",   "O toque final",
         "A capa é o cartão de visitas do charuto — e a Habano é a mais nobre delas. Sedosa "
         "ao toque, uniforme na queima, elegante na aparência. O acabamento que faz toda a diferença."),
    ]

    for i, (num, title, subtitle, body) in enumerate(cards):
        cx = MARGIN + i * (CARD_W + CARD_GAP)

        # Fundo SURF1
        c.saveState()
        c.setFillColor(SURF1)
        c.rect(cx, CARD_Y - CARD_H, CARD_W, CARD_H, stroke=0, fill=1)
        c.restoreState()

        # Glow dourado — 4 bordas concêntricas, alpha decrescente
        for gi, ga in enumerate([0.06, 0.04, 0.02, 0.01]):
            off = gi * 1.5
            c.saveState()
            c.setStrokeColor(Color(GOLD.red, GOLD.green, GOLD.blue, alpha=ga))
            c.setLineWidth(1)
            c.rect(cx - off, CARD_Y - CARD_H - off,
                   CARD_W + off * 2, CARD_H + off * 2, stroke=1, fill=0)
            c.restoreState()

        # Corner marks
        draw_corner_marks(c, cx + 4, CARD_Y - CARD_H + 4, CARD_W - 8, CARD_H - 8, size=10)

        # Número ghost
        c.saveState()
        c.setFillColor(Color(GOLD.red, GOLD.green, GOLD.blue, alpha=0.20))
        c.setFont("Helvetica-Bold", 32)
        c.drawString(cx + 10, CARD_Y - 36, num)
        c.restoreState()

        # Linha divisória
        c.saveState()
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.5)
        c.line(cx + 10, CARD_Y - 44, cx + CARD_W - 10, CARD_Y - 44)
        c.restoreState()

        # Título
        c.saveState()
        c.setFillColor(TXT)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(cx + 10, CARD_Y - 60, title)
        c.restoreState()

        # Subtítulo
        c.saveState()
        c.setFillColor(MIST)
        c.setFont("Helvetica-Oblique", 7)
        c.drawString(cx + 10, CARD_Y - 74, subtitle)
        c.restoreState()

        # Corpo
        draw_text_block(c, body, cx + 10, CARD_Y - 90,
                        CARD_W - 20, "Helvetica", 7.5, CREAM, leading=12)

    # ── Faixa final full-width ────────────────────────────────────────────
    FAIXA_H = 26
    FAIXA_Y = 30
    c.saveState()
    c.setFillColor(SURF2)
    c.rect(0, FAIXA_Y, W, FAIXA_H, stroke=0, fill=1)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.5)
    c.rect(0, FAIXA_Y, W, FAIXA_H, stroke=1, fill=0)
    c.setFillColor(CREAM)
    c.setFont("Helvetica-Oblique", 7.5)
    faixa_txt = ("Com uma linha extensa de bitolas para todos os gostos, a Barkley Cigar tem "
                 "com certeza o charuto ideal para cada momento e cada paladar.")
    ftw = c.stringWidth(faixa_txt, "Helvetica-Oblique", 7.5)
    c.drawString(W / 2 - ftw / 2, FAIXA_Y + 9, faixa_txt)
    c.restoreState()


def draw_page4(c: canvas.Canvas) -> None:
    """Linha de Produtos."""
    c.setFillColor(BG)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    apply_global_fx(c, 4, "Linha de Produtos")

    MARGIN = 36
    TOP_Y  = H - 50

    # ── Headline ────────────────────────────────────────────────────────
    c.saveState()
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(TXT)
    c.drawString(MARGIN, TOP_Y, "Cinco expressões.")
    c.setFillColor(GOLD)
    c.drawString(MARGIN, TOP_Y - 34, "Uma filosofia.")
    c.restoreState()

    # ── 5 Linhas de produto ──────────────────────────────────────────────
    products = [
        ("01", "ENTRY",         "PERLA",
         "4×40 · 30 min",
         "A porta de entrada ao universo Barkley. Compacta e elegante, entrega todo o sabor do "
         "blend em uma experiência rápida e intensa — ideal para uma pausa ou para o primeiro "
         "contato com a nossa linha."),
        ("02", "SIGNATURE",     "PROJETO VESPEIRO CAÑONAZO",
         "150×52 · 75 min",
         "Uma declaração de intenção. Impressiona pela construção robusta e pela riqueza de sabores "
         "que se desenvolvem ao longo de 75 minutos. Para quem aprecia profundidade sem abrir mão "
         "de suavidade."),
        ("03", "CLASSIC",       "PROTECTOR WIDE CHURCHILL",
         "124×50 · 55 min",
         "O clássico revisitado pela Barkley. O formato que atravessou gerações, executado com o "
         "rigor e a personalidade que definem nossa marca. Equilibrado, encorpado e absolutamente "
         "memorável."),
        ("04", "PREMIUM",       "DYNAMITE",
         "7×70 · 80 min a 2h",
         "O nome diz tudo. Um charuto monumental de calibre 70 que explode em sabores ao longo de "
         "até duas horas de pura satisfação. Para os que buscam a experiência máxima."),
        ("05", "ULTRA PREMIUM", "WE ARE BARKLEY SUPREMO MADURO",
         "55×58 · 127×23mm · 70–85 min",
         "O ápice da linha. Com capa Maduro de cor escura e sabor naturalmente adocicado, o Supremo "
         "Maduro carrega no nome a identidade da marca: We Are Barkley. Autenticidade, excelência e "
         "ritual em estado puro."),
    ]

    # Tag pill colors
    tag_colors = {
        "ENTRY":         (SMOKE,   TXT),
        "SIGNATURE":     (SURF2,   CREAM),
        "CLASSIC":       (SURF2,   CREAM),
        "PREMIUM":       (Color(GOLD.red, GOLD.green, GOLD.blue, alpha=0.30), GOLD_LT),
        "ULTRA PREMIUM": (GOLD,    BG),
    }

    ROW_H    = (H - 130) / 5     # altura de cada linha
    ROWS_TOP = TOP_Y - 80        # início das linhas

    for i, (num, tag, name, bitola, desc) in enumerate(products):
        ry     = ROWS_TOP - i * ROW_H
        # fundo alternado
        bg_col = SURF1 if i % 2 == 0 else BG
        c.saveState()
        c.setFillColor(bg_col)
        c.rect(0, ry - ROW_H, W, ROW_H, stroke=0, fill=1)
        c.restoreState()

        # Barra dourada esquerda
        c.saveState()
        c.setFillColor(GOLD)
        c.rect(0, ry - ROW_H, 3, ROW_H, stroke=0, fill=1)
        c.restoreState()

        row_mid = ry - ROW_H / 2

        # Número ghost
        c.saveState()
        c.setFillColor(Color(GOLD.red, GOLD.green, GOLD.blue, alpha=0.18))
        c.setFont("Helvetica-Bold", 36)
        c.drawString(12, row_mid - 14, num)
        c.restoreState()

        # Tag pill
        pill_x = 58
        pill_y = row_mid - 7
        pill_h = 14
        tag_bg, tag_fg = tag_colors.get(tag, (SMOKE, TXT))
        pill_w = c.stringWidth(tag, "Helvetica-Bold", 6) + 14
        c.saveState()
        c.setFillColor(tag_bg)
        c.roundRect(pill_x, pill_y, pill_w, pill_h, 3, stroke=0, fill=1)
        c.setFillColor(tag_fg)
        c.setFont("Helvetica-Bold", 6)
        c.drawString(pill_x + 7, pill_y + 4, tag)
        c.restoreState()

        # Nome do produto
        c.saveState()
        c.setFillColor(TXT)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(pill_x, row_mid + 10, name)
        c.restoreState()

        # Bitola + tempo
        c.saveState()
        c.setFillColor(MIST)
        c.setFont("Helvetica", 7)
        c.drawString(pill_x, row_mid - 24, bitola)
        c.restoreState()

        # Descrição com word-wrap
        draw_text_block(c, desc, W * 0.45, row_mid + 8,
                        W * 0.50, "Helvetica", 7, CREAM, leading=11)


def draw_page5(c: canvas.Canvas) -> None:
    """Origem & Terroir."""
    c.setFillColor(BG)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    apply_global_fx(c, 5, "Origem & Terroir")

    MARGIN   = 44
    COL_GAP  = 20
    COL_W    = (W - MARGIN * 2 - COL_GAP) / 2
    TOP_Y    = H - 50

    # ── Headline ────────────────────────────────────────────────────────
    c.saveState()
    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(TXT)
    c.drawString(MARGIN, TOP_Y, "O solo que transforma")
    c.setFillColor(GOLD)
    c.drawString(MARGIN, TOP_Y - 32, "tabaco em arte.")
    c.restoreState()

    # ── "NICARÁGUA" com tracking ──────────────────────────────────────────
    nic_y = TOP_Y - 72
    draw_spaced_string(c, "NICARÁGUA", MARGIN, nic_y,
                       "Helvetica-Bold", 8, GOLD_BR, spacing=3.0, anchor="left")

    # ── 2 Colunas de texto ────────────────────────────────────────────────
    col_text_y = nic_y - 18
    col1_txt = ("Desde 2016, a Nicarágua é a maior produtora de tabaco para charuto no mercado "
                "mundial e o 2º maior produtor de charutos em unidades, sendo República Dominicana "
                "a primeira colocada com aproximadamente 44% da produção mundial, Nicarágua em "
                "segundo e Cuba em terceiro. Estima-se uma produção anual de charutos premium em "
                "torno de 400 milhões de unidades somente na Nicarágua, passando de 1,2 bilhões de "
                "unidades se juntarmos os demais países produtores.")
    col2_txt = ("Somente nos EUA no ano de 2022, deram entrada 456 milhões de unidades provindos do "
                "mercado produtor de charutos premium. O mercado de charutos vem crescendo ano após "
                "ano com projeção de 11,5% nos próximos 5 anos, sendo o maior o mercado americano e "
                "acompanhado com o que mais cresce o mercado asiático.")

    draw_text_block(c, col1_txt, MARGIN, col_text_y, COL_W,
                    "Helvetica", 8, CREAM, leading=13)
    draw_text_block(c, col2_txt, MARGIN + COL_W + COL_GAP, col_text_y, COL_W,
                    "Helvetica", 8, CREAM, leading=13)

    # ── Faixa de stats ────────────────────────────────────────────────────
    STATS_H  = 52
    STATS_Y  = H * 0.34
    c.saveState()
    c.setFillColor(SURF1)
    c.rect(0, STATS_Y, W, STATS_H, stroke=0, fill=1)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.5)
    c.line(0, STATS_Y + STATS_H, W, STATS_Y + STATS_H)
    c.restoreState()

    stats = [
        ("Nº1",    "Maior produtora de tabaco"),
        ("400M+",  "Unidades premium/ano"),
        ("+11,5%", "Crescimento 5 anos"),
        ("1,2Bi",  "Mercado global"),
        ("456M",   "Importados EUA 2022"),
    ]
    stat_w = W / len(stats)
    for i, (num, label) in enumerate(stats):
        sx = i * stat_w + stat_w / 2
        c.saveState()
        c.setFillColor(GOLD_BR)
        c.setFont("Helvetica-Bold", 14)
        nw = c.stringWidth(num, "Helvetica-Bold", 14)
        c.drawString(sx - nw / 2, STATS_Y + 28, num)
        c.setFillColor(MIST)
        c.setFont("Helvetica", 6)
        lw = c.stringWidth(label, "Helvetica", 6)
        c.drawString(sx - lw / 2, STATS_Y + 14, label)
        c.restoreState()

        # Separador vertical (exceto após o último)
        if i < len(stats) - 1:
            c.saveState()
            c.setStrokeColor(SMOKE)
            c.setLineWidth(0.5)
            c.line((i + 1) * stat_w, STATS_Y + 8, (i + 1) * stat_w, STATS_Y + STATS_H - 8)
            c.restoreState()

    # ── "JALAPA" com tracking ─────────────────────────────────────────────
    jal_y = STATS_Y - 22
    draw_spaced_string(c, "JALAPA", MARGIN, jal_y,
                       "Helvetica-Bold", 8, GOLD_BR, spacing=3.0, anchor="left")

    # ── Texto Jalapa ──────────────────────────────────────────────────────
    jalapa_txt = ("O tabaco Barkley tem sua origem nas regiões produtoras da Nicarágua, cujos solos "
                  "negros, arenosos e vulcânicos proporcionam ao crescimento do tabaco propriedades "
                  "diferentes dependendo de sua zona de plantio. Jalapa entrega um tabaco com notas "
                  "doces, folhas grandes, lisas e sabores complexos. As folhas de Capa chegam a ser "
                  "até 4 vezes maiores do que o tabaco para Capote e Miolo.")
    draw_text_block(c, jalapa_txt, MARGIN, jal_y - 14, W - MARGIN * 2,
                    "Helvetica", 8, CREAM, leading=13)


def draw_page6(c: canvas.Canvas) -> None:
    """Encerramento."""
    c.setFillColor(BG)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    apply_global_fx(c, 6, "Encerramento")

    cx = W / 2

    # ── Logo branco — terço superior, altura 22% da página ───────────────
    # Reduzido de 35% → 22% para liberar espaço abaixo
    logo_h_target = H * 0.22
    if LOGO_W.exists():
        ir = ImageReader(str(LOGO_W))
        iw, ih = ir.getSize()
        scale  = logo_h_target / ih
        lw     = iw * scale
        lh     = logo_h_target
        logo_y = H * 0.70          # bottom da imagem — logo vai de 70% a 92% da altura
        c.saveState()
        c.drawImage(str(LOGO_W), cx - lw / 2, logo_y, lw, lh,
                    mask="auto", preserveAspectRatio=True)
        c.restoreState()

    # ── "BARKLEY" ────────────────────────────────────────────────────────
    barkley_y = H * 0.63
    c.saveState()
    c.setFillColor(TXT)
    c.setFont("Helvetica-Bold", 60)
    bw = c.stringWidth("BARKLEY", "Helvetica-Bold", 60)
    c.drawString(cx - bw / 2, barkley_y, "BARKLEY")
    c.restoreState()

    # ── "CIGAR" com tracking ──────────────────────────────────────────────
    cigar_y = barkley_y - 28
    draw_spaced_string(c, "CIGAR", cx, cigar_y,
                       "Helvetica", 14, TXT, spacing=8.0)

    # ── Tagline ───────────────────────────────────────────────────────────
    tag_y = cigar_y - 20
    c.saveState()
    c.setFillColor(MIST)
    c.setFont("Helvetica-Oblique", 9)
    tagline = "The Art of Smoking Excellence"
    tw = c.stringWidth(tagline, "Helvetica-Oblique", 9)
    c.drawString(cx - tw / 2, tag_y, tagline)
    c.restoreState()

    # ── Grid 2×2 de cards de contato ─────────────────────────────────────
    CARD_W   = W * 0.20
    CARD_H   = 62           # reduzido de 72 para ganhar espaço vertical
    CARD_GAP = 14
    GRID_W   = CARD_W * 2 + CARD_GAP
    GRID_X   = cx - GRID_W / 2
    GRID_Y   = tag_y - CARD_H - 20

    contacts = [
        ("@",   "@barkley.oficial",         "Siga-nos. Faça parte da\ncomunidade Barkley."),
        ("●",   "R. Mascarenhas Camelo, 792","Sorocaba · São Paulo · Brasil"),
        ("▶",   "Todo o Brasil",             "Charutos premium até onde\nvocê estiver."),
        ("◆",   "barkleycigar.com",          "Conheça toda a linha online."),
    ]

    for i, (icon, title, body) in enumerate(contacts):
        col = i % 2
        row = i // 2
        kx  = GRID_X + col * (CARD_W + CARD_GAP)
        ky  = GRID_Y - row * (CARD_H + 10)

        # Fundo
        c.saveState()
        c.setFillColor(SURF1)
        c.rect(kx, ky, CARD_W, CARD_H, stroke=0, fill=1)
        c.setStrokeColor(SMOKE)
        c.setLineWidth(0.5)
        c.rect(kx, ky, CARD_W, CARD_H, stroke=1, fill=0)
        c.restoreState()

        pad = 10
        # Ícone
        c.saveState()
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(kx + pad, ky + CARD_H - pad - 14, icon)
        c.restoreState()

        # Título
        c.saveState()
        c.setFillColor(TXT)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(kx + pad, ky + CARD_H - pad - 28, title)
        c.restoreState()

        # Corpo
        draw_text_block(c, body, kx + pad, ky + CARD_H - pad - 40,
                        CARD_W - pad * 2, "Helvetica", 6.5, CREAM, leading=10)

    # ── Frase de encerramento ─────────────────────────────────────────────
    closing_w  = W * 0.70
    # GRID_Y é o bottom da 1ª linha de cards; 2ª linha: GRID_Y - (CARD_H + 10)
    closing_y  = GRID_Y - (CARD_H + 10) - 20
    closing_txt = ("Seja bem-vindo ao universo Barkley. Cada charuto que você acende é uma extensão "
                   "de quem você é — uma declaração de bom gosto, de presença e de autenticidade. "
                   "Obrigado por escolher o melhor.")
    closing_x = cx - closing_w / 2
    c.saveState()
    c.setFillColor(CREAM)
    c.setFont("Helvetica-Oblique", 7.5)
    chars = max(1, int(closing_w / (7.5 * 0.52)))
    lines = textwrap.wrap(closing_txt, chars)
    for line in lines:
        lw = c.stringWidth(line, "Helvetica-Oblique", 7.5)
        c.drawString(cx - lw / 2, closing_y, line)
        closing_y -= 12
    c.restoreState()

    # ── Faixa dourada no rodapé ───────────────────────────────────────────
    FAIXA_H = 22
    c.saveState()
    c.setFillColor(GOLD)
    c.rect(0, 0, W, FAIXA_H, stroke=0, fill=1)
    c.setFillColor(BG)
    c.setFont("Helvetica-Bold", 7)
    footer_txt = "@barkley.oficial  ·  barkleycigar.com  ·  Sorocaba  ·  SP  ·  Brasil"
    ftw = c.stringWidth(footer_txt, "Helvetica-Bold", 7)
    c.drawString(cx - ftw / 2, 8, footer_txt)
    c.restoreState()


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
