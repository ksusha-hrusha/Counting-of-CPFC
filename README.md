# NutriCalc

Веб-сервис для точного подсчёта КБЖУ с учётом термической обработки.

## Требования

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

## Запуск backend

Открой bash-терминал (Git Bash) в папке проекта и выполни:

```bash
cd nutricale/backend

# Создать виртуальное окружение
python -m venv venv
source venv/Scripts/activate      # Git Bash на Windows
# source venv/bin/activate        # Linux/Mac

# Установить зависимости
pip install -r requirements.txt

# Создать .env
cp .env.example .env
# Открой .env и заполни DATABASE_URL и JWT_SECRET_KEY

# Создать БД в PostgreSQL (в psql или pgAdmin):
# CREATE DATABASE nutricale;

# Применить миграции
flask --app run db init
flask --app run db migrate -m "init"
flask --app run db upgrade

# Заполнить начальные данные
flask --app run seed

# Запустить
python run.py
```

Backend будет доступен на http://localhost:5000

## Запуск frontend

Открой **второй** bash-терминал в папке проекта:

```bash
cd nutricale/frontend
npm install
npm run dev
```

Frontend будет доступен на http://localhost:5173

## Переменные окружения (.env)

| Переменная | Описание |
|---|---|
| DATABASE_URL | postgresql://user:pass@localhost:5432/nutricale |
| JWT_SECRET_KEY | Секретный ключ для JWT |
| LIBRETRANSLATE_URL | URL LibreTranslate (по умолчанию https://libretranslate.com) |
| LIBRETRANSLATE_API_KEY | API ключ LibreTranslate (необязательно для публичного) |

## Функциональность

- Поиск продуктов через Open Food Facts с переводом на русский (LibreTranslate + кэш в БД)
- Расчёт КБЖУ с учётом термообработки (варка, жарка, запекание и др.)
- Термообработка на готовое блюдо целиком
- Составные блюда с live-preview КБЖУ
- JWT авторизация
- Публичный каталог блюд
- Две цветовые темы: зелёная и розовая (переключатель в шапке)
