import sqlite3
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, List

from scripts import settings
from scripts.get_embeds import *
from scripts.check_input import *
from scripts.update import *
from scripts.process_data import process_stats, process_traits, process_single_match
from views.statview import StatsView


conn = sqlite3.connect("wclaw.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS links ('discord', 'riot', 'server', 'region', 'puuid', 'summoner_id', 'icon_id', 'rank')")
cur.execute("CREATE TABLE IF NOT EXISTS profile ('puuid', 'riot', 'server', 'region', 'icon_id', 'rank', 'standard', 'turbo', 'pairs', 'last_processed')")
cur.execute("CREATE TABLE IF NOT EXISTS matches ('match_id' INTEGER PRIMARY KEY, 'riot', 'server', 'set_number', 'timestamp', 'placement', 'gamemode', 'level', 'time_spent', 'player_damage', 'players_eliminated', 'traits', 'units', 'augments')")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="$", intents=intents)



@bot.event
async def on_ready():
    print('online')
    await bot.tree.sync()


async def server_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    data = []
    server_list = ['br', 'euw', 'jp', 'lan', 'las', 'na', 'oc', 'ph', 'sg', 'th', 'tr', 'tw', 'vn', 'eune', 'kr', 'ru']
    for server in server_list:
        if current.lower() in server.lower():
            data.append(app_commands.Choice(name=server, value=server))
    return data

@bot.event
async def on_message(ctx):
    if ctx.content == 'was geht':
        embed = single_match_embed('ghosty', '2', 'fuck my life', 4 ,4)
        await ctx.channel.send(embed=embed)

@bot.hybrid_command(description='Shows list of all supported servers')
async def servers(ctx):
    embed = server_embed(ctx.message.author.name)
    await ctx.send(embed=embed, ephemeral=True)



@bot.hybrid_command(description='Link Riot account to your discord account')
@app_commands.autocomplete(server=server_autocomplete)
async def link(ctx, riot_id: str, server: str):
    await ctx.defer()
    author = ctx.message.author.name

    try:
        riot, server, region, puuid, summoner_id, icon_id, rank = check_summoner(riot_id, server)
    except SyntaxError as e:
        embed = error_embed(e, 'Invalid input', str(author))
        await ctx.send(embed=embed)
        return

    #given riot id and server exist

    cur.execute('''
            DELETE FROM links WHERE discord = ?''', (author,))
    cur.execute('''
            INSERT INTO links ('discord', 'riot', 'server', 'region', 'puuid', 'summoner_id', 'icon_id', 'rank')
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (author, riot, server, region, puuid, summoner_id, icon_id, rank))
    conn.commit()

    embed = linked_embed(riot, icon_id, rank, 'Succesfully')

    await ctx.send(embed=embed)

@bot.hybrid_command(description='Shows Riot account linked to your Discord account')
async def linked(ctx):
    author = ctx.message.author.name

    try:
        res = cur.execute('SELECT riot, icon_id, rank FROM links WHERE discord = ?', (author,))
        linked = res.fetchall()[0]
        embed = linked_embed(linked[0], linked[1], linked[2], 'Currently')
    except IndexError:
        embed = error_embed(f"No Riot account linked to '{author}'", 'Not linked', author)
    await ctx.send(embed=embed)

@bot.tree.command(description='Delete information linked to your Discord account')
async def unlink(interaction: discord.Interaction):
    author = interaction.user.name
    cur.execute('''
            DELETE FROM links WHERE discord = ?''', (author,))
    conn.commit()
    await interaction.response.send_message(f'Succesfully unlinked your riot account.', ephemeral=True)

@bot.hybrid_command(description='Update games from linked or specified account')
async def update(ctx, riot_id: Optional[str], server: Optional[str]):
    author = ctx.message.author.name
    await ctx.defer()

    if riot_id or server:
        if not server or not riot_id:
            embed = error_embed('Please enter both Riot id and server or neither.', 'Invalid input', author)
            await ctx.send(embed=embed)
            return
        
        try:
            riot, server, region, puuid, summoner_id, icon_id, rank = check_summoner(riot_id, server)
        except SyntaxError as e:
            embed = error_embed(e, 'Invalid input', str(author))
            await ctx.send(embed=embed)
            return
        
    else:
        try:
            res = cur.execute('SELECT riot, server, region, puuid, rank FROM links WHERE discord = ?', (author,))
            riot, server, region, puuid, rank = res.fetchall()[0]

        except IndexError:
            embed = error_embed(f"No Riot account linked to '{author}'", 'No Link', author)
            await ctx.send(embed=embed)
            return
  
    try:
        icon_id, count, data = get_matchids(riot, server, region, puuid, cur)
    except NameError as error:
        conn.commit()
        embed = error_embed(error, 'No games found', author)
        await ctx.send(embed=embed)
        return
    
    update_games(cur, data)
    conn.commit()
    embed = update_embed(riot, icon_id, count)
    await ctx.send(embed=embed)

@bot.hybrid_command(description='Shows stats for linked or specified Account')
async def stats(ctx, riot_id: Optional[str], server: Optional[str], count: Optional[int], days: Optional[int], set: Optional[float] = settings.CURRENT_SET):
    await ctx.defer()
    author = ctx.message.author.name

    if set > settings.CURRENT_SET:
        embed = error_embed(f"{set} is not a valid set number.", 'Invalid Set Number', author)
        await ctx.send(embed=embed)
        return
    
    if riot_id or server:
        if not server or not riot_id:
            embed = error_embed('Please enter both Riot id and server or neither.', 'Invalid input', author)
            await ctx.send(embed=embed)
            return
        
        if not server in server_list:
            embed = error_embed(f'`{server}` is not supported a server', 'Invalid input', str(author))
            await ctx.send(embed=embed)
            return
        
        server = server_list[server]['server']
        
        try:
            res = cur.execute("SELECT riot, server, icon_id, rank FROM profile WHERE riot = ? AND server = ?", (riot_id, server))
            riot, server, icon_id, rank = res.fetchall()[0]
        except IndexError:
            embed = error_embed(f'No games found for `{riot_id}` on {server}. Make sure to use /update first', 'Invalid input', str(author))
            await ctx.send(embed=embed)
            return

    else:
        try:
            res = cur.execute('SELECT riot, server, icon_id, rank FROM links WHERE discord = ?', (author,))
            riot, server, icon_id, rank = res.fetchall()[0]
        except IndexError:
            embed = error_embed(f"No Riot account linked to '{author}'", 'Nothing linked', author)
            await ctx.send(embed=embed)
            return

    try:
        data, x = process_stats(cur, riot, server, count, days, set)
    except IndexError as e:
        embed = error_embed(f"No games from {riot} found. \nMake sure to use /update first.", 'No games found', author)
        await ctx.send(embed=embed)
        return
    
    embed = stats_embed(data, author, riot, icon_id, rank)
    view = StatsView(cur, data, author, riot, server, icon_id, rank, count, days, set)
    view.message = await ctx.send(embed=embed, view=view)

@bot.hybrid_command(description='Show details about specific match. Get match ids from /matchhistory (defaults to most recent match)')
async def single_game(ctx, match_id: Optional[str], riot_id: Optional[str], server: Optional[str]):
    author = ctx.message.author.name

    if riot_id or server:
        if not server or not riot_id:
            embed = error_embed('Please enter both Riot id and server or neither.', 'Invalid input', author)
            await ctx.send(embed=embed)
            return
        
        if not server in server_list:
            embed = error_embed(f'`{server}` is not supported a server', 'Invalid input', str(author))
            await ctx.send(embed=embed)
            return
        
        server = server_list[server]['server']
        
        try:
            res = cur.execute("SELECT riot, server, icon_id, rank FROM profile WHERE riot = ? AND server = ?", (riot_id, server))
            riot, server, icon_id, rank = res.fetchall()[0]
        except IndexError:
            embed = error_embed(f'No games found for `{riot_id}` on {server}. Make sure to use /update first', 'Invalid input', str(author))
            await ctx.send(embed=embed)
            return

    else:
        try:
            res = cur.execute('SELECT riot, server, icon_id, rank FROM links WHERE discord = ?', (author,))
            riot, server, icon_id, rank = res.fetchall()[0]
        except IndexError:
            embed = error_embed(f"No Riot account linked to '{author}'", 'Nothing linked', author)
            await ctx.send(embed=embed)
            return
        
    try:
        data = process_single_match(cur, riot, server, match_id)
    except IndexError as e:
        embed = error_embed(f"No games from {riot} found. \nMake sure to use /update first.", 'No games found', author)
        await ctx.send(embed=embed)
        return
    
    embed = single_match_embed(data, author, riot, icon_id, rank)
    await ctx.send(embed=embed)

bot.run(settings.TOKEN)