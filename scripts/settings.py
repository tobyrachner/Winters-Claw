from dotenv import load_dotenv
import os
import json

TESTSERVER_ID = '1137866058867425340'
CURRENT_SET = 11.0
SET_START_DATE = 1710932400   # March 20th, 2024, 11:00:00 GMT 

CURRENT_PATCH = '14.7.1' #required for ddragon endpoints

load_dotenv()
RGAPI = os.getenv('RGAPI')
TOKEN = os.getenv('DISCORD_TOKEN')
ADMIN_TOKEN = os.getenv('DISCORD_ADMIN_TOKEN')

with open('data/ranked_tiers.json') as f:
    ranked_tiers = json.load(f)
with open('data/traits.json', 'r') as f:
    trait_list = json.load(f)
with open('data/trait_emoji.json', 'r') as f:
    trait_emoji = json.load(f)
with open('data/augments.json', 'r') as f:
    augment_list = json.load(f)
with open('data/augment_emoji.json', 'r') as f:
    augment_emoji = json.load(f)

unique_traits = ['Artist', 'Great', 'Lovers', 'Spirit Walker', 'Trickshot/Altruist']