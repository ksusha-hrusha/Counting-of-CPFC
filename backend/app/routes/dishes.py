from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Dish, DishIngredient, CookingMethod
from app.services.calculator import calc_dish

dishes_bp = Blueprint("dishes", __name__)


def ingredient_to_dict(ing):
    if ing.product:
        label = ing.product.name_ru or ing.product.name
        ref_id = ing.product_id
        ref_type = "product"
    elif ing.nested_dish:
        label = ing.nested_dish.name
        ref_id = ing.nested_dish_id
        ref_type = "dish"
    else:
        label = "?"
        ref_id = None
        ref_type = None
    return {
        "id": ing.id,
        "ref_type": ref_type,
        "ref_id": ref_id,
        "label": label,
        "weight_raw": ing.weight_raw,
        "cooking_method_id": ing.cooking_method_id,
        "cooking_method_name": ing.cooking_method.name if ing.cooking_method else None,
    }


def dish_to_dict(dish, with_nutrition=False):
    d = {
        "id": dish.id,
        "name": dish.name,
        "description": dish.description,
        "category": dish.category,
        "servings": dish.servings,
        "is_public": dish.is_public,
        "cooking_method_id": dish.cooking_method_id,
        "cooking_method_name": dish.cooking_method.name if dish.cooking_method else None,
        "created_at": dish.created_at.isoformat(),
        "ingredients": [ingredient_to_dict(i) for i in dish.ingredients],
    }
    if with_nutrition:
        d["nutrition"] = calc_dish(dish.ingredients, dish.cooking_method)
    return d


@dishes_bp.get("/")
@jwt_required()
def list_dishes():
    user_id = get_jwt_identity()
    dishes = Dish.query.filter_by(user_id=user_id).order_by(Dish.created_at.desc()).all()
    return jsonify([dish_to_dict(d, with_nutrition=True) for d in dishes])


@dishes_bp.post("/")
@jwt_required()
def create_dish():
    user_id = get_jwt_identity()
    data = request.get_json()
    dish = Dish(
        user_id=user_id,
        name=data.get("name", "Без названия"),
        description=data.get("description"),
        category=data.get("category"),
        servings=data.get("servings", 1),
        is_public=data.get("is_public", False),
        cooking_method_id=data.get("cooking_method_id"),
    )
    db.session.add(dish)
    db.session.flush()

    for ing in data.get("ingredients", []):
        ingredient = DishIngredient(
            dish_id=dish.id,
            product_id=ing.get("product_id"),
            nested_dish_id=ing.get("nested_dish_id"),
            weight_raw=float(ing.get("weight_raw", 0)),
            cooking_method_id=ing.get("cooking_method_id"),
        )
        db.session.add(ingredient)

    db.session.commit()
    return jsonify(dish_to_dict(dish, with_nutrition=True)), 201


@dishes_bp.get("/<dish_id>")
@jwt_required()
def get_dish(dish_id):
    user_id = get_jwt_identity()
    dish = Dish.query.filter_by(id=dish_id, user_id=user_id).first_or_404()
    return jsonify(dish_to_dict(dish, with_nutrition=True))


@dishes_bp.put("/<dish_id>")
@jwt_required()
def update_dish(dish_id):
    user_id = get_jwt_identity()
    dish = Dish.query.filter_by(id=dish_id, user_id=user_id).first_or_404()
    data = request.get_json()

    dish.name = data.get("name", dish.name)
    dish.description = data.get("description", dish.description)
    dish.category = data.get("category", dish.category)
    dish.servings = data.get("servings", dish.servings)
    dish.is_public = data.get("is_public", dish.is_public)
    dish.cooking_method_id = data.get("cooking_method_id", dish.cooking_method_id)

    if "ingredients" in data:
        for ing in dish.ingredients:
            db.session.delete(ing)
        db.session.flush()
        for ing in data["ingredients"]:
            ingredient = DishIngredient(
                dish_id=dish.id,
                product_id=ing.get("product_id"),
                nested_dish_id=ing.get("nested_dish_id"),
                weight_raw=float(ing.get("weight_raw", 0)),
                cooking_method_id=ing.get("cooking_method_id"),
            )
            db.session.add(ingredient)

    db.session.commit()
    return jsonify(dish_to_dict(dish, with_nutrition=True))


@dishes_bp.delete("/<dish_id>")
@jwt_required()
def delete_dish(dish_id):
    user_id = get_jwt_identity()
    dish = Dish.query.filter_by(id=dish_id, user_id=user_id).first_or_404()
    db.session.delete(dish)
    db.session.commit()
    return jsonify({"ok": True})


@dishes_bp.post("/<dish_id>/publish")
@jwt_required()
def publish_dish(dish_id):
    user_id = get_jwt_identity()
    dish = Dish.query.filter_by(id=dish_id, user_id=user_id).first_or_404()
    dish.is_public = not dish.is_public
    db.session.commit()
    return jsonify({"is_public": dish.is_public})
