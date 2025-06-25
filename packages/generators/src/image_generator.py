from typing import Tuple
from PIL import Image, ImageDraw, ImageFont


def generate_image(text: str, size: Tuple[int, int] = (512, 512), background: str = "white") -> Image.Image:
    """Generate a simple image with the provided text."""
    img = Image.new("RGB", size, color=background)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    draw.text((10, 10), text, fill="black", font=font)
    return img
