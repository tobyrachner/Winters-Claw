#
# This bot is used to manage things like custom emoji for various traits and augments etc.
# that require more permissions than the main Bot has.
# This Bot is NOT INTENDED to be used in production and just exists to make the developers' lifes easier
#

import requests
import json
import os
import dotenv
from math import ceil
from io import BytesIO

from scripts import settings

import discord
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="$", intents=intents)

@bot.event
async def on_message(ctx):
    # a development way to easily use and test recovery commands
    # all commands here are also available from the main file

    if ctx.content == 'wc emoji_setup':
        recover_from_discord(bot)

def get_current_units():
    if 'units.json' in os.listdir('data/'):
        with open('data/units.json', 'r') as f:
            units = json.load(f)
    else:
        units = {}

    unit_data = requests.get('https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/tftchampions.json').json()

    supported = []
    for unit in unit_data:
        set_num = unit['name'].split('_')[0][3:]
        if set_num.isnumeric() and int(set_num) >= settings.MIN_SUPPORTED_SET:
            supported.append(unit)

    new = {}
    for unit in supported:
        if not unit['name'] in units:
            entry = {
                'name': unit['character_record']['display_name'], 
                'image': unit['character_record']['squareIconPath'].lower().split('characters/')[-1],
                'emoji': None,
            }

            new[unit['name']] = entry
            units[unit['name']] = entry
        
    return new, units

def get_current_traits():
    if 'traits.json' in os.listdir('data/'):
        with open('data/traits.json', 'r') as f:
            traits = json.load(f)
    else:
        traits = {}

    trait_data = requests.get('https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/tfttraits.json').json()

    supported = []
    for trait in trait_data:
        set_num = trait['set'].split('Set')[1]
        if set_num.isnumeric() and int(set_num) >= settings.MIN_SUPPORTED_SET or 'Event' in trait['trait_id']:
            supported.append(trait)

    new = {}
    for trait in supported:
        if not trait['trait_id'] in traits:
            entry = {
                'name': trait['display_name'], 
                'image': trait['icon_path'].lower().split('traiticons/')[-1],
                'emoji': None,
            }

            if trait['conditional_trait_sets'][0]['style_name'] == 'kUnique':
                entry['unique'] = True

            new[trait['trait_id']] = entry
            traits[trait['trait_id']] = entry

    return new, traits

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
        if '_Augment' in name:
            augment_list.append(item)

    new = {}
    for augment in augment_list:
        if not augment['nameId'] in augments:
            entry = {
                'name': augment['name'], 
                'image': augment['squareIconPath'].lower().split('hexcore/')[-1],
                'emoji': None,
            }

            new[augment['nameId']] = entry
            augments[augment['nameId']] = entry

    return new, augments

def get_current_items():
    if 'items.json' in os.listdir('data/'):
        with open('data/items.json', 'r') as f:
            items = json.load(f)
    else:
        items = {}

    item_data = requests.get('https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/tftitems.json').json()

    item_list = []
    for item in item_data:
        name = item['nameId']
        if '_Item' in name:
            item_list.append(item)

    new = {}
    for item in item_list:
        if not item['nameId'] in items:
            entry = {
                'name': item['name'], 
                'image': item['squareIconPath'].lower().split('item_icons/')[-1],
                'emoji': None,
            }

            new[item['nameId']] = entry
            items[item['nameId']] = entry

    return new, items

async def get_guild_ids(bot, slots):
    print('in guild')
    guild_ids = []

    if len(settings.guild_ids) > 0:
        guild_ids.append(settings.guild_ids[-1])
        last_guild = bot.get_guild(settings.guild_ids[-1])
        available = last_guild.emoji_limit - len(last_guild.emojis)
    else:
        available = 0
    
    while True:
        guilds_needed = ceil((slots - available) / 50) 
        if slots - available <= 0:
            return guild_ids
        
        input_guilds = input(f"You need {slots - available} more slots ({guilds_needed} empty servers). Enter them individually or seperated by commas. \nTo get the server ids, right click the server icon and press 'Copy Server ID' \nPress 'c' to cancel the process\n")
        if input_guilds == 'c':
            return 'cancelled'

        errors = []
        for id in input_guilds.split(', '):
            print(int(id))
            if not id.isnumeric():
                errors.append(id)
                continue

            if int(id) in guild_ids:
                errors.append(id)
                continue

            guild = bot.get_guild(int(id))
            if not guild:
                errors.append(id)
                continue

            guild_ids.append(int(id))
            available += guild.emoji_limit - len(guild.emojis)

        if errors:
            print('Following server IDs are invalid, already in use or the Bot is not added to the servers: \n' + ', '.join(errors))

async def add_emoji(bot, type, new, total_count, duplicates, added_emoji, guild_ids, translated):
    img_path = settings.setup[type]
    new_objects = new[type].copy()

    this_cycle = {}

    total_count = 0

    for id in guild_ids:
        guild = bot.get_guild(id)
        guild_slots = guild.emoji_limit - len(guild.emojis)
        guild_objects = new_objects.copy()
        
        for object in guild_objects:

            if guild_slots <= 0:
                break

            if guild_objects[object]['image'] in added_emoji:   # image path has already been used in the past
                new[type][object]['emoji'] = added_emoji[guild_objects[object]['image']]
                del new_objects[object]
                continue

            elif guild_objects[object]['image'] in this_cycle:  # image path was used during this run of the function
                duplicates[object] = this_cycle[guild_objects[object]['image']]
                del new_objects[object]
                continue

            # image has not been used before

            # changing name if longer than 32 (maximumn length for discord emoji)
            name = object
            if len(object) > 32:
                name = object.split('_')[-1]
                if len(name) > 32:
                    name = name[:32]
                translated[name] = object

            url = guild_objects[object]['image']
            img = BytesIO(requests.get(img_path + url).content)

            try:
                await guild.create_custom_emoji(image=img.getvalue(), name=name)
                del new_objects[object]
                this_cycle[guild_objects[object]['image']] = object
                total_count += 1
                guild_slots -= 1
                print(total_count, guild_slots, '-', guild_objects[object]['name'])

            except Exception as e:
                print(e)

    return new, total_count, duplicates, translated

def get_emoji_ids(bot, guild_ids, new, duplicates, translated):
    for id in guild_ids:
        guild = bot.get_guild(id)
        print('Guild:', guild.name)

        for emoji in guild.emojis:
            name = emoji.name
            if emoji.name in translated:
                name = translated[emoji.name]

            for type in new:
                if name in new[type]:
                    new[type][name]['emoji'] = f'<:{name}:{emoji.id}>'
    
    for object in duplicates:
        for type in new:
            if object in new[type]:
                new[type][object]['emoji'] = new[type][duplicates[object]]['emoji']

    return new

async def setup(bot):
    new = {}
    data = {}
    duplicates = {}
    translated = {}
    total_count = 0

    new['traits'], data['traits'] = get_current_traits()
    new['units'], data['units'] = get_current_units()
    new['augments'], data['augments'] = get_current_augments()
    new['items'], data['items'] = get_current_items()

    slots_required = 0
    for key in new:
        slots_required += len(new[key])

    print(f'Adding {slots_required} objects')

    guild_ids = await get_guild_ids(bot, slots_required)
    if guild_ids == 'cancelled':
        print('successfully cancelled process')
        return
    
    print('Adding emojis to these guilds:', guild_ids)

    if 'added_emoji.json' in os.listdir('data/'):
        with open('data/added_emoji.json', 'r') as f:
            added_emoji = json.load(f)

    for type in ['traits', 'units', 'augments', 'items']:
        new, total_count, duplicates, translated = await add_emoji(bot, type, new, total_count, duplicates, added_emoji, guild_ids, translated)

    print('Successfully added all emojis. Just finishing up...')
    
    new = get_emoji_ids(bot, guild_ids, new, duplicates, translated)

    for type in new:
        for object in new[type]:
            data[type][object] = new[type][object]
            added_emoji[new[type][object]['image']] = new[type][object]['emoji']

        with open(f'data/{type}.json', 'w') as f:
            json.dump(data[type], f, indent=2)

    with open(f'data/added_emoji.json', 'w') as f:
        json.dump(added_emoji, f, indent=2)

    env_file = dotenv.find_dotenv()
    dotenv.load_dotenv()
    old_guild_ids = os.getenv('GUILD_IDS')
    if not old_guild_ids == '':
        guild_ids = old_guild_ids + ', '.join([str(x) for x in guild_ids]) + ', '
    print(guild_ids)
    dotenv.set_key(env_file, 'GUILD_IDS', guild_ids)


    print(f'Successfully added {slots_required} abjects! \nYour Bot is now got to go!')

def recover_from_added_emoji():
    # if an error occurs during the setup process, emojis might be added to discord but not saved in the intended json files.
    # if emoji ids are saved in data/added_emoji.json, they can be added to the intended json files with this function.

    with open('data/added_emoji.json', 'r') as f:
        added_emoji = json.load(f)

    not_added = []

    for name in ['traits', 'units', 'augments', 'items']:	
        with open(f'data/{name}.json', 'r') as f:
            data = json.load(f)

            for object in data:
                if not data[object]['emoji']:
                    try:
                        data[object]['emoji'] = added_emoji[data[object]['image']]
                    except KeyError:
                        if len(object) > 32:
                            try:
                                data[object]['emoji'] = added_emoji[data[object[-32:]]['image']]
                                continue
                            except KeyError:
                                pass
                        not_added.append(object)

        with open(f'data/{name}.json', 'w') as f:
            json.dump(data, f, indent=2)

    print('Could not add the following emojis: \n' + ', '.join(not_added))

def recover_from_discord(bot):
    # if emojis are added to discord but not saved in data/added_emoji.json, use this function to recover emoji ids.

    # store all item paths in data/added_emoji.json with null as value
    # loop over json files to convert image paths to internal names
    # loop over all discord emoji servers 
        # check if any emoji names are part of any internal names
        # if so, add emoji id to data/added_emoji.json 
    # save data/added_emoji.json
    # run recover_from_added_emoji()

    with open('data/added_emoji.json', 'r') as f:
        added_emoji = json.load(f)

    to_recover = set()

    for emoji in added_emoji:
        if not added_emoji[emoji]:
            to_recover.add(emoji)

    internal_names = {}

    for name in ['traits', 'units', 'augments', 'items']:    
        with open(f'data/{name}.json', 'r') as f:
            data = json.load(f)

        for object in data:
            if data[object]['image'] in to_recover:
                name = object
                if len(name) > 32:
                    name = object.split('_')[-1]
                    if len(name) > 32:
                        name = name[:32]
                internal_names[name] = data[object]['image']

    for id in settings.guild_ids:
        guild = bot.get_guild(id)
        
        print('Guild:', guild.name)
        
        for emoji in guild.emojis:
            if emoji.name in internal_names:
                print('recovering', emoji.name)
                added_emoji[internal_names[emoji.name]] = f'<:{emoji.name}:{emoji.id}>'

    with open('data/added_emoji.json', 'w') as f:
        json.dump(added_emoji, f, indent=2)

    recover_from_added_emoji()

#bot.run(settings.TOKEN)