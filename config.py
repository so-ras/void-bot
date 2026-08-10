import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8882672601:AAGJos3r1VJPYKiJuoPL9RW5kR3O92iezpA")
OWNER_ID = int(os.getenv("OWNER_ID", 1391789851))

# از my.telegram.org بگیر
API_ID = 31421832
API_HASH = "8c212c014c85ea497cc5d7dac6b2e6cb"

WARN_LIMIT = 3
FLOOD_LIMIT = 5
REWARD_ENABLED = True
DEFAULT_LANG = "fa"
