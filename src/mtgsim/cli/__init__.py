import typer

from .card_commands import card_app
from .db_commands import db_app
from .mtgjson_commands import mtgjson_app

app = typer.Typer(help="MTG card simulator CLI")

# Add sub-apps
app.add_typer(card_app, name="card")
app.add_typer(db_app, name="db")
app.add_typer(mtgjson_app, name="mtgjson")


def main():
    app()


if __name__ == "__main__":
    main()
