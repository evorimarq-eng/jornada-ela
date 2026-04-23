import sys
import numpy as np
from pathlib import Path
from PIL import Image

try:
    from pdf2image import convert_from_path
except ImportError:
    sys.exit("pdf2image não instalado.")

PDF_PATH = Path("logo.pdf")
WHITE = (255, 255, 255)
GOLD  = (191, 155, 48)

def pdf_to_image(pdf_path: Path, dpi: int = 300) -> Image.Image:
    pages = convert_from_path(str(pdf_path), dpi=dpi)
    if not pages:
        sys.exit("Nenhuma página encontrada no PDF.")
    return pages[0]

def smart_crop(img: Image.Image) -> Image.Image:
    """Crop to bounding box of non-transparent pixels."""
    rgba = img.convert("RGBA")
    arr  = np.array(rgba)
    alpha = arr[:, :, 3]
    rows  = np.any(alpha > 0, axis=1)
    cols  = np.any(alpha > 0, axis=0)
    if not rows.any():
        return rgba
    r0, r1 = np.where(rows)[0][[0, -1]]
    c0, c1 = np.where(cols)[0][[0, -1]]
    return Image.fromarray(arr[r0:r1+1, c0:c1+1])

def recolor(img: Image.Image, color: tuple[int, int, int]) -> Image.Image:
    """Replace every non-transparent pixel with `color`, keep alpha."""
    rgba = img.convert("RGBA")
    arr  = np.array(rgba, dtype=np.uint8)
    mask = arr[:, :, 3] > 0
    arr[mask, 0] = color[0]
    arr[mask, 1] = color[1]
    arr[mask, 2] = color[2]
    return Image.fromarray(arr)

def main():
    if not PDF_PATH.exists():
        sys.exit(f"Arquivo não encontrado: {PDF_PATH}\n"
                 "Coloque logo.pdf na mesma pasta e execute novamente.")

    print(f"Convertendo {PDF_PATH} → imagem (300 DPI)...")
    raw = pdf_to_image(PDF_PATH, dpi=300)

    # PDF pages come out as RGB; convert to RGBA so transparency is preserved
    if raw.mode != "RGBA":
        # Make white background transparent
        raw_rgba = raw.convert("RGBA")
        arr = np.array(raw_rgba, dtype=np.uint8)
        # Pixels that are almost white (background) become transparent
        white_mask = (arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240)
        arr[white_mask, 3] = 0
        raw = Image.fromarray(arr)

    print("Recortando área do logo...")
    cropped = smart_crop(raw)

    print("Salvando logo_white.png...")
    white_img = recolor(cropped, WHITE)
    white_img.save("logo_white.png")

    print("Salvando logo_gold.png...")
    gold_img = recolor(cropped, GOLD)
    gold_img.save("logo_gold.png")

    print(f"Concluído. Tamanho final: {cropped.size[0]}×{cropped.size[1]} px")

if __name__ == "__main__":
    main()
