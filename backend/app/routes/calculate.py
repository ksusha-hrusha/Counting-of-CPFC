from flask import Blueprint, request, jsonify
from app.models import Product, CookingMethod, DishIngredient
from app.services.calculator import calc_ingredient, calc_dish

calculate_bp = Blueprint("calculate", __name__)


@calculate_bp.post("/")
def calculate():
    data = request.get_json()
    product_id = data.get("product_id")
    weight_raw = float(data.get("weight_raw", 0))
    cooking_method_id = data.get("cooking_method_id")

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Продукт не найден"}), 404

    method = CookingMethod.query.get(cooking_method_id) if cooking_method_id else None
    result = calc_ingredient(product, weight_raw, method)
    return jsonify(result)


@calculate_bp.post("/dish-preview")
def dish_preview():
    """Расчёт КБЖУ блюда без сохранения (для live-preview в форме)."""
    data = request.get_json()
    ingredients_data = data.get("ingredients", [])
    cooking_method_id = data.get("cooking_method_id")

    # Строим временные объекты ингредиентов
    class FakeIng:
        def __init__(self, product, weight_raw, cooking_method, nested_dish=None):
            self.product = product
            self.weight_raw = weight_raw
            self.cooking_method = cooking_method
            self.nested_dish = nested_dish

    ings = []
    for ing in ingredients_data:
        product = Product.query.get(ing.get("product_id")) if ing.get("product_id") else None
        method = CookingMethod.query.get(ing.get("cooking_method_id")) if ing.get("cooking_method_id") else None
        ings.append(FakeIng(product, float(ing.get("weight_raw", 0)), method))

    dish_method = CookingMethod.query.get(cooking_method_id) if cooking_method_id else None
    result = calc_dish(ings, dish_method)
    return jsonify(result)
