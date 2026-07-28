import logging
import requests
from config import DISCORD_WEBHOOK_URL
logger = logging.getLogger(__name__)


def discord(webhook_url, message):
    msg = {"content": message}
    response = requests.post(webhook_url, json=msg)
    if response.status_code == 204:
        logger.info("Alert sent to Discord successfully.")
    else:
        logger.error(f"Failed to send alert to Discord. Status code: {response.status_code}")


def alerter(service, message):
    if service == "discord":
        discord(DISCORD_WEBHOOK_URL, message)
    else:
        logger.warning(f"Alert service not supported: {service}")
