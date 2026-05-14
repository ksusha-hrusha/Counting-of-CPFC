from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
socketio = SocketIO()


def create_app():
    app = Flask(__name__)

    db_url = os.getenv("DATABASE_URL", "")
    # psycopg3 требует postgresql+psycopg:// вместо postgresql://
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret")

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    allowed_origins = [
        "http://localhost:5173",
        "http://localhost",
        "https://nutricalc.silaeder.space",
    ]
    CORS(app, resources={r"/api/*": {"origins": allowed_origins}})
    socketio.init_app(app, cors_allowed_origins=allowed_origins, async_mode="gevent")

    from app.routes.auth import auth_bp
    from app.routes.products import products_bp
    from app.routes.dishes import dishes_bp
    from app.routes.catalog import catalog_bp
    from app.routes.calculate import calculate_bp
    from app.routes.users import users_bp
    from app.routes.scale import scale_bp
    from app.routes.diary import diary_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(products_bp, url_prefix="/api/products")
    app.register_blueprint(dishes_bp, url_prefix="/api/dishes")
    app.register_blueprint(catalog_bp, url_prefix="/api/catalog")
    app.register_blueprint(calculate_bp, url_prefix="/api/calculate")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(scale_bp, url_prefix="/api/scale")
    app.register_blueprint(diary_bp, url_prefix="/api/diary")

    return app
