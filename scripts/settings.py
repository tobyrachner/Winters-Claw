from dotenv import load_dotenv
import os
import json

TESTSERVER_ID = '1137866058867425340'
CURRENT_SET = 11.0
SET_START_DATE = 1710932400   # March 20th, 2024, 11:00:00 GMT 

CURRENT_PATCH = '14.7.1' #required for ddragon endpoints
MIN_SUPPORTED_SET = 11

load_dotenv()
RGAPI = os.getenv('RGAPI')
TOKEN = os.getenv('DISCORD_TOKEN')
ADMIN_TOKEN = os.getenv('DISCORD_ADMIN_TOKEN')

guild_ids = os.getenv('GUILD_IDS').split(', ')[:-1]

setup = {
    'augments': 'https://raw.communitydragon.org/latest/game/assets/maps/tft/icons/augments/choiceui/',
    'units': 'https://raw.communitydragon.org/latest/game/assets/characters/',
    'traits': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/ux/traiticons/',
    'items': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/maps/particles/tft/item_icons/',
    }

with open('data/ranked_tiers.json') as f:
    ranked_tiers = json.load(f)
with open('data/traits.json', 'r') as f:
    trait_list = json.load(f)
with open('data/trait_emoji.json', 'r') as f:
    trait_emoji = json.load(f)
with open('data/units.json', 'r') as f:
    unit_list = json.load(f)
with open('data/unit_emoji.json', 'r') as f:
    unit_emoji = json.load(f)
with open('data/augments.json', 'r') as f:
    augment_list = json.load(f)
with open('data/augment_emoji.json', 'r') as f:
    augment_emoji = json.load(f)
with open('data/items.json', 'r') as f:
    item_list = json.load(f)
with open('data/items_emoji.json', 'r') as f:
    item_emoji = json.load(f)
with open('data/misc_emoji.json', 'r') as f:
    misc_emoji = json.load(f)

unique_traits = ['Artist', 'Great', 'Lovers', 'Spirit Walker', 'Trickshot/Altruist']