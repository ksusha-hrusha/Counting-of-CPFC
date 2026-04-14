from app import create_app, db
from app.seed import seed_cooking_methods, seed_egg_unit
import click

app = create_app()


@app.cli.command("seed")
def seed():
    """Заполнить БД начальными данными."""
    with app.app_context():
        seed_cooking_methods()
        seed_egg_unit()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
