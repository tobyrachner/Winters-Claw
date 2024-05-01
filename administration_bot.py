#
# This bot is used to manage things like custom emoji for various traits and augments etc.
# that require more permissions than the main Bot has.
# This Bot is NOT INTENDED to be used in production and just exists to make the developers' lifes easier
#

import requests
import json
import os
from math import ceil
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
    await get_guild_ids(231)

@bot.event
async def on_message(ctx):
    if ctx.content == 'wc test':
        get_current_augments()


def get_current_untis():
    if 'units.json' in os.listdir('data/'):
        with open('data/units.json', 'r') as f:
            units = json.load(f)
    else:
        units = {}

    unit_data = requests.get('https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/tftchampions.json').json()

    supported = []
    for unit in unit_data:
        set_num = unit['name'].split('_')[0][3:]
        if set_num.isnumeric() and int(set_num) => settings.MIN_SET_SUPPORTED:
            supported.append(unit)

    new = {}
    for unit in supported:
        entry = {
            'name': unit['character_record']['display_name'], 
            'image': unit['character_record']['squareIconPath'].split('Characters/')[1].lower(),
        }

        if not unit['name'] in units:
            new[unit['name']] = entry

        units[unit['name']] = entry
    with open('data/units.json', 'w') as f:
        json.dump(units, f, indent=2)
    with open('data/temp_units.json', 'w') as f:
        json.dump(new, f, indent=2)

def get_current_augments():
    if 'augments.json' in os.listdir('data/'):
        with open('data/augments.json', 'r') as f:
            augments = json.load(f)
    else:
        augments = {}

    item_data = requests.get('https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/tftitems.json').json()

    augment_list = []
    for item in item_data:
        name = item['nameId']
        if 'Augment' in name:
            augment_list.append(item)

    new = []
    for augment in augment_list:
        entry = {
            'name': augment['name'], 
            'image': augment['squareIconPath'].lower().split('hexcore/')[-1],
        }

        if not augment['nameId'] in augments:
            new[augment['nameId']] = entry

        augments[augment['nameId']] = entry

    with open('data/augments.json', 'w') as f:
        json.dump(augments, f, indent=2)
    with open('data/temp_augments.json', 'w') as f:
        json.dump(new, f, indent=2)

def get_current_augments_old():
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

async def setup():
    # get list of all missing objects

    # get number of required emoji slots + guild ids

    # add emoji

    # get emoji ids
    pass

async def get_guild_ids(slots):
    last_guild = bot.get_guild(settings.guild_ids['augments'][-1])
    available = last_guild.emoji_limit - len(last_guild.emojis)
    
    guild_ids = []
    while True:
        guilds_needed = ceil((slots - available) / 50) 
        if guilds_needed <= 0:
            return guild_ids
        
        input_guilds = await input(f"You need {guilds_needed} more servers. Enter them individually or seperated by commas. \nTo get the server ids, right click the server icon and press 'Copy Server ID' \nPress 'c' to cancel the process\n")
        if input_guilds == 'c':
            print('successfully cancelled process')
            return 'c'

        errors = []
        for id in input_guilds.split(', '):
            if not id.isnumeric():
                errors.append(id)
                continue

            guild = bot.get_guild(int(id))
            if not guild:
                errors.append(id)
                continue

            guild_ids.append(id)
            available += guild.emoji_limit - len(guild.emojis)

        if errors:
            print('Following server IDs are invalid or the Bot is not added to the servers: \n' + ', '.join(errors))


async def new_add_emoji(ctx, type):
    img_path = settings.setup[type]['img_path']
    guild_ids = settings.setup[type]['guild_ids']

    if type + '_emoji.json' in os.listdir('data/'):
        with open(f'data/{type}_emoji.json', 'r') as f:
            added = set(json.load(f))
    else:
        added = set({})

    overall_count = 0

    with open(f'data/temp_{type}.json', 'r') as f:
        objects = json.load(f)
        new_objects = objects.copy()

    if not ctx.author.guild_permissions.manage_emojis:
        return
        
    for id in guild_ids:
        guild = bot.get_guild(id)
        guild_count = 0
        guild_objects = new_objects.copy()
        
        for object in guild_objects:
            if  object['name'] in added:
                del new_objects[object]
                continue

            url = objects[object]['image']
            img = BytesIO(requests.get(img_path + url).content)

            # replacing all the special characters used in Augment Names [',', '+', '-', '!', ''', '&', '.', '_', '/'] with letters because discord emojis do not accept special characters
            name = objects[object]['name'].replace(' ', '').replace(',', 'AAA').replace('+', 'BBB').replace('-', 'CCC').replace('!', 'DDD').replace("'", 'EEE')
            name = name.replace('&', 'FFF').replace('.', 'GGG').replace('_', 'HHH').replace('/', 'JJJ')

            try:
                await guild.create_custom_emoji(image=img.getvalue(), name=name)
                del new_objects[object]
                added.add(object['name'])
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
