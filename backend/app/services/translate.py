"""
Перевод через LibreTranslate с кэшированием в БД (поле name_ru у Product).
"""
import requests
import os


LIBRETRANSLATE_URL = os.getenv("LIBRETRANSLATE_URL", "https://libretranslate.com")
LIBRETRANSLATE_API_KEY = os.getenv("LIBRETRANSLATE_API_KEY", "")


def translate_to_ru(text: str) -> str:
    """Переводит текст с английского на русский через LibreTranslate."""
    if not text:
        return text
    try:
        payload = {"q": text, "source": "en", "target": "ru", "format": "text"}
        if LIBRETRANSLATE_API_KEY:
            payload["api_key"] = LIBRETRANSLATE_API_KEY
        resp = requests.post(
            f"{LIBRETRANSLATE_URL}/translate",
            json=payload,
            timeout=5,
        )
        if resp.status_code == 200:
            return resp.json().get("translatedText", text)
    except Exception:
        pass
    return text
