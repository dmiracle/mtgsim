# Parallelization Strategy

## Bottleneck Analysis

Based on timing data, OCR is the dominant cost (~95% of runtime). Each image requires 2 OCR calls (0° and 180°). OCR is CPU-bound (tesseract).

| Method       | Time % | Bound |
|--------------|--------|-------|
| OCR          | ~95%   | CPU   |
| Image.open   | ~2%    | I/O   |
| Image.rotate | ~1%    | CPU   |
| Image.save   | ~2%    | I/O   |

## Strategy: Process Pool

Use `concurrent.futures.ProcessPoolExecutor` to parallelize image analysis across CPU cores.

### Why ProcessPoolExecutor?

- OCR is CPU-bound → multiprocessing beats threading (GIL)
- Each image is independent → embarrassingly parallel
- Built into Python stdlib → no new dependencies
- Clean API with futures

### Implementation

```python
from concurrent.futures import ProcessPoolExecutor, as_completed

def analyze_directory_parallel(
    image_dir: Path,
    workers: int | None = None,  # None = cpu_count()
    progress: Callable | None = None,
) -> list[RotationResult]:
    images = get_image_paths(image_dir)
    results = []

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(detect_rotation, img): img for img in images}

        for future in as_completed(futures):
            results.append(future.result())
            if progress:
                progress(futures[future])

    return results
```

### CLI Changes

Add `--workers` flag:

```
mtgviz rotate-report ~/images --workers 4
mtgviz rotate-report ~/images --workers 0  # auto (cpu_count)
```

### Expected Speedup

| Workers | Speedup (theoretical) |
|---------|----------------------|
| 1       | 1x (baseline)        |
| 2       | ~1.9x                |
| 4       | ~3.7x                |
| 8       | ~7x                  |

Actual speedup depends on:
- Number of CPU cores
- Memory bandwidth
- Tesseract's internal parallelism

### Considerations

1. **Memory**: Each worker loads images independently. With large images, memory usage scales with worker count.

2. **Progress tracking**: `as_completed` returns results out of order. Progress bar still works but results need sorting.

3. **Timing**: Per-process timing won't aggregate to main process. Timing report would show wall-clock totals only in parallel mode.

4. **Error handling**: One failed image shouldn't kill the batch. Wrap in try/except, collect errors.

### Alternative: Batch OCR

Tesseract supports multi-page input. Could batch images into a single tesseract call, but loses per-image confidence granularity.

### Recommendation

Start with `ProcessPoolExecutor` at `--workers 0` (auto). Simple to implement, good speedup, no new dependencies.
