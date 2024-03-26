import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
RGAPI = os.getenv('RGAPI')
TESTSERVER_ID = '1137866058867425340'