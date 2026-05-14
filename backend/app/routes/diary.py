from datetime import datetime, date, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import DailyMeal, Dish, Product
from app.services.calculator import calc_dish, calc_ingredient

diary_bp = Blueprint("diary", __name__)


def meal_to_dict(m):
    return {
        "id": m.id,
        "meal_date": m.meal_date.isoformat(),
        "meal_type": m.meal_type,
        "dish_id": m.dish_id,
        "product_id": m.product_id,
        "amount": m.amount,
        "calories": round(m.calories, 2),
        "protein": round(m.protein, 2),
        "fat": round(m.fat, 2),
        "carbs": round(m.carbs, 2),
        "label": m.label,
        "created_at": m.created_at.isoformat(),
    }


def _parse_date(value):
    if not value:
        return datetime.now(timezone.utc).date()
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return datetime.now(timezone.utc).date()


@diary_bp.get("/")
@jwt_required()
def list_meals():
    user_id = get_jwt_identity()
    day = _parse_date(request.args.get("date"))
    meals = (
        DailyMeal.query.filter_by(user_id=user_id, meal_date=day)
        .order_by(DailyMeal.created_at.asc())
        .all()
    )

    totals = {"calories": 0.0, "protein": 0.0, "fat": 0.0, "carbs": 0.0}
    for m in meals:
        totals["calories"] += m.calories
        totals["protein"] += m.protein
        totals["fat"] += m.fat
        totals["carbs"] += m.carbs

    return jsonify({
        "date": day.isoformat(),
        "meals": [meal_to_dict(m) for m in meals],
        "totals": {k: round(v, 2) for k, v in totals.items()},
    })


@diary_bp.post("/")
@jwt_required()
def add_meal():
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    day = _parse_date(data.get("date"))
    meal_type = data.get("meal_type", "snack")
    amount = float(data.get("amount", 1))
    dish_id = data.get("dish_id")
    product_id = data.get("product_id")
    cooking_method_id = data.get("cooking_method_id")

    if not dish_id and not product_id:
        return jsonify({"error": "Нужно указать dish_id или product_id"}), 400

    calories = protein = fat = carbs = 0.0
    label = data.get("label")

    if dish_id:
        dish = Dish.query.filter_by(id=dish_id).first()
        if not dish:
            return jsonify({"error": "Блюдо не найдено"}), 404
        # Только свои или публичные
        if dish.user_id != user_id and not dish.is_public:
            return jsonify({"error": "Нет доступа к блюду"}), 403
        nutrition = calc_dish(dish.ingredients, dish.cooking_method)
        total_weight = nutrition.get("weight_cooked") or 0
        servings = dish.servings or 1
        # amount = число порций
        factor = amount / servings if servings > 0 else amount
        calories = nutrition["calories"] * factor
        protein = nutrition["protein"] * factor
        fat = nutrition["fat"] * factor
        carbs = nutrition["carbs"] * factor
        if not label:
            label = dish.name
    else:
        product = Product.query.filter_by(id=product_id).first()
        if not product:
            return jsonify({"error": "Продукт не найден"}), 404
        from app.models import CookingMethod
        method = CookingMethod.query.get(cooking_method_id) if cooking_method_id else None
        result = calc_ingredient(product, amount, method)
        calories = result["calories"]
        protein = result["protein"]
        fat = result["fat"]
        carbs = result["carbs"]
        if not label:
            label = product.name_ru or product.name

    meal = DailyMeal(
        user_id=user_id,
        meal_date=day,
        meal_type=meal_type,
        dish_id=dish_id,
        product_id=product_id,
        amount=amount,
        calories=calories,
        protein=protein,
        fat=fat,
        carbs=carbs,
        label=label,
    )
    db.session.add(meal)
    db.session.commit()
    return jsonify(meal_to_dict(meal)), 201


@diary_bp.delete("/<meal_id>")
@jwt_required()
def delete_meal(meal_id):
    user_id = get_jwt_identity()
    meal = DailyMeal.query.filter_by(id=meal_id, user_id=user_id).first_or_404()
    db.session.delete(meal)
    db.session.commit()
    return jsonify({"ok": True})


@diary_bp.post("/bmi")
def calc_bmi():
    """Расчёт ИМТ и рекомендуемого КБЖУ.

    body:
      weight_kg, height_cm, age, sex ('male'|'female'),
      activity (1.2 .. 1.9), goal ('lose'|'gain'|'maintain')
    """
    data = request.get_json() or {}
    try:
        weight = float(data.get("weight_kg", 0))
        height = float(data.get("height_cm", 0))
        age = int(data.get("age", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Некорректные числовые данные"}), 400

    sex = (data.get("sex") or "male").lower()
    activity = float(data.get("activity", 1.375))
    goal = (data.get("goal") or "maintain").lower()

    if weight <= 0 or height <= 0 or age <= 0:
        return jsonify({"error": "Заполните вес, рост и возраст"}), 400

    # ИМТ
    height_m = height / 100.0
    bmi = weight / (height_m * height_m)
    if bmi < 18.5:
        bmi_class = "Недостаточный вес"
    elif bmi < 25:
        bmi_class = "Норма"
    elif bmi < 30:
        bmi_class = "Избыточный вес"
    elif bmi < 35:
        bmi_class = "Ожирение I степени"
    elif bmi < 40:
        bmi_class = "Ожирение II степени"
    else:
        bmi_class = "Ожирение III степени"

    # Идеальный вес (Лоренц)
    if sex == "female":
        ideal_weight = height - 100 - (height - 150) / 2.0
    else:
        ideal_weight = height - 100 - (height - 150) / 4.0

    # BMR Миффлина-Сан Жеора
    if sex == "female":
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age + 5

    tdee = bmr * activity

    # Цель
    if goal == "lose":
        target_calories = tdee - 500
    elif goal == "gain":
        target_calories = tdee + 400
    else:
        target_calories = tdee

    target_calories = max(1200, target_calories)

    # БЖУ по цели
    if goal == "lose":
        p_ratio, f_ratio, c_ratio = 0.35, 0.30, 0.35
    elif goal == "gain":
        p_ratio, f_ratio, c_ratio = 0.30, 0.25, 0.45
    else:
        p_ratio, f_ratio, c_ratio = 0.25, 0.30, 0.45

    protein_g = target_calories * p_ratio / 4.0
    fat_g = target_calories * f_ratio / 9.0
    carbs_g = target_calories * c_ratio / 4.0

    return jsonify({
        "bmi": round(bmi, 2),
        "bmi_class": bmi_class,
        "ideal_weight": round(ideal_weight, 1),
        "bmr": round(bmr, 0),
        "tdee": round(tdee, 0),
        "goal": goal,
        "target": {
            "calories": round(target_calories, 0),
            "protein": round(protein_g, 1),
            "fat": round(fat_g, 1),
            "carbs": round(carbs_g, 1),
        },
    })
