from flask import Blueprint, request, jsonify
from app import socketio

scale_bp = Blueprint("scale", __name__)


@scale_bp.route("/push", methods=["POST"])
def push_weight():
    """
    ESP8266/ESP32 шлёт сюда POST с JSON: { "weight": 123.4 }
    Сервер пробрасывает значение всем подключённым браузерам через WebSocket.
    """
    data = request.get_json(silent=True)
    if not data or "weight" not in data:
        return jsonify({"error": "weight required"}), 400

    weight = round(float(data["weight"]), 1)
    socketio.emit("weight_update", {"weight": weight})
    return jsonify({"ok": True, "weight": weight})
