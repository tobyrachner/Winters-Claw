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
from discord import app_commands

from scripts import settings

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="$", intents=intents)


@bot.event
async def on_ready():
    print('online')
    await bot.tree.sync()

@bot.event
async def on_message(ctx):
    pass

def get_current_augments():
    augments = requests.get(f'https://ddragon.leagueoflegends.com/cdn/{settings.CURRENT_PATCH}/data/en_US/tft-augments.json').json()['data']

    with open('data/augments.json', 'w') as f:
        json.dump(augments, f, indent=2)
    with open('data/temp_augments.json', 'w') as f:
        json.dump(augments, f, indent=2)

async def add_augment_emoji(ctx):
    augment_guild_ids = [1226021957963743262, 1226022008643518526, 1226022064897392660, 1226022118664437872, 1226022170291867669, 1226022232007114823]
    if ctx.content == 'wc create emoji':
        overall_count = 0

        with open('data/temp_augments.json', 'r') as f:
            augments = json.load(f)
            new_augments = augments.copy()

        if not ctx.author.guild_permissions.manage_emojis:
            return
        
        for id in augment_guild_ids:
            guild = bot.get_guild(id)
            print(guild.name)
            guild_count = 0
            guild_augments = new_augments.copy()
        
            for augment in guild_augments:
                url = augments[augment]['image']
                img = BytesIO(requests.get('https://raw.communitydragon.org/latest/game/assets/maps/tft/icons/augments/choiceui/' + url.lower()).content)

                # replacing all the special characters used in Augment Names [',', '+', '-', '!', '''] with letters because discord emojis do not accept special characters
                name = augments[augment]['name'].replace(' ', '').replace(',', 'AAA').replace('+', 'BBB').replace('-', 'CCC').replace('!', 'DDD').replace("'", 'EEE')

                try:
                    await guild.create_custom_emoji(image=img.getvalue(), name=name)
                    del new_augments[augment]
                    overall_count += 1
                    guild_count += 1
                    print(overall_count, guild_count, '-', augments[augment]['name'])

                    sleep(5.1)  # waiting to avoid discord rate limit
                    if guild_count >= 50:
                        break
                except Exception as e:
                    print(e)
                    break

        with open('data/temp_augments.json', 'w') as f:
            json.dump(new_augments, f, indent=2)

def get_augment_emoji_ids():
    augment_guild_ids = [1226021957963743262, 1226022008643518526, 1226022064897392660, 1226022118664437872, 1226022170291867669, 1226022232007114823]

    with open('data/augments.json', 'r') as f:
        augments = json.load(f)

    with open('data/augment_emoji.json', 'r') as f:
        augment_emoji = json.load(f)

    names = {}
    for augment in augments:
        name = augments[augment]['name'].replace(' ', '').replace(',', 'AAA').replace('+', 'BBB').replace('-', 'CCC').replace('!', 'DDD').replace("'", 'EEE')
        names[name] = augments[augment]['name']

    for id in augment_guild_ids:
        guild = bot.get_guild(id)
        print(guild.name)
        for emoji in guild.emojis:
            if emoji.name in names:
                name = names[emoji.name]
                augment_emoji[name] = f'<:{emoji.name}:{emoji.id}>'

    with open('data/augment_emoji.json', 'w') as f:
        json.dump(augment_emoji, f, indent=2)

    return

bot.run(settings.ADMIN_TOKEN)