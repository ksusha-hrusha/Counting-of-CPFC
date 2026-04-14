from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Dish, DishIngredient, User
from app.services.calculator import calc_dish
from app.routes.dishes import dish_to_dict

catalog_bp = Blueprint("catalog", __name__)


def dish_with_author(dish):
    d = dish_to_dict(dish, with_nutrition=True)
    if dish.owner:
        d["author"] = {
            "id": dish.owner.id,
            "username": dish.owner.username,
            "avatar": f"/api/users/{dish.owner.id}/avatar" if dish.owner.avatar else None,
        }
    else:
        d["author"] = None
    return d


@catalog_bp.get("/")
def list_catalog():
    q = request.args.get("q", "").strip()
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    query = Dish.query.filter_by(is_public=True)
    if q:
        query = query.filter(Dish.name.ilike(f"%{q}%"))
    dishes = query.order_by(Dish.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return jsonify([dish_with_author(d) for d in dishes])


@catalog_bp.get("/<dish_id>")
def get_catalog_dish(dish_id):
    dish = Dish.query.filter_by(id=dish_id, is_public=True).first_or_404()
    return jsonify(dish_with_author(dish))


@catalog_bp.post("/<dish_id>/copy")
@jwt_required()
def copy_dish(dish_id):
    """Копирует публичное блюдо в профиль текущего пользователя."""
    user_id = get_jwt_identity()
    source = Dish.query.filter_by(id=dish_id, is_public=True).first_or_404()
    copy = Dish(
        user_id=user_id,
        name=source.name + " (копия)",
        description=source.description,
        category=source.category,
        servings=source.servings,
        is_public=False,
        cooking_method_id=source.cooking_method_id,
    )
    db.session.add(copy)
    db.session.flush()
    for ing in source.ingredients:
        db.session.add(DishIngredient(
            dish_id=copy.id,
            product_id=ing.product_id,
            nested_dish_id=ing.nested_dish_id,
            weight_raw=ing.weight_raw,
            cooking_method_id=ing.cooking_method_id,
        ))
    db.session.commit()
    return jsonify(dish_to_dict(copy, with_nutrition=True)), 201
