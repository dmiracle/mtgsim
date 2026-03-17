from collections.abc import Callable
from pathlib import Path

import numpy as np
from PIL import Image

from mtgviz.rotation import get_image_paths


def compute_average_card(
    image_dir: Path,
    target_size: tuple[int, int] = (745, 1040),
    greyscale: bool = False,
    progress: Callable[[], None] | None = None,
) -> np.ndarray:
    """
    Compute average pixel values across all card images.

    Args:
        image_dir: Directory containing card images
        target_size: (width, height) to resize all images to
        greyscale: If True, convert to greyscale before averaging
        progress: Optional callback called after each image

    Returns:
        numpy array of shape (height, width, 3) for RGB or (height, width) for greyscale
    """
    images = get_image_paths(image_dir)

    if not images:
        raise ValueError(f"No images found in {image_dir}")

    width, height = target_size

    if greyscale:
        accumulator = np.zeros((height, width), dtype=np.float64)
    else:
        accumulator = np.zeros((height, width, 3), dtype=np.float64)

    for image_path in images:
        img = Image.open(image_path)
        img = img.resize(target_size, Image.Resampling.LANCZOS)

        if greyscale:
            img = img.convert("L")
        else:
            img = img.convert("RGB")

        accumulator += np.array(img, dtype=np.float64)

        if progress:
            progress()

    average = accumulator / len(images)
    return average


def save_average_card(
    average: np.ndarray,
    output_path: Path,
) -> None:
    """Save averaged pixel array as an image."""
    # Clip to valid range and convert to uint8
    clipped = np.clip(average, 0, 255).astype(np.uint8)

    if len(clipped.shape) == 2:
        img = Image.fromarray(clipped, mode="L")
    else:
        img = Image.fromarray(clipped, mode="RGB")

    img.save(output_path)
