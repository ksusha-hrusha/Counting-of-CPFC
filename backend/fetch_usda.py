"""
Скачивает продукты из USDA FoodData Central и сохраняет в БД.
Запуск: python fetch_usda.py
"""
import requests
import psycopg
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = "fPHThdUY98Kcy7PHY3OvJcT8icq1ee7LfTKig9i2"
BASE_URL = "https://api.nal.usda.gov/fdc/v1"

# Категории для поиска
QUERIES = [
    "chicken", "beef", "pork", "turkey", "lamb", "duck", "rabbit",
    "salmon", "tuna", "cod", "shrimp", "herring", "mackerel", "pollock",
    "egg", "milk", "cheese", "butter", "yogurt", "kefir", "cottage cheese",
    "rice", "buckwheat", "oats", "pasta", "bread", "flour", "semolina",
    "potato", "carrot", "onion", "cabbage", "broccoli", "tomato", "cucumber",
    "pepper", "zucchini", "eggplant", "beet", "spinach", "garlic", "corn",
    "apple", "banana", "orange", "pear", "strawberry", "grape", "peach",
    "blueberry", "kiwi", "watermelon", "lemon", "cherry", "plum", "mango",
    "lentils", "chickpeas", "beans", "peas", "soy",
    "walnut", "almond", "peanut", "cashew", "sunflower seeds",
    "olive oil", "sunflower oil", "honey", "sugar", "mushroom", "tofu",
    "avocado", "pumpkin", "celery", "lettuce", "radish", "asparagus",
]


def fetch_products(query, page_size=25):
    resp = requests.get(
        f"{BASE_URL}/foods/search",
        params={
            "api_key": API_KEY,
            "query": query,
            "dataType": "SR Legacy",
            "pageSize": page_size,
        },
        timeout=10,
    )
    if resp.status_code != 200:
        print(f"  Ошибка {resp.status_code} для '{query}'")
        return []
    return resp.json().get("foods", [])


def parse_nutrient(food, nutrient_id):
    for n in food.get("foodNutrients", []):
        if n.get("nutrientId") == nutrient_id:
            return round(float(n.get("value", 0)), 2)
    return 0.0


def main():
    db_url = os.getenv("DATABASE_URL", "")
    if db_url.startswith("postgresql+psycopg://"):
        db_url = db_url.replace("postgresql+psycopg://", "postgresql://", 1)

    conn = psycopg.connect(db_url)
    cur = conn.cursor()

    total = 0
    seen_fdc_ids = set()

    for query in QUERIES:
        print(f"Загружаю: {query}...")
        foods = fetch_products(query)
        for food in foods:
            fdc_id = str(food.get("fdcId", ""))
            if fdc_id in seen_fdc_ids:
                continue
            seen_fdc_ids.add(fdc_id)

            name = food.get("description", "").strip()
            if not name:
                continue

            # USDA nutrient IDs: 1008=energy(kcal), 1003=protein, 1004=fat, 1005=carbs
            calories = parse_nutrient(food, 1008)
            protein  = parse_nutrient(food, 1003)
            fat      = parse_nutrient(food, 1004)
            carbs    = parse_nutrient(food, 1005)

            # Пропускаем если нет данных
            if calories == 0 and protein == 0:
                continue

            # Проверяем дубликат по off_id (используем fdc_id как off_id)
            cur.execute("SELECT id FROM products WHERE off_id = %s", (fdc_id,))
            if cur.fetchone():
                continue

            cur.execute(
                """INSERT INTO products (id, off_id, name, name_ru, calories, protein, fat, carbs)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (str(uuid.uuid4()), fdc_id, name, None, calories, protein, fat, carbs)
            )
            total += 1

        conn.commit()
        print(f"  Добавлено: {total} продуктов всего")

    cur.close()
    conn.close()
    print(f"\nГотово! Всего добавлено {total} продуктов.")


if __name__ == "__main__":
    main()
