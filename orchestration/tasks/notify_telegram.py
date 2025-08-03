import os
import requests
from prefect import task
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


@task(name="notify_telegram")
def notify_telegram(message: str, parse_mode: str = "HTML") -> None:
    """
    Envía un mensaje a Telegram usando el bot y chat definidos por variables de entorno.

    Requiere:
    - TELEGRAM_BOT_TOKEN: token del bot de Telegram
    - TELEGRAM_CHAT_ID: ID del chat o canal

    Args:
        message (str): Texto del mensaje
        parse_mode (str): Modo de parseo del mensaje (HTML o MarkdownV2)
    """

    if not BOT_TOKEN or not CHAT_ID:
        raise ValueError(
            "Variables de entorno TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID son requeridas"
        )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": parse_mode}

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        raise RuntimeError(f"Error al enviar mensaje a Telegram: {response.text}")
