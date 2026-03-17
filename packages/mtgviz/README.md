# mtgviz

Computer vision, OCR, and image analysis for Magic: The Gathering card images.

## Installation

```bash
uv sync
```

Requires tesseract OCR installed on system:
```bash
brew install tesseract  # macOS
```

## Commands

### Generate rotation report

Analyze card images and generate an HTML report showing which need 180° rotation:

```bash
uv run mtgviz rotate-report ~/path/to/images
```

### Apply rotations

Analyze and automatically rotate images that are upside down:

```bash
uv run mtgviz rotate-apply ~/path/to/images
```

### Parallel processing

Use `--workers` / `-j` for parallel analysis (significant speedup):

```bash
# Auto-detect CPU cores
uv run mtgviz rotate-report ~/path/to/images -j 0

# Use 4 workers
uv run mtgviz rotate-report ~/path/to/images -j 4
```

## Profiling

### Memory profiling with memray

Add `--profile` to generate a memray profile:

```bash
uv run mtgviz rotate-report ~/path/to/images --profile
```

This creates `rotation-report.bin`. View the profile:

```bash
# Interactive flamegraph (generates HTML)
uv run memray flamegraph rotation-report.bin
open memray-flamegraph-rotation-report.html

# Text summary
uv run memray summary rotation-report.bin

# Tree view
uv run memray tree rotation-report.bin

# Stats table
uv run memray stats rotation-report.bin
```

### Timing profiling

Add `--timing-log` to generate timing statistics:

```bash
uv run mtgviz rotate-report ~/path/to/images --timing-log timing.log
```

Prints a quartile report per method:

```
Timing Report
Method               |  Count |      25% |      50% |      75% |     100% |    Total
-------------------------------------------------------------------------------------
Image.open           |    100 |   0.012s |   0.015s |   0.018s |   0.045s |   1.523s
OCR                  |    200 |   0.892s |   1.023s |   1.156s |   2.341s | 205.432s
Image.rotate         |    100 |   0.002s |   0.003s |   0.003s |   0.008s |   0.312s
-------------------------------------------------------------------------------------
Total: 210.543s
```
