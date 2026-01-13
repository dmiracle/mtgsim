from pathlib import Path

import typer

from mtgviz.rotation import generate_report

app = typer.Typer()


@app.command("rotate-report")
def rotate_report(
    directory: Path = typer.Argument(..., help="Directory containing card images"),
    output: Path = typer.Option(Path("rotation-report.html"), help="Output HTML file"),
) -> None:
    """Generate a rotation detection report for card images."""
    if not directory.exists():
        typer.echo(f"Directory not found: {directory}")
        raise typer.Exit(1)

    typer.echo(f"Analyzing images in {directory}...")
    generate_report(directory, output)
    typer.echo(f"Report written to {output}")


def main() -> None:
    app()
