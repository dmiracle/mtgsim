"""CLI entry point for running the API server."""

import typer
import uvicorn

app = typer.Typer()


@app.command()
def main(
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug logging"),
    port: int = typer.Option(8001, "--port", "-p", help="Port to listen on"),
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind to"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload on code changes"),
):
    """Run the MTG API server."""
    import os

    if debug:
        os.environ["MTGSIM_DEBUG"] = "1"

    uvicorn.run(
        "mtgsim.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="debug" if debug else "info",
    )


if __name__ == "__main__":
    app()
