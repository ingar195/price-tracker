import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
ALERT_TIMER = int(os.getenv("ALERT_TIMER", 1)) # In minutes
