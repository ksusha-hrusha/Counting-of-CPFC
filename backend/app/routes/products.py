from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from app import db
from app.models import Product, CookingMethod
from app.services.off import search_off
from app.services.translate import translate_to_ru

products_bp = Blueprint("products", __name__)


def product_to_dict(p):
    return {
        "id": p.id,
        "off_id": p.off_id,
        "name": p.name_ru or p.name,
        "name_original": p.name,
        "calories": p.calories,
        "protein": p.protein,
        "fat": p.fat,
        "carbs": p.carbs,
        "unit": p.unit or 'g',
        "serving_weight": p.serving_weight,
        "is_custom": p.created_by is not None,
    }


def get_current_user_id():
    """Возвращает user_id если токен есть, иначе None."""
    try:
        verify_jwt_in_request(optional=True)
        return get_jwt_identity()
    except Exception:
        return None


@products_bp.get("/")
def search_products():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])

    user_id = get_current_user_id()

    # Ищем глобальные продукты (created_by IS NULL) + личные текущего пользователя
    query = Product.query.filter(
        (Product.name.ilike(f"%{q}%")) | (Product.name_ru.ilike(f"%{q}%"))
    ).filter(
        (Product.created_by == None) | (Product.created_by == user_id)
    ).limit(20)

    local = query.all()

    if local:
        return jsonify([product_to_dict(p) for p in local])

    # Иначе — Open Food Facts (только глобальный поиск)
    off_results = search_off(q)
    saved = []
    for item in off_results:
        existing = Product.query.filter_by(off_id=item["off_id"]).first() if item["off_id"] else None
        if existing:
            saved.append(existing)
            continue
        name_ru = translate_to_ru(item["name"])
        product = Product(
            off_id=item["off_id"] or None,
            name=item["name"],
            name_ru=name_ru,
            calories=item["calories"],
            protein=item["protein"],
            fat=item["fat"],
            carbs=item["carbs"],
            created_by=None,  # глобальный
        )
        db.session.add(product)
        saved.append(product)
    db.session.commit()
    return jsonify([product_to_dict(p) for p in saved])


@products_bp.get("/cooking-methods")
def get_cooking_methods():
    methods = CookingMethod.query.all()
    return jsonify([{"id": m.id, "name": m.name, "weight_coefficient": m.weight_coefficient} for m in methods])


@products_bp.get("/<product_id>")
def get_product(product_id):
    p = Product.query.get_or_404(product_id)
    return jsonify(product_to_dict(p))


@products_bp.post("/")
@jwt_required()
def create_custom_product():
    """Создать личный продукт пользователя."""
    user_id = get_jwt_identity()
    data = request.get_json()
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Укажите название"}), 400

    # Проверяем дубликат среди личных продуктов этого пользователя
    existing = Product.query.filter(
        Product.name_ru.ilike(name),
        Product.created_by == user_id
    ).first()
    if existing:
        return jsonify(product_to_dict(existing)), 200

    product = Product(
        name=name,
        name_ru=name,
        calories=float(data.get("calories", 0)),
        protein=float(data.get("protein", 0)),
        fat=float(data.get("fat", 0)),
        carbs=float(data.get("carbs", 0)),
        unit=data.get("unit", "g"),
        serving_weight=float(data["serving_weight"]) if data.get("serving_weight") else None,
        created_by=user_id,
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product_to_dict(product)), 201


@products_bp.get("/my")
@jwt_required()
def my_products():
    """Список личных продуктов пользователя."""
    user_id = get_jwt_identity()
    products = Product.query.filter_by(created_by=user_id).order_by(Product.name_ru).all()
    return jsonify([product_to_dict(p) for p in products])


@products_bp.delete("/<product_id>")
@jwt_required()
def delete_custom_product(product_id):
    """Удалить личный продукт."""
    user_id = get_jwt_identity()
    p = Product.query.filter_by(id=product_id, created_by=user_id).first_or_404()
    db.session.delete(p)
    db.session.commit()
    return jsonify({"ok": True})
