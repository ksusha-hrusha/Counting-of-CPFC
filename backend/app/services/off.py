"""
Поиск продуктов через Open Food Facts API.
Возвращает список продуктов с КБЖУ на 100г.
"""
import requests

OFF_SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"


def search_off(query: str, page_size: int = 20) -> list:
    """Ищет продукты в Open Food Facts, возвращает список dict."""
    try:
        resp = requests.get(
            OFF_SEARCH_URL,
            params={
                "search_terms": query,
                "search_simple": 1,
                "action": "process",
                "json": 1,
                "page_size": page_size,
                "fields": "id,product_name,nutriments",
            },
            timeout=8,
        )
        if resp.status_code != 200:
            return []
        products = []
        for p in resp.json().get("products", []):
            n = p.get("nutriments", {})
            name = p.get("product_name", "").strip()
            if not name:
                continue
            calories = n.get("energy-kcal_100g") or n.get("energy_100g", 0)
            # energy_100g может быть в кДж — конвертируем
            if not n.get("energy-kcal_100g") and n.get("energy_100g"):
                calories = round(float(n["energy_100g"]) / 4.184, 2)
            products.append({
                "off_id": p.get("id", ""),
                "name": name,
                "calories": round(float(calories or 0), 2),
                "protein": round(float(n.get("proteins_100g") or 0), 2),
                "fat": round(float(n.get("fat_100g") or 0), 2),
                "carbs": round(float(n.get("carbohydrates_100g") or 0), 2),
            })
        return products
    except Exception:
        return []
