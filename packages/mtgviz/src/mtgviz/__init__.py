from contextlib import contextmanager
from pathlib import Path
from time import perf_counter

import memray
import typer
from rich.progress import Progress

from mtgviz.average import compute_average_card, save_average_card
from mtgviz.ocr import get_image_files, run_ocr, scan_directory_to_json, scan_to_json
from mtgviz.rotation import (
    analyze_directory,
    apply_rotations,
    get_image_paths,
    write_report,
)

app = typer.Typer()


def percentile(data: list[float], p: float) -> float:
    """Calculate percentile of sorted data."""
    if not data:
        return 0.0
    k = (len(data) - 1) * p / 100
    f = int(k)
    c = f + 1 if f + 1 < len(data) else f
    return data[f] + (k - f) * (data[c] - data[f])


class PerfTimer:
    """Live performance timer that logs to file."""

    def __init__(self, log_path: Path | None):
        self.log_path = log_path
        self.start_time = perf_counter()
        self.timings: dict[str, list[float]] = {}
        if log_path:
            log_path.write_text(f"[{0:.3f}s] Performance log started\n")

    def log(self, message: str):
        if not self.log_path:
            return
        elapsed = perf_counter() - self.start_time
        line = f"[{elapsed:.3f}s] {message}"
        with self.log_path.open("a") as f:
            f.write(line + "\n")

    @contextmanager
    def time(self, label: str):
        start = perf_counter()
        self.log(f"{label}...")
        yield
        duration = perf_counter() - start
        if label not in self.timings:
            self.timings[label] = []
        self.timings[label].append(duration)
        self.log(f"{label} done ({duration:.3f}s)")

    def report(self) -> str:
        total = perf_counter() - self.start_time
        lines = [
            "",
            "Timing Report",
            f"{'Method':<20} | {'Count':>6} | {'25%':>8} | {'50%':>8} | {'75%':>8} | {'100%':>8} | {'Total':>8}",
            "-" * 85,
        ]
        for label, times in self.timings.items():
            times_sorted = sorted(times)
            count = len(times)
            p25 = percentile(times_sorted, 25)
            p50 = percentile(times_sorted, 50)
            p75 = percentile(times_sorted, 75)
            p100 = times_sorted[-1] if times_sorted else 0
            total_time = sum(times)
            lines.append(
                f"{label:<20} | {count:>6} | {p25:>7.3f}s | {p50:>7.3f}s | {p75:>7.3f}s | {p100:>7.3f}s | {total_time:>7.3f}s"
            )
        lines.append("-" * 85)
        lines.append(f"Total: {total:.3f}s")
        return "\n".join(lines)


@contextmanager
def maybe_profile(enabled: bool, output: Path):
    """Context manager for optional memray profiling."""
    if enabled:
        with memray.Tracker(output):
            yield
        typer.echo(f"Memory profile written to {output}")
        typer.echo(f"View with: uv run memray flamegraph {output}")
    else:
        yield


@app.command("rotate-report")
def rotate_report(
    directory: Path = typer.Argument(..., help="Directory containing card images"),
    output: Path = typer.Option(Path("rotation-report.html"), help="Output HTML file"),
    profile: bool = typer.Option(False, "--profile", help="Enable memory profiling"),
    timing_log: Path = typer.Option(None, "--timing-log", help="Write timing log to file"),
    workers: int = typer.Option(1, "--workers", "-j", help="Parallel workers (0=auto, 1=sequential)"),
) -> None:
    """Generate a rotation detection report for card images."""
    if not directory.exists():
        typer.echo(f"Directory not found: {directory}")
        raise typer.Exit(1)

    # Timing only works in sequential mode
    timer = PerfTimer(timing_log) if workers == 1 else PerfTimer(None)
    if timing_log and workers != 1:
        typer.echo("Note: --timing-log requires --workers 1 for per-method timing")

    profile_output = output.with_suffix(".bin")

    with maybe_profile(profile, profile_output):
        with timer.time("Load image paths"):
            images = get_image_paths(directory)
        timer.log(f"Found {len(images)} images")

        with Progress() as progress:
            task = progress.add_task("Analyzing images...", total=len(images))

            def on_progress(path: Path):
                progress.advance(task)

            results = analyze_directory(directory, progress=on_progress, timer=timer, workers=workers)

        with timer.time("Write report"):
            write_report(results, output)

    typer.echo(f"Report written to {output}")
    if timing_log and workers == 1:
        report = timer.report()
        typer.echo(report)
        with timing_log.open("a") as f:
            f.write(report + "\n")


@app.command("rotate-apply")
def rotate_apply(
    directory: Path = typer.Argument(..., help="Directory containing card images"),
    report: Path = typer.Option(Path("rotation-report.html"), help="Report file path"),
    profile: bool = typer.Option(False, "--profile", help="Enable memory profiling"),
    timing_log: Path = typer.Option(None, "--timing-log", help="Write timing log to file"),
    workers: int = typer.Option(1, "--workers", "-j", help="Parallel workers (0=auto, 1=sequential)"),
) -> None:
    """Apply 180° rotation to cards that need it based on OCR analysis."""
    if not directory.exists():
        typer.echo(f"Directory not found: {directory}")
        raise typer.Exit(1)

    # Timing only works in sequential mode
    timer = PerfTimer(timing_log) if workers == 1 else PerfTimer(None)
    if timing_log and workers != 1:
        typer.echo("Note: --timing-log requires --workers 1 for per-method timing")

    profile_output = report.with_suffix(".bin")

    with maybe_profile(profile, profile_output):
        with timer.time("Load image paths"):
            images = get_image_paths(directory)
        timer.log(f"Found {len(images)} images")

        with Progress() as progress:
            task = progress.add_task("Analyzing images...", total=len(images))

            def on_analyze(path: Path):
                progress.advance(task)

            results = analyze_directory(directory, progress=on_analyze, timer=timer, workers=workers)

        with timer.time("Write report"):
            write_report(results, report)

        typer.echo(f"Report written to {report}")

        needs_rotation = [r for r in results if r.needs_rotation]
        if not needs_rotation:
            typer.echo("No images need rotation.")
            if timing_log and workers == 1:
                rpt = timer.report()
                typer.echo(rpt)
                with timing_log.open("a") as f:
                    f.write(rpt + "\n")
            return

        with Progress() as progress:
            task = progress.add_task("Rotating images...", total=len(needs_rotation))

            def on_rotate(path: Path):
                progress.advance(task)

            count = apply_rotations(results, progress=on_rotate, timer=timer, workers=workers)

        typer.echo(f"Rotated {count} images")

    if timing_log and workers == 1:
        rpt = timer.report()
        typer.echo(rpt)
        with timing_log.open("a") as f:
            f.write(rpt + "\n")


@app.command("average-card")
def average_card(
    directory: Path = typer.Argument(..., help="Directory containing card images"),
    output: Path = typer.Option(Path("average-card"), help="Output base name (without extension)"),
    greyscale: bool = typer.Option(False, "--greyscale", "-g", help="Output greyscale instead of RGB"),
    width: int = typer.Option(745, "--width", help="Target width"),
    height: int = typer.Option(1040, "--height", help="Target height"),
) -> None:
    """Compute average pixel values across all card images."""
    import numpy as np

    if not directory.exists():
        typer.echo(f"Directory not found: {directory}")
        raise typer.Exit(1)

    images = get_image_paths(directory)

    with Progress() as progress:
        task = progress.add_task("Computing average...", total=len(images))
        average = compute_average_card(
            directory,
            target_size=(width, height),
            greyscale=greyscale,
            progress=lambda: progress.advance(task),
        )

    # Save numpy array
    array_path = output.with_suffix(".npy")
    np.save(array_path, average)
    typer.echo(f"Array saved to {array_path}")

    # Save image
    image_path = output.with_suffix(".png")
    save_average_card(average, image_path)
    typer.echo(f"Image saved to {image_path}")


@app.command("ocr")
def ocr(
    image: Path = typer.Argument(..., help="Path to image file"),
    border: bool = typer.Option(False, "--border", "-b", help="Add 15px white border"),
    filter: bool = typer.Option(False, "--filter", "-f", help="Remove short/non-word lines"),
    psm: int = typer.Option(1, "--psm", help="Tesseract page segmentation mode"),
) -> None:
    """Run OCR on an image and print extracted text."""
    if not image.exists():
        typer.echo(f"Image not found: {image}")
        raise typer.Exit(1)

    text = run_ocr(image, border=border, filter=filter, psm=psm)
    typer.echo(text)


@app.command("scan-json")
def scan_json(
    image: Path = typer.Argument(..., help="Path to image file"),
    border: bool = typer.Option(False, "--border", "-b", help="Add 15px white border"),
    filter: bool = typer.Option(False, "--filter", "-f", help="Remove short/non-word lines"),
    psm: int = typer.Option(1, "--psm", help="Tesseract page segmentation mode"),
    output: Path = typer.Option(None, "--output", "-o", help="Output JSON file (default: stdout)"),
) -> None:
    """Run OCR and output result as JSON with metadata."""
    if not image.exists():
        typer.echo(f"Image not found: {image}")
        raise typer.Exit(1)

    result = scan_to_json(image, border=border, filter=filter, psm=psm)
    if output:
        output.write_text(result)
        typer.echo(f"Written to {output}")
    else:
        typer.echo(result)


@app.command("scan-dir")
def scan_dir(
    directory: Path = typer.Argument(..., help="Directory containing images"),
    border: bool = typer.Option(False, "--border", "-b", help="Add 15px white border"),
    filter: bool = typer.Option(False, "--filter", "-f", help="Remove short/non-word lines"),
    psm: int = typer.Option(1, "--psm", help="Tesseract page segmentation mode"),
    limit: int = typer.Option(None, "--limit", "-n", help="Max number of images to scan"),
    output: Path = typer.Option(None, "--output", "-o", help="Output JSON file (default: stdout)"),
) -> None:
    """Scan all images in a directory and output JSON."""
    if not directory.exists():
        typer.echo(f"Directory not found: {directory}")
        raise typer.Exit(1)

    images = get_image_files(directory)
    if limit:
        images = images[:limit]

    with Progress() as progress:
        task = progress.add_task("Scanning images...", total=len(images))

        def on_progress(path: Path):
            progress.advance(task)

        result = scan_directory_to_json(
            directory, border=border, filter=filter, psm=psm, limit=limit, progress=on_progress
        )

    if output:
        output.write_text(result)
        typer.echo(f"Written to {output}")
    else:
        typer.echo(result)


def main() -> None:
    app()
