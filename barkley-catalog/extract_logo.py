import sys
import numpy as np
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image

LOGO_PDF = Path(__file__).parent / "logo.pdf"
OUT_WHITE = Path(__file__).parent / "logo_white.png"
OUT_GOLD  = Path(__file__).parent / "logo_gold.png"
GOLD_RGB  = (191, 155, 48)
DPI       = 300


def smart_crop(rgba: np.ndarray) -> np.ndarray:
    """Crop to bounding box of non-transparent pixels."""
    alpha = rgba[:, :, 3]
    rows = np.any(alpha > 0, axis=1)
    cols = np.any(alpha > 0, axis=0)
    if not rows.any():
        raise ValueError("Imagem completamente transparente após conversão.")
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    return rgba[rmin:rmax + 1, cmin:cmax + 1]


def recolor(rgba: np.ndarray, target_rgb: tuple[int, int, int]) -> np.ndarray:
    """Replace color of all opaque pixels with target_rgb, keep alpha."""
    out = rgba.copy()
    mask = out[:, :, 3] > 0          # pixels não-transparentes
    out[mask, 0] = target_rgb[0]
    out[mask, 1] = target_rgb[1]
    out[mask, 2] = target_rgb[2]
    return out


def main() -> None:
    if not LOGO_PDF.exists():
        print(f"ERRO: {LOGO_PDF} não encontrado.")
        print("Coloque o logo.pdf na pasta barkley-catalog/ e execute novamente.")
        sys.exit(1)

    print(f"Convertendo {LOGO_PDF} @ {DPI} DPI...")
    pages = convert_from_path(str(LOGO_PDF), dpi=DPI, transparent=True)
    img = pages[0].convert("RGBA")

    arr = np.array(img)

    # Se vier sem canal alpha real (fundo branco), converte fundo branco → transparente
    if arr[:, :, 3].min() == 255:
        print("PDF sem transparência — convertendo fundo branco em transparente...")
        white_mask = (arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240)
        arr[white_mask, 3] = 0

    arr = smart_crop(arr)
    print(f"Tamanho após crop: {arr.shape[1]}x{arr.shape[0]} px")

    white_arr = recolor(arr, (255, 255, 255))
    Image.fromarray(white_arr).save(OUT_WHITE, "PNG")
    print(f"Salvo: {OUT_WHITE}")

    gold_arr = recolor(arr, GOLD_RGB)
    Image.fromarray(gold_arr).save(OUT_GOLD, "PNG")
    print(f"Salvo: {OUT_GOLD}")

    print("Concluído.")


if __name__ == "__main__":
    main()
