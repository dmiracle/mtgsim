import json
import re
from dataclasses import asdict, dataclass
from functools import cache
from pathlib import Path

import pytesseract
from PIL import Image, ImageOps

DICT_PATH = Path("/usr/share/dict/words")

_scan_counter = 0


@cache
def load_dictionary() -> set[str]:
    """Load system dictionary as lowercase word set."""
    if not DICT_PATH.exists():
        return set()
    return {word.strip().lower() for word in DICT_PATH.read_text().splitlines()}


def has_dict_word(line: str) -> bool:
    """Check if line contains at least one dictionary word."""
    words = re.findall(r"[a-zA-Z]+", line)
    dictionary = load_dictionary()
    if not dictionary:
        return any(len(w) >= 2 for w in words)
    return any(w.lower() in dictionary for w in words)


def filter_lines(text: str) -> str:
    """Filter out lines <3 chars or without dictionary words."""
    lines = []
    for line in text.splitlines():
        if len(line) < 3:
            continue
        if not has_dict_word(line):
            continue
        lines.append(line)
    return "\n".join(lines)


@dataclass
class OcrOptions:
    psm: int = 1
    border: bool = False
    filter: bool = False


@dataclass
class ImageMetadata:
    width: int
    height: int
    format: str | None
    mode: str
    file_size: int


@dataclass
class ScanResult:
    id: int
    image_path: str
    text: str
    options: OcrOptions
    metadata: ImageMetadata


def run_ocr(
    image_path: Path,
    border: bool = False,
    filter: bool = False,
    psm: int = 1,
) -> str:
    """Run pytesseract OCR on an image and return the extracted text."""
    image = Image.open(image_path)
    if border:
        image = ImageOps.expand(image, border=15, fill="white")
    text = pytesseract.image_to_string(image, config=f"--psm {psm}")
    if filter:
        text = filter_lines(text)
    return text


def scan_image(
    image_path: Path,
    border: bool = False,
    filter: bool = False,
    psm: int = 1,
) -> ScanResult:
    """Run OCR and return ScanResult with metadata."""
    global _scan_counter
    _scan_counter += 1

    image = Image.open(image_path)
    metadata = ImageMetadata(
        width=image.width,
        height=image.height,
        format=image.format,
        mode=image.mode,
        file_size=image_path.stat().st_size,
    )

    options = OcrOptions(psm=psm, border=border, filter=filter)
    text = run_ocr(image_path, border=border, filter=filter, psm=psm)

    return ScanResult(
        id=_scan_counter,
        image_path=str(image_path.resolve()),
        text=text,
        options=options,
        metadata=metadata,
    )


def scan_to_json(
    image_path: Path,
    border: bool = False,
    filter: bool = False,
    psm: int = 1,
) -> str:
    """Run OCR and return result as JSON with metadata."""
    result = scan_image(image_path, border=border, filter=filter, psm=psm)
    return json.dumps(asdict(result), indent=2)


def get_image_files(directory: Path) -> list[Path]:
    """Get all image files from a directory."""
    extensions = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".gif"}
    return sorted(p for p in directory.iterdir() if p.suffix.lower() in extensions)


def scan_directory(
    directory: Path,
    border: bool = False,
    filter: bool = False,
    psm: int = 1,
    limit: int | None = None,
    progress: callable = None,
) -> list[ScanResult]:
    """Scan all images in a directory and return results."""
    images = get_image_files(directory)
    if limit:
        images = images[:limit]

    results = []
    for image_path in images:
        result = scan_image(image_path, border=border, filter=filter, psm=psm)
        results.append(result)
        if progress:
            progress(image_path)

    return results


def scan_directory_to_json(
    directory: Path,
    border: bool = False,
    filter: bool = False,
    psm: int = 1,
    limit: int | None = None,
    progress: callable = None,
) -> str:
    """Scan all images in a directory and return JSON."""
    results = scan_directory(directory, border, filter, psm, limit, progress)
    return json.dumps([asdict(r) for r in results], indent=2)
