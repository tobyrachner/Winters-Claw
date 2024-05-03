import datetime
import discord

from scripts.settings import trait_list, augment_list, unit_list, item_list, trait_emoji, augment_emoji, unit_emoji, item_emoji, misc_emoji

PLACEMENTS = {1: '1st', 2: '2nd', 3: '3rd', 4: '4th', 5: '5th', 6: '6th', 7: '7th', 8: '8th'}
ALL_COMMANDS = {'help': ['`/help`', 'Offers general help'],
                'commands': ['`/commands [command]`', 'Shows a list of all available commands or more information about the given command.'],
                'servers': ['`/servers`', 'Shows a list of all supported servers'],
                'link': ['`/link [riotId] [server]`', ' Link a summoner to your discord username to quickly use all other commands. \n Riot IDs must be in the format of sample#000 \n A list of all supported servers can be found with `/servers`.'],
                'linked': ['`/linked`', 'Shows summoner currently linked to your discord username.'],
                'unlink': ['`/unlink`', 'Delete all information linked to your discord username.'],
                'update': ['`/update [riotId] [server]`', 'Download all games for entered summoner (defaults to linked summoner). \n Downloads all games played in the current set or since the last time used. \n This may take 1 or 2 minutes if more than 100 games are getting downloaded.'],
                'stats': ['`/stats [days] [count] [set] [riotId] [server]`', 'Shows all your statistics for gamemodes, traits, units and augments. \n Parameters can be used to only show data from the last x games or days or a specific set. \n More information can be viewed using the buttons provided.'],
                'matchhistory': ['`/matchhistory [riotId] [server]`', 'Shows information about the recent 6 matches from a summoner. \n More games can be viewed by using the buttons.'],
                'singlematch': ['`/singlematch [matchId] [riotId] [server]`', 'Shows details about a specfic match for given or linked summoner. \n Match IDs are obtainable through `/match_history` (defaults to last match played)']}


def error_embed(message, error_type):
    embed=discord.Embed(title=error_type, description=message, color=0x7011d0,)
    embed.set_thumbnail(url='https://wintersclaw-lol.vercel.app/poro.png')
    embed.timestamp = datetime.datetime.utcnow()
    return embed

def help_embed():
    embed=discord.Embed(title='/help', description='''Use `/commands` for a list of commands''', color=0x1386ec)
    embed.add_field(name='Quickstart', value='''1. `/link`   to link your Riot account to your discord
2. `/update` to download games into database
3. `/stats`  for overall stats on your account''', inline=False)
    embed.add_field(name='Note', value='''- All stat commands take an optional input for Riot accounts. If not given it defaults to your linked account.
- `riotId` must be in the format of `user#0000` 
- use `/servers` for a list of all supported servers
- Capitalization for Riot IDs **matters**''')
    return embed

def commands_embed(command):
    if command is None:
        ephemeral = False
        embed = discord.Embed(title='Winter\'s Claw commands', description='''Use `/commands [command]` for more information on a single command''', color=0x1386ec)
        embed.add_field(name='Stat commands', value='`/stats`  - >  General statistics for your account', inline=False)
        embed.add_field(name='', value='`/singlematch`  - >  Detailed data for a single match', inline=False)
        embed.add_field(name='', value='`/matchhistory`  - >  Data for most recent matches played', inline=False)
        embed.add_field(name='Other commands', value='`/commands`  - >  Shows this message', inline=True)
        for command in ['`/help`  - >  For general help', 
                        '`/servers`  - >  Shows a list of all supported servers', 
                        '`/link`  - >  Link a summoner to your discord account', 
                        '`/linked`  - >  Show summoner linked to your discord account', 
                        '`/unlink`  - >  Delete all data linked to your discord account', 
                        '`/update`  - >  Download new games from your account into database']:
            embed.add_field(name='', value=command, inline=False)
    else:
        ephemeral = True
        title, field = ALL_COMMANDS[command]
        embed = discord.Embed(title=title, description='', color=0x1386ec)
        embed.add_field(name='', value=field, inline=False)
    return embed, ephemeral

def linked_embed(riot, icon_id, rank, text):
    name = riot.replace('%20', ' ')
    embed=discord.Embed(title=f"{name} {rank.split(' ')[0]}", description='', color=0x1386ec, url=f'')
    embed.set_author(name=f'{text} linked:')
    embed.set_thumbnail(url=f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{icon_id}.jpg')
    embed.add_field(name='to your Discord account.', value='')
    embed.timestamp = datetime.datetime.utcnow()
    return embed

def server_embed():
    embed = discord.Embed(title = 'Server', color=0x1386ec)

    embed.add_field(name="Europe", inline=True, value="""
```fix
Europe West       - > EUW 
Europe Northeast  - > EUNE    
Turkey            - > TR
Russia            - > RU```""")
    
    embed.add_field(name='America', inline=True, value="""
```fix
North America       - > NA
Latinamerica North  - > LAN
Latinamerica South  - > LAS
Brasil              - > BR```""")
    
    embed.add_field(name='', value='', inline=True)

    embed.add_field(name='Sea', inline=True, value="""
```fix
Oceania             - > OC
Philippines         - > PH
Singapoure          - > SG
Taiwan              - > TW
Thailand            - > TH```""")
    
    embed.add_field(name='Asia', inline=True, value="""
```fix
Japan               - > JP
Korea               - > KR```""")

    
    embed.add_field(name='', value='', inline=True)
    return embed

def stats_embed(data, author, riot, icon_id, rank, mode_name='All Modes', index=None):
    rank_icon = rank.split(' ')[0]
    
    embed=discord.Embed(title=riot + ' ' + rank_icon, description='', color=0x1386ec, url=f'')
    embed.set_thumbnail(url=f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{icon_id}.jpg')
    embed.add_field(name=f"{mode_name} - {data['count']} games", 
                    value=f"""{rank}
Avg Placement - {data['avg']} 
Top% - {data['top%']}% 
Win% - {data['win%']}%
Total damage to players - {data['player_damage']}
Total players eliminated - {data['players_eliminated']}
Time spent ingame - {data['time_spent']}h""", inline=False)
 
    embed.set_footer(text='Use buttons to customize data')
    return embed

def update_embed(riot, icon_id, count):
    name = riot.replace('%20', ' ')
    embed=discord.Embed(title=name, description='', color=0x1386ec, url=f'')
    embed.set_thumbnail(url=f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{icon_id}.jpg')
    if count == 0:
        embed.set_author(name=f'No new games to add to:')
    else:
        embed.set_author(name=f'Succesfully added {count} games to:')
    embed.add_field(name='Your profile is up to date.', value='')
    embed.timestamp = datetime.datetime.utcnow()
    return embed

def traits_embed(data, author, riot, icon_id, rank, index=0, mode_name='All Modes'):
    rank_icon = rank.split(' ')[0]

    embed=discord.Embed(title=riot + ' ' + rank_icon, description='', color=0x1386ec, url=f'')
    embed.set_thumbnail(url=f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{icon_id}.jpg')
    embed.add_field(name=f"{mode_name} - {data['count']} games", value='', inline=False)
    for i in range(2):
        if index < len(data['traits']):
            trait = data['traits'][index][0]
            embed.add_field(name=f"{trait_list[trait]['emoji']} {trait_list[trait]['name']} - {data['traits'][index][1]['count']}",
                            value=f"""{' '.join([trait_emoji['level'][str(level)] + str(amount) for level, amount in data['traits'][index][1]['level'].items()])}
                            Avg Placement - {data['traits'][index][1]['avg']}
                            Top 4% - {data['traits'][index][1]['top4%']}%
                            Win% - {data['traits'][index][1]['win%']}%
                            ⠀""",
                            inline=True)
        else:
            embed.add_field(name='  ', value='', inline=True)

        embed.add_field(name='  ', value='', inline=True)

        if index + 1 < len(data['traits']):
            trait = data['traits'][index + 1][0]
            embed.add_field(name=f"{trait_list[trait]['emoji']} {trait_list[trait]['name']} - {data['traits'][index + 1][1]['count']}",
                            value=f"""{' '.join([trait_emoji['level'][str(level)] + str(amount) + '' for level, amount in data['traits'][index + 1][1]['level'].items()])}
                            Avg Placement - {data['traits'][index + 1][1]['avg']}
                            Top 4% - {data['traits'][index + 1][1]['top4%']}%
                            Win% - {data['traits'][index + 1][1]['win%']}%""",
                            inline=True)
        else:
            embed.add_field(name='  ', value='', inline=True)
        index += 2
    embed.set_footer(text='Use buttons to customize data')
    return embed

def augments_embed(data, author, riot, icon_id, rank, index=0, mode_name='All Modes'):
    rank_icon = rank.split(' ')[0]

    embed=discord.Embed(title=riot + ' ' + rank_icon, description='', color=0x1386ec, url=f'')
    embed.set_thumbnail(url=f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{icon_id}.jpg')
    embed.add_field(name=f"{mode_name} - {data['count']} games", value='', inline=False)
    for i in range(2):
        if index < len(data['augments']):
            augment = data['augments'][index][0]
            embed.add_field(name=f"{augment_list[augment]['emoji']} {augment_list[augment]['name']} - {data['augments'][index][1]['count']}",
                            value=f""" Avg Placement - {data['augments'][index][1]['avg']}
                            Top 4% - {data['augments'][index][1]['top4%']}%
                            Win% - {data['augments'][index][1]['win%']}%""",
                            inline=True)
        else:
            embed.add_field(name='  ', value='', inline=True)

        embed.add_field(name='  ', value='', inline=True)

        index += 1
        if index < len(data['augments']):
            augment = data['augments'][index][0]
            embed.add_field(name=f"{augment_list[augment]['emoji']} {augment_list[augment]['name']} - {data['augments'][index][1]['count']}",
                            value=f""" Avg Placement - {data['augments'][index][1]['avg']}
                            Top 4% - {data['augments'][index][1]['top4%']}%
                            Win% - {data['augments'][index][1]['win%']}%""",
                            inline=True)
        else:
            embed.add_field(name='  ', value='', inline=True)
        index += 1
    embed.set_footer(text='Use buttons to customize data')
    return embed

def units_embed(data, author, riot, icon_id, rank, index=0, mode_name='All Modes'):
    rank_icon = rank.split(' ')[0]

    embed=discord.Embed(title=riot + ' ' + rank_icon, description='', color=0x1386ec, url=f'')
    embed.set_thumbnail(url=f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{icon_id}.jpg')
    embed.add_field(name=f"{mode_name} - {data['count']} games", value='', inline=False)
    for i in range(2):
        if index < len(data['units']):
            unit = data['units'][index][1]
            name = data['units'][index][0]
            embed.add_field(name=f"{unit_list[name]['emoji']} {unit_list[name]['name']} - {unit['count']}",
                            value=f"""{' '.join([f"{misc_emoji['star_level'][str(level)]} {unit['level'][level]}" for level in unit['level']])}
                            {'⠀'.join([item_list[item]['emoji'] + ' ' + str(unit['items'][item]) for item in unit['items']])}
                            Avg Placement - {unit['avg']}
                            Top 4% - {unit['top4%']}%
                            Win% - {unit['win%']}%
                            ⠀""", # invisible charcter to add more vertical space between rows
                            inline=True)
        else:
            embed.add_field(name='  ', value='', inline=True)

        embed.add_field(name='  ', value='', inline=True)

        index += 1
        if index < len(data['units']):
            unit = data['units'][index][1]
            name = data['units'][index][0]

            embed.add_field(name=f"{unit_list[name]['emoji']} {unit_list[name]['name']} - {unit['count']}",
                            value=f"""{' '.join([f"{misc_emoji['star_level'][str(level)]} {unit['level'][level]}" for level in unit['level']])}
                            {'⠀'.join([item_list[item]['emoji'] + '' + str(unit['items'][item]) for item in unit['items']])}
                            Avg Placement - {unit['avg']}
                            Top 4% - {unit['top4%']}%
                            Win% - {unit['win%']}%""",
                            inline=True)
        else:
            embed.add_field(name='  ', value='', inline=True)
        index += 1
    embed.set_footer(text='Use buttons to customize data')
    return embed

def single_match_embed(data, riot, icon_id, rank):
    rank_icon = rank.split(' ')[0]
    
    embed=discord.Embed(title=riot + ' ' + rank_icon, description='', color=0x1386ec, url=f'')
    embed.set_thumbnail(url=f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{icon_id}.jpg')
    embed.add_field(name=f"Game Info", 
                    value=f"""<t:{data['timestamp']}>
{data['gamemode']}
Level {data['level']}
{PLACEMENTS[data['placement']]} Place""", inline=False)
    embed.add_field(name="Augments",
                    value='\n'.join([augment_list[augment]['emoji'] + ' ' + augment_list[augment]['name'] for augment in data['augments']]), inline=False)
    embed.add_field(name="Traits", inline=False, value='\n'.join([f"{trait_list[trait]['emoji']} {trait_list[trait]['name']} | {trait_emoji['level'][data['traits'][trait]['level']]} {data['traits'][trait]['num_units']}" for trait in data['traits']]))
    embed.add_field(name="Units", value='', inline=False)
    for unit in data['units']:
        text = f'{unit_list[unit]["emoji"]} {unit_list[unit]["name"]} {misc_emoji["star_level"][data["units"][unit]["level"]]}⠀|⠀'
        if len(data['units'][unit]["items"]) > 0:
            text += ' '.join([item_list[item]['emoji'] for item in data['units'][unit]['items']])
        embed.add_field(name='',
                        value=text, inline=False)

    embed.set_footer(text='Use buttons to customize data')
    return embed

def history_embed(data, riot, icon_id, rank, stat_type='general', index=0, show_ids=False):
    rank_icon = rank.split(' ')[0]

    function_class = HistoryEmbed()
    functions = {'general': function_class.general, 'traits': function_class.traits, 'augments': function_class.augments, 'units': function_class.units}
    rows = {'general': 4, 'augments': 4, 'units': 2, 'traits': 3}
    
    embed=discord.Embed(title=riot + ' ' + rank_icon, description='', color=0x1386ec, url=f'')
    embed.set_thumbnail(url=f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{icon_id}.jpg')
    for i in range(3):
        if len(data) > index:
            id = ''
            if show_ids:
                id = f"ID: {data[index]['id']}\n"
            functions[stat_type](embed, data, index, id)
        embed.add_field(name='', value='', inline=True)
        index += 1
        if len(data) > index:
            id = ''
            if show_ids:
                id = f"ID: {data[index]['id']}\n"
            functions[stat_type](embed, data, index, id)
        index += 1
    embed.set_footer(text='Use buttons to customize data')
    return embed

class HistoryEmbed():
    def __init__(self):
        pass

    def general(self, embed, data, index, id):
        embed.add_field(name=PLACEMENTS[data[index]['placement']] + ' Place', value=f'''{id} <t:{data[index]['timestamp']}>
{data[index]['gamemode']}
Level {data[index]['level']}''', inline=True)
        
    def augments(self, embed, data, index, id):
        embed.add_field(name=PLACEMENTS[data[index]['placement']] + ' Place', value=id + '\n'.join([augment_list[augment]['emoji'] + ' ' + augment_list[augment]['name'] for augment in data[index]['augments']]), inline=True)
    
    def traits(self, embed, data, index, id):
        embed.add_field(name=PLACEMENTS[data[index]['placement']] + ' Place', inline=True, value=id + '\n'.join([f"{trait_list[trait]['emoji']} {trait_list[trait]['name']} | {trait_emoji['level'][data[index]['traits'][trait]['level']]} {data[index]['traits'][trait]['num_units']}" for trait in data[index]['traits']]))

    def units(self, embed, data, index, id):
        text = '\n'.join([f'{unit_list[unit]["emoji"]} {unit_list[unit]["name"]} {misc_emoji["star_level"][data[index]["units"][unit]["level"]]}' for unit in data[index]['units']])
        embed.add_field(name=PLACEMENTS[data[index]['placement']] + ' Place', value=id + text, inline=True)