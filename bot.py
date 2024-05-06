from typing import Optional, List, Literal

import sqlite3
import aiohttp
import discord
from discord.ext import commands
from discord import app_commands

from scripts import settings
from scripts.get_embeds import *
from scripts.check_input import *
from scripts.update import *
from scripts.process_data import process_stats, process_single_match, process_history
from views.statview import StatsView
from views.matchview import MatchView
from views.historyview import HistoryView

COMMANDS = ['help', 'commands', 'servers', 'link', 'linked', 'unlink', 'stats', 'update', 'matchhistory', 'singlematch']

conn = sqlite3.connect("wclaw.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS links ('discord', 'puuid')")
cur.execute("CREATE TABLE IF NOT EXISTS profile ('puuid', 'riot', 'server', 'region', 'icon_id', 'rank', 'standard', 'turbo', 'pairs', 'last_processed')")
cur.execute("CREATE TABLE IF NOT EXISTS matches ('match_id' INTEGER PRIMARY KEY, 'puuid', 'set_number', 'timestamp', 'placement', 'gamemode', 'level', 'time_spent', 'player_damage', 'players_eliminated', 'traits', 'units', 'augments')")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="$", intents=intents)
bot.remove_command('help')

@bot.event
async def on_ready():
    print('online')
    bot.session = aiohttp.ClientSession()

@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    print('syncing')
    if not guilds:

        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

async def server_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    data = []
    server_list = ['br', 'euw', 'jp', 'lan', 'las', 'na', 'oc', 'ph', 'sg', 'th', 'tr', 'tw', 'vn', 'eune', 'kr', 'ru']
    for server in server_list:
        if current.lower() in server.lower():
            data.append(app_commands.Choice(name=server, value=server))
    return data

async def command_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    data = []
    for command in COMMANDS:
        if current.lower() in command.lower():
            data.append(app_commands.Choice(name=command, value=command))
    return data

@bot.hybrid_command(description='If you ever need help')
async def help(ctx):
    embed = help_embed()
    await ctx.send(embed=embed)

@bot.hybrid_command(description='List of all available commands')
@app_commands.autocomplete(command=command_autocomplete)
async def commands(ctx, command: Optional[str]):
    if command and not command in COMMANDS:
        embed = error_embed('Please enter a valid command name.', 'Invalid command')
        await ctx.send(embed=embed, ephemeral=True)
    else:
        embed = commands_embed(command)
        await ctx.send(embed=embed)

@bot.hybrid_command(description='Shows list of all supported servers')
async def servers(ctx):
    embed = server_embed()
    await ctx.send(embed=embed, ephemeral=True)

@bot.hybrid_command(description='Link Riot account to your discord account')
@app_commands.autocomplete(server=server_autocomplete)
async def link(ctx, riot_id: str, server: str):
    await ctx.defer()
    discord_id = ctx.message.author.id

    try:
        riot, server, region, puuid, summoner_id, icon_id, rank = await check_summoner(bot.session, riot_id, server)
    except SyntaxError as e:
        embed = error_embed(e, 'Invalid input')
        await ctx.send(embed=embed, ephemeral=True)
        return

    #given riot id and server exist

    cur.execute('''
            DELETE FROM links WHERE discord = ?''', (discord_id,))
    cur.execute('''
            INSERT INTO links ('discord', 'puuid')
            VALUES (?, ?)''', (discord_id, puuid))
    
    test = cur.execute('SELECT * FROM profile WHERE puuid = ?', (puuid,)).fetchone()
    if test is None:
        cur.execute("INSERT INTO profile ('riot', 'server', 'region', 'puuid', 'icon_id', 'rank') VALUES (?, ?, ?, ?, ?, ?)", (riot, server, region, puuid, icon_id, rank))
    conn.commit()

    embed = linked_embed(riot, icon_id, rank, 'Succesfully')

    await ctx.send(embed=embed)

@bot.hybrid_command(description='Shows Riot account linked to your Discord account')
async def linked(ctx):
    discord_id = ctx.message.author.id

    try:
        puuid = cur.execute('SELECT puuid FROM links WHERE discord = ?', (discord_id,)).fetchone()[0]
        linked = cur.execute('SELECT riot, icon_id, rank FROM profile WHERE puuid = ?', (puuid,)).fetchone()
        embed = linked_embed(linked[0], linked[1], linked[2], 'Currently')
    except TypeError or ValueError:
        embed = error_embed(f"No Riot account linked to '{ctx.message.author.name}'", 'Not linked')
    await ctx.send(embed=embed, ephemeral=True)

@bot.hybrid_command(description='Delete information linked to your Discord account')
async def unlink(ctx):
    cur.execute('''
            DELETE FROM links WHERE discord = ?''', (ctx.message.author.id,))
    conn.commit()
    await ctx.send(f'Succesfully unlinked your riot account.', ephemeral=True)

@bot.hybrid_command(description='Update games from linked or specified account')
async def update(ctx, riot_id: Optional[str], server: Optional[str]):
    await ctx.defer()

    if riot_id or server:
        if not server or not riot_id:
            embed = error_embed('Please enter both Riot id and server or neither.', 'Invalid input')
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        try:
            riot, server, region, puuid, summoner_id, icon_id, rank = await check_summoner(bot.session, riot_id, server)
        except SyntaxError as e:
            embed = error_embed(e, 'Invalid input')
            await ctx.send(embed=embed, ephemeral=True)
            return
        
    else:
        try:
            puuid = cur.execute('SELECT puuid FROM links WHERE discord = ?', (ctx.message.author.id,)).fetchone()[0]
            riot, server, region, rank = cur.execute('SELECT riot, server, region, rank FROM profile WHERE puuid = ?', (puuid,)).fetchone()
        except TypeError:
            embed = error_embed(f"No Riot account linked to your discord", 'Nothing linked')
            await ctx.send(embed=embed, ephemeral=True)
            return
  
    try:
        icon_id, count, data = await get_matchids(bot.session, riot, server, region, puuid, cur)
    except NameError as error:
        conn.commit()
        embed = error_embed(error, 'No games found')
        await ctx.send(embed=embed, ephemeral=True)
        return
    
    await update_games(bot.session, cur, data)
    conn.commit()
    embed = update_embed(riot, icon_id, count)
    await ctx.send(embed=embed)

@bot.hybrid_command(description='Shows stats for linked or specified Account')
async def stats(ctx, riot_id: Optional[str], server: Optional[str], count: Optional[int], days: Optional[int], set: Optional[float] = settings.CURRENT_SET):
    await ctx.defer()
    author = ctx.message.author.name

    if set > settings.CURRENT_SET:
        embed = error_embed(f"{set} is not a valid set number.", 'Invalid Set Number')
        await ctx.send(embed=embed, ephemeral=True)
        return
    
    if riot_id or server:
        if not server or not riot_id:
            embed = error_embed('Please enter both Riot id and server or neither.', 'Invalid input')
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        if not server in server_list:
            embed = error_embed(f'`{server}` is not supported a server', 'Invalid input')
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        server = server_list[server]['server']
        
        try:
            riot, server, region, puuid, summoner_id, icon_id, rank = await check_summoner(bot.session, riot_id, server)
        except Exception as e:
            embed = error_embed(e, 'Invalid input')
            await ctx.send(embed=embed, ephemeral=True)
            return

    else:
        try:
            puuid = cur.execute('SELECT puuid FROM links WHERE discord = ?', (ctx.message.author.id,)).fetchone()[0]
            riot, server, icon_id, rank = cur.execute('SELECT riot, server, icon_id, rank FROM profile WHERE puuid = ?', (puuid,)).fetchone()
        except TypeError:
            embed = error_embed(f"No Riot account linked to your discord", 'Nothing linked')
            await ctx.send(embed=embed, ephemeral=True)
            return

    try:
        data, x = process_stats(cur, riot, server, count, days, set)
    except IndexError as e:
        embed = error_embed(f"No games from {riot} found. \nMake sure to use /update first.", 'No games found')
        await ctx.send(embed=embed, ephemeral=True)
        return
    
    embed = stats_embed(data, author, riot, icon_id, rank)
    view = StatsView(cur, author, ctx.message.author.id, data, riot, server, icon_id, rank, count, days, set)
    view.message = await ctx.send(embed=embed, view=view)

@bot.hybrid_command(description='Show details about specific match. Get match ids from /matchhistory (defaults to most recent match)')
async def singlematch(ctx, match_id: Optional[int], riot_id: Optional[str], server: Optional[str]):
    if riot_id or server:
        if not server or not riot_id:
            embed = error_embed('Please enter both Riot id and server or neither.', 'Invalid input')
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        if not server in server_list:
            embed = error_embed(f'`{server}` is not supported a server', 'Invalid input')
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        server = server_list[server]['server']
        
        try:
            riot, server, region, puuid, summoner_id, icon_id, rank = await check_summoner(bot.session, riot_id, server)
        except Exception as e:
            embed = error_embed(e, 'Invalid input')
            await ctx.send(embed=embed, ephemeral=True)
            return

    else:
        try:
            puuid = cur.execute('SELECT puuid FROM links WHERE discord = ?', (ctx.message.author.id,)).fetchone()[0]
            riot, server, icon_id, rank = cur.execute('SELECT riot, server, icon_id, rank FROM profile WHERE puuid = ?', (puuid,)).fetchone()
        except ValueError or TypeError:
            embed = error_embed(f"No Riot account linked to your discord", 'Nothing linked')
            await ctx.send(embed=embed, ephemeral=True)
            return
        
    try:
        match_ids = cur.execute('SELECT match_id FROM matches WHERE puuid = ? ORDER BY timestamp DESC', (puuid,)).fetchall()
        match_ids = [id[0] for id in match_ids]
        if len(match_ids) == 0:
            raise IndexError()
        if match_id:
            id_index = match_ids.index(match_id)
        else:
            id_index = 0
        data = process_single_match(cur, riot, server, match_id)
    except IndexError as e:
        embed = error_embed(e, 'Game not found')
        await ctx.send(embed=embed, ephemeral=True)
        return
    
    embed = single_match_embed(data, riot, icon_id, rank)
    view = MatchView(cur, ctx.message.author.id, match_ids, riot, server, icon_id, rank, id_index=id_index)
    view.message = await ctx.send(embed=embed, view=view)

@bot.hybrid_command(description='Shows general information about most recent games played')
async def matchhistory(ctx, riot_id: Optional[str], server: Optional[str]):
    author = ctx.message.author.name

    if riot_id or server:
        if not server or not riot_id:
            embed = error_embed('Please enter both Riot id and server or neither.', 'Invalid input')
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        if not server in server_list:
            embed = error_embed(f'`{server}` is not supported a server', 'Invalid input')
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        server = server_list[server]['server']
        
        try:
            riot, server, region, puuid, summoner_id, icon_id, rank = await check_summoner(bot.session, riot_id, server)
        except Exception as e:
            embed = error_embed(e, 'Invalid input')
            await ctx.send(embed=embed, ephemeral=True)
            return

    else:
        try:
            puuid = cur.execute('SELECT puuid FROM links WHERE discord = ?', (ctx.message.author.id,)).fetchone()[0]
            riot, server, icon_id, rank = cur.execute('SELECT riot, server, icon_id, rank FROM profile WHERE puuid = ?', (puuid,)).fetchone()
        except ValueError or TypeError:
            embed = error_embed(f"No Riot account linked to your discord", 'Nothing linked')
            await ctx.send(embed=embed, ephemeral=True)
            return
        
    data = process_history(cur, riot, server)
    embed = history_embed(data, riot, icon_id, rank)
    view = HistoryView(cur, ctx.message.author.id, data, riot, server, icon_id, rank)
    view.message = await ctx.send(embed=embed, view=view)

bot.run(settings.TOKEN)