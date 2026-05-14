import os
import uuid
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Dish
from app.services.calculator import calc_dish

users_bp = Blueprint("users", __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "avatars")
ALLOWED_EXT = {"png", "jpg", "jpeg", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


def user_to_dict(user):
    return {
        "id": user.id,
        "username": user.username,
        "avatar": f"/api/users/{user.id}/avatar" if user.avatar else None,
        "created_at": user.created_at.isoformat(),
    }


@users_bp.get("/me")
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    data = user_to_dict(user)
    data["email"] = user.email
    return jsonify(data)


@users_bp.post("/me/avatar")
@jwt_required()
def upload_avatar():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    if "avatar" not in request.files:
        return jsonify({"error": "Файл не найден"}), 400
    file = request.files["avatar"]
    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Допустимые форматы: jpg, png, webp"}), 400

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Удаляем старый аватар
    if user.avatar:
        old_path = os.path.join(UPLOAD_FOLDER, user.avatar)
        if os.path.exists(old_path):
            os.remove(old_path)

    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = f"{user_id}_{uuid.uuid4().hex[:8]}.{ext}"
    file.save(os.path.join(UPLOAD_FOLDER, filename))

    user.avatar = filename
    db.session.commit()
    return jsonify({"avatar": f"/api/users/{user_id}/avatar"})


@users_bp.get("/<user_id>/avatar")
def get_avatar(user_id):
    user = User.query.get_or_404(user_id)
    if not user.avatar:
        return jsonify({"error": "Нет аватара"}), 404
    return send_from_directory(UPLOAD_FOLDER, user.avatar)


@users_bp.get("/<user_id>")
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user_to_dict(user))
