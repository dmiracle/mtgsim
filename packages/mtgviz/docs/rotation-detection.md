# Card Rotation Detection

Detect if a scanned Magic card is upside down and rotate 180° if needed.

## Approach: OCR Confidence Comparison

Run OCR on the image in both orientations (0° and 180°) and compare text detection confidence. The correct orientation will produce higher confidence scores and more recognizable text.

### Why OCR-based?

- MTG cards have consistent text regions (card name, type line, rules text)
- No training data or custom models required
- Works across all card frames and sets
- Simple to implement and debug

### Algorithm

1. Load image
2. Run OCR on original orientation, record confidence score
3. Rotate image 180°
4. Run OCR on rotated image, record confidence score
5. Keep the orientation with higher confidence
6. Save corrected image

### Libraries

- **Pillow** - image loading and rotation
- **pytesseract** or **easyocr** - OCR engine

pytesseract is lighter weight and sufficient for confidence comparison. EasyOCR has better accuracy but heavier dependencies (PyTorch).

### Confidence Metric

Tesseract returns per-word confidence (0-100). We can use:
- Mean confidence across all detected words
- Sum of confidences (rewards more text detected)
- Count of high-confidence words (>60)

Recommend: **sum of confidences** - balances quantity and quality of detected text.

### Interface

```python
def detect_rotation(image_path: str) -> int:
    """Returns 0 or 180 indicating degrees of rotation needed."""

def fix_rotation(image_path: str, output_path: str) -> bool:
    """Rotates image if needed, saves to output_path. Returns True if rotated."""
```

### CLI

```
mtgviz rotate-report <directory> --output report.md
```

Generates a markdown report with:
- Thumbnail of each card (embedded or linked)
- Detected rotation (0° or 180°)
- Confidence scores for both orientations
- Recommendation (keep or rotate)

### Report Format

```markdown
# Card Rotation Report

## image001.jpg

![image001](path/to/image001.jpg)

| Orientation | Confidence |
|-------------|------------|
| 0°          | 2450       |
| 180°        | 890        |

**Detected rotation:** 0° (keep as-is)

---

## image002.jpg

![image002](path/to/image002.jpg)

| Orientation | Confidence |
|-------------|------------|
| 0°          | 320        |
| 180°        | 2100       |

**Detected rotation:** 180° (needs rotation)
```

### Future: Apply Rotations

Once report is reviewed, a separate command can apply the fixes:

```
mtgviz rotate-apply <directory> [--output-dir DIR]
```
