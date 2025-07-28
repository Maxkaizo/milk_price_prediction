import os
import requests
from prefect import task

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

    TELEGRAM_BOT_TOKEN = "8220632753:AAG6_ePNCwcJQhJk1l6cptx4dD1kd7M9hrU"
    TELEGRAM_CHAT_ID = "582235345"

    token = TELEGRAM_BOT_TOKEN
    chat_id = TELEGRAM_CHAT_ID

    # token = os.getenv("TELEGRAM_BOT_TOKEN")
    # chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        raise ValueError("Variables de entorno TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID son requeridas")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": parse_mode
    }

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        raise RuntimeError(f"Error al enviar mensaje a Telegram: {response.text}")
