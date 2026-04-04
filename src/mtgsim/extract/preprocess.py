"""Image preprocessing for card scan pipeline.

Normalizes uploaded card images before sending to extraction backends.
Uses Pillow for rotation correction, contrast enhancement, and resizing.
"""

import io

from PIL import Image, ImageEnhance, ImageOps

# Max dimension for the long edge — keeps API payload reasonable
# without losing detail needed for text recognition
MAX_DIMENSION = 2048

# JPEG quality for re-encoded output
JPEG_QUALITY = 85


def preprocess_card_image(data: bytes, mime_type: str) -> tuple[bytes, str]:
    """Preprocess a card image for extraction.

    Applies:
    1. EXIF orientation correction (rotation from camera metadata)
    2. Downscale if larger than MAX_DIMENSION
    3. Light contrast enhancement

    Args:
        data: Raw image bytes.
        mime_type: MIME type of the input image.

    Returns:
        Tuple of (processed_bytes, output_mime_type). Output is always JPEG.
    """
    img = Image.open(io.BytesIO(data))

    # 1. Apply EXIF rotation so the card is right-side-up
    img = ImageOps.exif_transpose(img)

    # 2. Convert to RGB (strips alpha, handles palette images)
    if img.mode != "RGB":
        img = img.convert("RGB")

    # 3. Downscale if needed
    img = _constrain_size(img, MAX_DIMENSION)

    # 4. Boost contrast slightly — helps with washed-out phone photos
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.2)

    # 5. Encode as JPEG
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=JPEG_QUALITY)
    return buf.getvalue(), "image/jpeg"


def _constrain_size(img: Image.Image, max_dim: int) -> Image.Image:
    """Downscale image so the longest edge is at most max_dim pixels."""
    w, h = img.size
    if max(w, h) <= max_dim:
        return img
    scale = max_dim / max(w, h)
    new_size = (int(w * scale), int(h * scale))
    return img.resize(new_size, Image.LANCZOS)
