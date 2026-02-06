import os
from dotenv import load_dotenv

load_dotenv()

# токен бота
BOT_TOKEN = str(os.getenv("TOKEN"))

ADMINS = str(os.getenv("admins"))

# id админов
admins_id = [7683783190, 923162995]