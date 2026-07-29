import typer

from .booster_commands import booster_app
from .card_commands import card, extract
from .db_commands import db_app
from .deck_commands import deck_app
from .domain_commands import domain_app
from .image_commands import images_app
from .mtgjson_commands import mtgjson_app

app = typer.Typer(help="MTG card simulator CLI")

# Add sub-apps
app.add_typer(booster_app, name="booster")
app.add_typer(db_app, name="db")
app.add_typer(deck_app, name="deck")
app.add_typer(domain_app, name="domain")
app.add_typer(images_app, name="images")
app.add_typer(mtgjson_app, name="mtgjson")

# Import commands from card_app to register them with the main app
# In Typer, if we want them at the top level, we can just use @app.command() in those files
# but since they are already decorated with @app.command() in their respective files
# if we want them at the top level of this app, we should either import them or use app.command() here.
# Actually, the plan was:
# cli/__init__.py: CLI app setup, registers subcommands
# card_commands.py: card, extract commands


app.command()(card)
app.command()(extract)


def main():
    app()


if __name__ == "__main__":
    main()
