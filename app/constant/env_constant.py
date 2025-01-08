import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "gg_chatalyze")
DOTA_CONSTANTS_HOST = os.getenv("DOTA_CONSTANTS_HOST", "localhost:3000")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
