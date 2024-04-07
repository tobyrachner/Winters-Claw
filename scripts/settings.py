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

setup = {
    'augments': {'img_path': 'https://raw.communitydragon.org/latest/game/assets/maps/tft/icons/augments/choiceui/', 'guild_ids': [1226021957963743262, 1226022008643518526, 1226022064897392660, 1226022118664437872, 1226022170291867669, 1226022232007114823]},
    'units': {'img_path': 'https://raw.communitydragon.org/latest/game/assets/characters/', 'guild_ids': [1226197363589124238, 1226197423727317143]},
    'items': {'img_path': 'https://ddragon.leagueoflegends.com/cdn/14.7.1/img/tft-item/', 'guild_ids': [1226317902458785843, 1226281674296266873, 1226281740494966874, 1226281789283237918, 1226281841217241139]}
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