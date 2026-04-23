"""
Extrai logo Barkley de PDF ou PNG e gera logo_white.png e logo_gold.png.
Aceita: logo.pdf  OU  logo_source.png (PNG com fundo branco)
"""

import sys
import numpy as np
from pathlib import Path
from PIL import Image

BASE      = Path(__file__).parent
LOGO_PDF  = BASE / "logo.pdf"
LOGO_PNG  = BASE / "logo_source.png"
OUT_WHITE = BASE / "logo_white.png"
OUT_GOLD  = BASE / "logo_gold.png"
GOLD_RGB  = (191, 155, 48)
DPI       = 300


def remove_white_bg(arr: np.ndarray, threshold: int = 240) -> np.ndarray:
    """Converte pixels quase-brancos em transparentes."""
    out = arr.copy()
    white_mask = (
        (out[:, :, 0] > threshold) &
        (out[:, :, 1] > threshold) &
        (out[:, :, 2] > threshold)
    )
    out[white_mask, 3] = 0
    return out


def smart_crop(rgba: np.ndarray) -> np.ndarray:
    """Crop para bounding box dos pixels não-transparentes."""
    alpha = rgba[:, :, 3]
    rows = np.any(alpha > 0, axis=1)
    cols = np.any(alpha > 0, axis=0)
    if not rows.any():
        raise ValueError("Imagem completamente transparente após conversão.")
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    return rgba[rmin:rmax + 1, cmin:cmax + 1]


def recolor(rgba: np.ndarray, target_rgb: tuple[int, int, int]) -> np.ndarray:
    """Pinta todos os pixels opacos com target_rgb, preserva alpha."""
    out = rgba.copy()
    mask = out[:, :, 3] > 0
    out[mask, 0] = target_rgb[0]
    out[mask, 1] = target_rgb[1]
    out[mask, 2] = target_rgb[2]
    return out


def load_source() -> np.ndarray:
    """Carrega de logo.pdf ou logo_source.png, retorna array RGBA."""
    if LOGO_PDF.exists():
        from pdf2image import convert_from_path
        print(f"Convertendo {LOGO_PDF} @ {DPI} DPI...")
        pages = convert_from_path(str(LOGO_PDF), dpi=DPI, transparent=True)
        img = pages[0].convert("RGBA")
        arr = np.array(img)
        if arr[:, :, 3].min() == 255:
            print("PDF sem canal alpha — removendo fundo branco...")
            arr = remove_white_bg(arr)
        return arr

    if LOGO_PNG.exists():
        print(f"Carregando {LOGO_PNG}...")
        img = Image.open(str(LOGO_PNG)).convert("RGBA")
        arr = np.array(img)
        # PNG com fundo branco sólido
        if arr[:, :, 3].min() == 255:
            print("PNG sem transparência — removendo fundo branco...")
            arr = remove_white_bg(arr)
        return arr

    print("ERRO: nenhum arquivo fonte encontrado.")
    print(f"  Esperado: {LOGO_PDF}  OU  {LOGO_PNG}")
    sys.exit(1)


def main() -> None:
    arr = load_source()
    arr = smart_crop(arr)
    print(f"Tamanho após crop: {arr.shape[1]}x{arr.shape[0]} px")

    Image.fromarray(recolor(arr, (255, 255, 255))).save(OUT_WHITE, "PNG")
    print(f"Salvo: {OUT_WHITE}")

    Image.fromarray(recolor(arr, GOLD_RGB)).save(OUT_GOLD, "PNG")
    print(f"Salvo: {OUT_GOLD}")

    print("Concluído.")


if __name__ == "__main__":
    main()
