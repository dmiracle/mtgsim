from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

import pytesseract
from PIL import Image

if TYPE_CHECKING:
    from contextlib import AbstractContextManager


class Timer(Protocol):
    def time(self, label: str) -> "AbstractContextManager": ...
    def log(self, message: str) -> None: ...


@dataclass
class RotationResult:
    image_path: Path
    confidence_0: float
    confidence_180: float
    detected_rotation: int  # 0 or 180

    @property
    def needs_rotation(self) -> bool:
        return self.detected_rotation == 180


def get_ocr_confidence(image: Image.Image, timer: Timer | None = None) -> float:
    """Run OCR and return sum of word confidences."""
    if timer:
        with timer.time("OCR"):
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    else:
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    confidences = [c for c in data["conf"] if c > 0]
    return sum(confidences)


def detect_rotation(image_path: Path, timer: Timer | None = None) -> RotationResult:
    """Detect if image needs 180° rotation based on OCR confidence."""
    if timer:
        with timer.time("Image.open"):
            image = Image.open(image_path)
    else:
        image = Image.open(image_path)

    confidence_0 = get_ocr_confidence(image, timer)

    if timer:
        with timer.time("Image.rotate"):
            rotated = image.rotate(180)
    else:
        rotated = image.rotate(180)

    confidence_180 = get_ocr_confidence(rotated, timer)

    detected = 180 if confidence_180 > confidence_0 else 0

    return RotationResult(
        image_path=image_path,
        confidence_0=confidence_0,
        confidence_180=confidence_180,
        detected_rotation=detected,
    )


def get_image_paths(image_dir: Path) -> list[Path]:
    """Get sorted list of image paths in directory."""
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
    return sorted(p for p in image_dir.iterdir() if p.suffix.lower() in image_extensions)


def analyze_directory(
    image_dir: Path,
    progress: Callable[[Path], None] | None = None,
    timer: Timer | None = None,
    workers: int = 1,
) -> list[RotationResult]:
    """Analyze all images in directory and return rotation results."""
    images = get_image_paths(image_dir)

    if workers == 1:
        results = []
        for image_path in images:
            results.append(detect_rotation(image_path, timer))
            if progress:
                progress(image_path)
        return results

    # Parallel execution (timer not supported across processes)
    results = []
    with ProcessPoolExecutor(max_workers=workers if workers > 0 else None) as executor:
        futures = {executor.submit(detect_rotation, img, None): img for img in images}
        for future in as_completed(futures):
            results.append(future.result())
            if progress:
                progress(futures[future])

    # Sort by original path order
    path_order = {p: i for i, p in enumerate(images)}
    results.sort(key=lambda r: path_order[r.image_path])
    return results


def rotate_single(image_path: Path) -> Path:
    """Rotate a single image 180° and save it."""
    image = Image.open(image_path)
    rotated = image.rotate(180)
    rotated.save(image_path)
    return image_path


def apply_rotations(
    results: list[RotationResult],
    progress: Callable[[Path], None] | None = None,
    timer: Timer | None = None,
    workers: int = 1,
) -> int:
    """Apply 180° rotation to images that need it. Returns count of rotated images."""
    to_rotate = [r.image_path for r in results if r.needs_rotation]

    if not to_rotate:
        return 0

    if workers == 1:
        for image_path in to_rotate:
            if timer:
                with timer.time("Image.open"):
                    image = Image.open(image_path)
                with timer.time("Image.rotate"):
                    rotated = image.rotate(180)
                with timer.time("Image.save"):
                    rotated.save(image_path)
            else:
                rotate_single(image_path)
            if progress:
                progress(image_path)
        return len(to_rotate)

    # Parallel execution
    with ProcessPoolExecutor(max_workers=workers if workers > 0 else None) as executor:
        futures = {executor.submit(rotate_single, p): p for p in to_rotate}
        for future in as_completed(futures):
            future.result()
            if progress:
                progress(futures[future])

    return len(to_rotate)


def write_report(results: list[RotationResult], output_path: Path) -> None:
    """Write HTML report from rotation results."""
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Card Rotation Report</title>
    <style>
        body { font-family: system-ui, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .card { border: 1px solid #ccc; padding: 20px; margin: 20px 0; border-radius: 8px; }
        .card.needs-rotation { border-color: #e74c3c; background: #fdf2f2; }
        .card img { max-width: 300px; height: auto; }
        table { border-collapse: collapse; margin: 10px 0; }
        th, td { border: 1px solid #ccc; padding: 8px 16px; text-align: left; }
        .status { font-weight: bold; margin-top: 10px; }
        .status.rotate { color: #e74c3c; }
        .status.keep { color: #27ae60; }
    </style>
</head>
<body>
    <h1>Card Rotation Report</h1>
"""

    for result in results:
        status = "needs rotation" if result.needs_rotation else "keep as-is"
        card_class = "card needs-rotation" if result.needs_rotation else "card"
        status_class = "status rotate" if result.needs_rotation else "status keep"

        html += f"""
    <div class="{card_class}">
        <h2>{result.image_path.name}</h2>
        <img src="file://{result.image_path.absolute()}" alt="{result.image_path.name}">
        <table>
            <tr><th>Orientation</th><th>Confidence</th></tr>
            <tr><td>0°</td><td>{result.confidence_0:.0f}</td></tr>
            <tr><td>180°</td><td>{result.confidence_180:.0f}</td></tr>
        </table>
        <p class="{status_class}">Detected rotation: {result.detected_rotation}° ({status})</p>
    </div>
"""

    html += """
</body>
</html>
"""
    output_path.write_text(html)
