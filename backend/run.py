# gevent monkey-patch MUST run before anything else imports stdlib socket/ssl/select
from gevent import monkey
monkey.patch_all()

import psycopg  # noqa: E402  (psycopg3 has gevent-aware async, but ensure import after patch)

from app import create_app, db, socketio  # noqa: E402
from app.seed import seed_cooking_methods, seed_egg_unit  # noqa: E402

app = create_app()


@app.cli.command("seed")
def seed():
    """Заполнить БД начальными данными."""
    with app.app_context():
        seed_cooking_methods()
        seed_egg_unit()


if __name__ == "__main__":
    # Только для локальной разработки вне Docker
    socketio.run(app, debug=True, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
