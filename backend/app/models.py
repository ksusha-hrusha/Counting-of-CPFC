import uuid
from app import db
from datetime import datetime, timezone


def gen_uuid():
    return str(uuid.uuid4())


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_exp = db.Column(db.DateTime, nullable=True)
    avatar = db.Column(db.String(200), nullable=True)  # путь к файлу аватарки
    dishes = db.relationship("Dish", backref="owner", lazy=True)


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    off_id = db.Column(db.String(100), unique=True, nullable=True)
    name = db.Column(db.String(200), nullable=False)
    name_ru = db.Column(db.String(200), nullable=True)
    calories = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    # unit: 'g' = граммы, 'pcs' = штуки
    unit = db.Column(db.String(10), default='g', nullable=False)
    # вес одной штуки в граммах (для unit='pcs')
    serving_weight = db.Column(db.Float, nullable=True)
    created_by = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)


class CookingMethod(db.Model):
    __tablename__ = "cooking_methods"
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    name = db.Column(db.String(50), nullable=False)
    weight_coefficient = db.Column(db.Float, nullable=False)


class Dish(db.Model):
    __tablename__ = "dishes"
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)
    servings = db.Column(db.Integer, default=1)
    is_public = db.Column(db.Boolean, default=False)
    # Термообработка на готовое блюдо целиком
    cooking_method_id = db.Column(db.String(36), db.ForeignKey("cooking_methods.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    ingredients = db.relationship("DishIngredient", backref="dish", lazy=True, cascade="all, delete-orphan", foreign_keys="DishIngredient.dish_id")
    cooking_method = db.relationship("CookingMethod", foreign_keys=[cooking_method_id])


class DishIngredient(db.Model):
    __tablename__ = "dish_ingredients"
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    dish_id = db.Column(db.String(36), db.ForeignKey("dishes.id"), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey("products.id"), nullable=True)
    # Для вложенного блюда как ингредиента
    nested_dish_id = db.Column(db.String(36), db.ForeignKey("dishes.id"), nullable=True)
    weight_raw = db.Column(db.Float, nullable=False)
    cooking_method_id = db.Column(db.String(36), db.ForeignKey("cooking_methods.id"), nullable=True)
    product = db.relationship("Product", foreign_keys=[product_id])
    cooking_method = db.relationship("CookingMethod", foreign_keys=[cooking_method_id])
    nested_dish = db.relationship("Dish", foreign_keys=[nested_dish_id])
