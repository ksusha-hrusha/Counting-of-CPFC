# Counting-of-CPFC / NutriCalc

Веб-сервис для упрощённого подсчёта пищевой ценности продуктов в сыром виде, после термической обработки и в составных блюдах (супы, рагу и т.д.), с дневником питания и расчётом ИМТ/нормы КБЖУ.

[Документация / описание проекта](https://docs.google.com/document/d/1OM11w-eVbyQG9DLlLOxwpjPVmSsXTAbtJuQWXhQhjSM/edit?usp=sharing)

[Ссылка на сайт проекта](https://nutricalc.silaeder.space)

## Требования

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

## Запуск backend

```bash
cd nutricale/backend

python -m venv venv
source venv/Scripts/activate      # Git Bash на Windows
# source venv/bin/activate        # Linux/Mac

pip install -r requirements.txt

cp .env.example .env
# Заполни DATABASE_URL и JWT_SECRET_KEY

# Создай БД nutricale в PostgreSQL

flask --app run db upgrade
flask --app run seed

python run.py
```

Backend: http://localhost:5000

## Запуск frontend

```bash
cd nutricale/frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

## Запуск через docker compose

```bash
docker compose up -d --build
```

## Переменные окружения (.env)

| Переменная | Описание |
|---|---|
| DATABASE_URL | postgresql://user:pass@localhost:5432/nutricale |
| JWT_SECRET_KEY | Секретный ключ для JWT |
| LIBRETRANSLATE_URL | URL LibreTranslate (по умолчанию https://libretranslate.com) |
| LIBRETRANSLATE_API_KEY | API ключ LibreTranslate (необязательно) |

## Функциональность

- Поиск продуктов через Open Food Facts с переводом на русский (LibreTranslate + кэш в БД)
- Расчёт КБЖУ с учётом термообработки (варка, жарка, запекание и др.)
- Термообработка на готовое блюдо целиком
- Составные блюда с live-preview КБЖУ
- Дневник питания: трекинг блюд по дням, разбивка по приёмам пищи
- Расчёт ИМТ, BMR (Миффлин-Сан Жеор), TDEE и нормы КБЖУ под цели: похудение / поддержание / набор массы
- JWT-авторизация, аватарки, публичные блюда и лента
