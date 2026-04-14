"""
Логика расчёта КБЖУ.
Поддерживает:
  - одиночный продукт с термообработкой
  - составное блюдо (сумма ингредиентов)
  - термообработку на готовое блюдо целиком
"""


def calc_ingredient(product, weight_raw: float, cooking_method=None) -> dict:
    """КБЖУ одного ингредиента после термообработки.
    Если product.unit == 'pcs', weight_raw = количество штук.
    """
    # Переводим штуки в граммы
    if getattr(product, 'unit', 'g') == 'pcs' and product.serving_weight:
        actual_grams = weight_raw * product.serving_weight
    else:
        actual_grams = weight_raw

    ratio = actual_grams / 100.0
    calories = product.calories * ratio
    protein = product.protein * ratio
    fat = product.fat * ratio
    carbs = product.carbs * ratio

    coeff = cooking_method.weight_coefficient if cooking_method else 1.0
    weight_cooked = actual_grams * coeff

    return {
        "calories": round(calories, 2),
        "protein": round(protein, 2),
        "fat": round(fat, 2),
        "carbs": round(carbs, 2),
        "weight_cooked": round(weight_cooked, 2),
    }


def calc_dish(ingredients: list, dish_cooking_method=None) -> dict:
    """
    Суммирует КБЖУ всех ингредиентов блюда.
    Если задан dish_cooking_method — применяет его коэффициент
    к итоговому весу (термообработка на готовое блюдо).
    """
    total = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0, "weight_cooked": 0}

    for ing in ingredients:
        if ing.product:
            result = calc_ingredient(ing.product, ing.weight_raw, ing.cooking_method)
        elif ing.nested_dish:
            # Вложенное блюдо — рекурсивно считаем его КБЖУ
            nested = calc_dish(ing.nested_dish.ingredients, ing.nested_dish.cooking_method)
            # Масштабируем по весу
            if nested["weight_cooked"] > 0:
                scale = ing.weight_raw / nested["weight_cooked"]
            else:
                scale = 1.0
            result = {
                "calories": round(nested["calories"] * scale, 2),
                "protein": round(nested["protein"] * scale, 2),
                "fat": round(nested["fat"] * scale, 2),
                "carbs": round(nested["carbs"] * scale, 2),
                "weight_cooked": ing.weight_raw,
            }
        else:
            continue

        for key in total:
            total[key] += result[key]

    # Применяем термообработку на всё блюдо
    if dish_cooking_method:
        coeff = dish_cooking_method.weight_coefficient
        total["weight_cooked"] = round(total["weight_cooked"] * coeff, 2)

    total_weight = total["weight_cooked"]
    per_100 = {}
    if total_weight > 0:
        per_100 = {
            "calories": round(total["calories"] / total_weight * 100, 2),
            "protein": round(total["protein"] / total_weight * 100, 2),
            "fat": round(total["fat"] / total_weight * 100, 2),
            "carbs": round(total["carbs"] / total_weight * 100, 2),
        }
    else:
        per_100 = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}

    return {**{k: round(v, 2) for k, v in total.items()}, "per_100g": per_100}
