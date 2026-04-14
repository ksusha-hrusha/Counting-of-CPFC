from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app import db
from app.models import User
from app.services.mail import send_reset_email
import bcrypt
import secrets
from datetime import datetime, timezone, timedelta

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json()
    if not data or not all(k in data for k in ("username", "email", "password")):
        return jsonify({"error": "Заполните все поля"}), 400
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email уже зарегистрирован"}), 409
    hashed = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt()).decode()
    user = User(username=data["username"], email=data["email"], password=hashed)
    db.session.add(user)
    db.session.commit()
    token = create_access_token(identity=user.id)
    return jsonify({"token": token, "user": {"id": user.id, "username": user.username, "email": user.email}}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json()
    if not data or not all(k in data for k in ("email", "password")):
        return jsonify({"error": "Заполните все поля"}), 400
    user = User.query.filter_by(email=data["email"]).first()
    if not user or not bcrypt.checkpw(data["password"].encode(), user.password.encode()):
        return jsonify({"error": "Неверный email или пароль"}), 401
    token = create_access_token(identity=user.id)
    return jsonify({"token": token, "user": {"id": user.id, "username": user.username, "email": user.email}})


@auth_bp.post("/forgot-password")
def forgot_password():
    data = request.get_json()
    email = data.get("email", "").strip()
    if not email:
        return jsonify({"error": "Укажите email"}), 400

    user = User.query.filter_by(email=email).first()
    # Не раскрываем существует ли пользователь
    if user:
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_exp = datetime.now(timezone.utc) + timedelta(hours=1)
        db.session.commit()
        try:
            send_reset_email(user.email, token)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Ошибка отправки письма: {str(e)}"}), 500

    return jsonify({"message": "Если такой email зарегистрирован, письмо отправлено"})


@auth_bp.post("/reset-password")
def reset_password():
    data = request.get_json()
    token = data.get("token", "").strip()
    new_password = data.get("password", "")

    if not token or not new_password:
        return jsonify({"error": "Неверный запрос"}), 400
    if len(new_password) < 6:
        return jsonify({"error": "Пароль должен быть не менее 6 символов"}), 400

    user = User.query.filter_by(reset_token=token).first()
    if not user:
        return jsonify({"error": "Ссылка недействительна"}), 400
    if user.reset_token_exp < datetime.now(timezone.utc):
        return jsonify({"error": "Ссылка истекла. Запросите новую."}), 400

    user.password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    user.reset_token = None
    user.reset_token_exp = None
    db.session.commit()

    return jsonify({"message": "Пароль успешно изменён"})
