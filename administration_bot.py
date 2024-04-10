#
# This bot is used to manage things like custom emoji for various traits and augments etc.
# that require more permissions than the main Bot has.
# This Bot is NOT INTENDED to be used in production and just exists to make the developers' lifes easier
#

import requests
import json
from time import sleep
from io import BytesIO

import discord
from discord.ext import commands

from scripts import settings

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="$", intents=intents)


@bot.event
async def on_ready():
    print('online')
    await bot.tree.sync()
guild_ids = []
@bot.event
async def on_message(ctx):
    if ctx.content == 'wc create emoji':
        print(bot.get_guild(settings.setup['augments']['guild_ids'][5]).name)


def get_current_untis():
    champ_data = requests.get('https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/tftchampions.json').json()

    set11 = []
    for champ in champ_data:
        if champ['name'].startswith('TFT11'):
            set11.append(champ)

    champions = {}
    for champ in set11:
        champions[champ['name']] = {
            'id': champ['name'],
            'name': champ['character_record']['display_name'], 
            'image': champ['character_record']['squareIconPath'].split('Characters/')[1]
        }

    with open('data/units.json', 'w') as f:
        json.dump(champions, f, indent=2)
    with open('data/temp_units.json', 'w') as f:
        json.dump(champions, f, indent=2)

def get_current_augments():
    augments = requests.get(f'https://ddragon.leagueoflegends.com/cdn/{settings.CURRENT_PATCH}/data/en_US/tft-augments.json').json()['data']

    with open('data/augments.json', 'w') as f:
        json.dump(augments, f, indent=2)
    with open('data/temp_augments.json', 'w') as f:
        json.dump(augments, f, indent=2)

def get_current_items():
    items = requests.get('https://ddragon.leagueoflegends.com/cdn/14.7.1/data/en_US/tft-item.json').json()['data']

    new_items = {}
    for item in items:
        if '/' in item:
            item = item.split('/')[1]
        new_items[item] = {'id': item, 'name': items[item]['name'], 'image': items[item]['image']['full']}

    with open('data/items.json', 'w') as f:
        json.dump(new_items, f, indent=2)

    with open('data/items.json', 'w') as f:
        json.dump(new_items, f, indent=2)
    with open('data/temp_items.json', 'w') as f:
        json.dump(new_items, f, indent=2)

async def add_emoji(ctx, type):
    img_path = settings.setup[type]['img_path']
    guild_ids = settings.setup[type]['guild_ids']

    if ctx.content == 'wc create emoji':
        overall_count = 0

        with open(f'data/temp_{type}.json', 'r') as f:
            objects = json.load(f)
            new_objects = objects.copy()

        if not ctx.author.guild_permissions.manage_emojis:
            return
        
        for id in guild_ids:
            guild = bot.get_guild(id)
            if guild.name.endswith('1') or guild.name.endswith('2'):
                print('skipped', guild.name)
                continue
            guild_count = 0
            guild_objects = new_objects.copy()
        
            for object in guild_objects:
                url = objects[object]['image']
                img = BytesIO(requests.get(img_path + url).content)

                # replacing all the special characters used in Augment Names [',', '+', '-', '!', ''', '&', '.', '_', '/'] with letters because discord emojis do not accept special characters
                name = objects[object]['name'].replace(' ', '').replace(',', 'AAA').replace('+', 'BBB').replace('-', 'CCC').replace('!', 'DDD').replace("'", 'EEE')
                name = name.replace('&', 'FFF').replace('.', 'GGG').replace('_', 'HHH').replace('/', 'JJJ')

                try:
                    await guild.create_custom_emoji(image=img.getvalue(), name=name)
                    del new_objects[object]
                    overall_count += 1
                    guild_count += 1
                    print(overall_count, guild_count, '-', objects[object]['name'])

                    sleep(5.1)  # waiting to avoid discord rate limit

                    if guild_count >= 50:
                        break
                except Exception as e:
                    print(e)
                    break

        with open(f'data/temp_{type}.json', 'w') as f:
            json.dump(new_objects, f, indent=2)

def get_emoji_ids(type):
    guild_ids = settings.setup[type]['guild_ids']

    with open(f'data/{type}.json', 'r') as f:
        objects = json.load(f)

    with open(f'data/{type}_emoji.json', 'r') as f:
        object_emoji = json.load(f)

    names = {}
    for object in objects:
        name = objects[object]['name'].replace(' ', '').replace(',', 'AAA').replace('+', 'BBB').replace('-', 'CCC').replace('!', 'DDD')
        name = name.replace("'", 'EEE').replace('&', 'FFF').replace('.', 'GGG').replace('_', 'HHH').replace('/', 'JJJ')
        names[name] = objects[object]['name']

    for id in guild_ids:
        guild = bot.get_guild(id)
        print(guild.name)
        for emoji in guild.emojis:
            if emoji.name in names:
                name = names[emoji.name]
                object_emoji[name] = f'<:{emoji.name}:{emoji.id}>'

    with open(f'data/{type}_emoji.json', 'w') as f:
        json.dump(object_emoji, f, indent=2)

    return

bot.run(settings.ADMIN_TOKEN)