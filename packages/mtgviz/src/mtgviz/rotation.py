from dataclasses import dataclass
from pathlib import Path

import pytesseract
from PIL import Image


@dataclass
class RotationResult:
    image_path: Path
    confidence_0: float
    confidence_180: float
    detected_rotation: int  # 0 or 180

    @property
    def needs_rotation(self) -> bool:
        return self.detected_rotation == 180


def get_ocr_confidence(image: Image.Image) -> float:
    """Run OCR and return sum of word confidences."""
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    confidences = [c for c in data["conf"] if c > 0]
    return sum(confidences)


def detect_rotation(image_path: Path) -> RotationResult:
    """Detect if image needs 180° rotation based on OCR confidence."""
    image = Image.open(image_path)

    confidence_0 = get_ocr_confidence(image)

    rotated = image.rotate(180)
    confidence_180 = get_ocr_confidence(rotated)

    detected = 180 if confidence_180 > confidence_0 else 0

    return RotationResult(
        image_path=image_path,
        confidence_0=confidence_0,
        confidence_180=confidence_180,
        detected_rotation=detected,
    )


def generate_report(image_dir: Path, output_path: Path) -> None:
    """Generate HTML report for all images in directory."""
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
    images = sorted(p for p in image_dir.iterdir() if p.suffix.lower() in image_extensions)

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

    for image_path in images:
        result = detect_rotation(image_path)

        status = "needs rotation" if result.needs_rotation else "keep as-is"
        card_class = "card needs-rotation" if result.needs_rotation else "card"
        status_class = "status rotate" if result.needs_rotation else "status keep"

        html += f"""
    <div class="{card_class}">
        <h2>{image_path.name}</h2>
        <img src="file://{image_path.absolute()}" alt="{image_path.name}">
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
