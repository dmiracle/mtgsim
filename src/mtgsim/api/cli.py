"""CLI entry point for running the API server."""

import uvicorn


def main():
    """Run the MTG API server."""
    uvicorn.run(
        "mtgsim.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
