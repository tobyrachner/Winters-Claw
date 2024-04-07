import discord

from scripts.settings import trait_emoji, augment_emoji, unit_emoji, item_emoji, misc_emoji

def linked_embed(riot, icon_id, rank, text):
    name = riot.replace('%20', ' ')
    embed=discord.Embed(title=f"{name} {rank.split(' ')[0]}", description='', color=0x7011d0, url=f'')
    embed.set_author(name=f'{text} linked:')
    embed.set_thumbnail(url=f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{icon_id}.jpg')
    embed.add_field(name='to your Discord account.', value='')
    return embed

def updating_embed(riot, icon_id, count):
    name = riot.replace('%20', ' ')
    embed=discord.Embed(title=name, description='', color=0x7011d0, url=f'')
    embed.set_thumbnail(url=f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{icon_id}.jpg')
    embed.set_author(name=f'Downloading {count} games ...')
    embed.add_field(name='(This might take a while)', value='')
    return embed

def update_embed(riot, icon_id, count):
    name = riot.replace('%20', ' ')
    embed=discord.Embed(title=name, description='', color=0x7011d0, url=f'')
    embed.set_thumbnail(url=f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{icon_id}.jpg')
    if count == 0:
        embed.set_author(name=f'No new games to add to:')
    else:
        embed.set_author(name=f'Succesfully added {count} games to:')
    embed.add_field(name='Your profile is up to date.', value='')
    return embed

def traits_embed(data, author, riot, icon_id, rank, index=0, mode_name='All Modes'):
    rank_icon = rank.split(' ')[0]

    embed=discord.Embed(title=riot + ' ' + rank_icon, description='', color=0x7011d0, url=f'')
    embed.set_thumbnail(url=f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{icon_id}.jpg')
    embed.add_field(name=f"{mode_name} - {data['count']} games", value='', inline=False)
    for i in range(2):
        if index < len(data['traits']):
            trait = data['traits'][index][0]
            embed.add_field(name=f"{trait_emoji[trait]} {trait} - {data['traits'][index][1]['count']}",
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
            trait2 = data['traits'][index + 1][0]
            embed.add_field(name=f"{trait_emoji[trait2]} {trait2} - {data['traits'][index + 1][1]['count']}",
                            value=f"""{' '.join([trait_emoji['level'][str(level)] + str(amount) + '' for level, amount in data['traits'][index + 1][1]['level'].items()])}
                            Avg Placement - {data['traits'][index + 1][1]['avg']}
                            Top 4% - {data['traits'][index + 1][1]['top4%']}%
                            Win% - {data['traits'][index + 1][1]['win%']}%""",
                            inline=True)
        else:
            embed.add_field(name='  ', value='', inline=True)
        index += 2
    embed.set_footer(text=f'Games since: {data["display_date"]}')
    return embed

def augments_embed(data, author, riot, icon_id, rank, index=0, mode_name='All Modes'):
    rank_icon = rank.split(' ')[0]

    embed=discord.Embed(title=riot + ' ' + rank_icon, description='', color=0x7011d0, url=f'')
    embed.set_thumbnail(url=f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{icon_id}.jpg')
    embed.add_field(name=f"{mode_name} - {data['count']} games", value='', inline=False)
    for i in range(2):
        if index < len(data['augments']):
            augment = data['augments'][index][0]
            embed.add_field(name=f"{augment_emoji[augment]} {augment} - {data['augments'][index][1]['count']}",
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
            embed.add_field(name=f"{augment_emoji[augment]} {augment} - {data['augments'][index][1]['count']}",
                            value=f""" Avg Placement - {data['augments'][index][1]['avg']}
                            Top 4% - {data['augments'][index][1]['top4%']}%
                            Win% - {data['augments'][index][1]['win%']}%""",
                            inline=True)
        else:
            embed.add_field(name='  ', value='', inline=True)
        index += 1
    embed.set_footer(text=f'Games since: {data["display_date"]}')
    return embed

def units_embed(data, author, riot, icon_id, rank, index=0, mode_name='All Modes'):
    rank_icon = rank.split(' ')[0]

    embed=discord.Embed(title=riot + ' ' + rank_icon, description='', color=0x7011d0, url=f'')
    embed.set_thumbnail(url=f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{icon_id}.jpg')
    embed.add_field(name=f"{mode_name} - {data['count']} games", value='', inline=False)
    for i in range(2):
        if index < len(data['units']):
            unit = data['units'][index][1]
            name = data['units'][index][0]
            embed.add_field(name=f"{unit_emoji[name]} {name} - {unit['count']}",
                            value=f"""{' '.join([f"{misc_emoji['star_level'][str(level)]} {unit['level'][level]}" for level in unit['level']])}
                            {'⠀'.join([item_emoji[item] + ' ' + str(unit['items'][item]) for item in unit['items']])}
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

            embed.add_field(name=f"{unit_emoji[name]} {name} - {unit['count']}",
                            value=f"""{' '.join([f"{misc_emoji['star_level'][str(level)]} {unit['level'][level]}" for level in unit['level']])}
                            {'⠀'.join([item_emoji[item] + '' +  str(unit['items'][item]) for item in unit['items']])}
                            Avg Placement - {unit['avg']}
                            Top 4% - {unit['top4%']}%
                            Win% - {unit['win%']}%""",
                            inline=True)
        else:
            embed.add_field(name='  ', value='', inline=True)
        index += 1
    embed.set_footer(text=f'Games since: {data["display_date"]}')
    return embed

def stats_embed(data, author, riot, icon_id, rank, mode_name='All Modes', index=None):
    rank_icon = rank.split(' ')[0]
    
    embed=discord.Embed(title=riot + ' ' + rank_icon, description='', color=0x7011d0, url=f'')
    embed.set_thumbnail(url=f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{icon_id}.jpg')
    embed.add_field(name=f"{mode_name} - {data['count']} games", 
                    value=f"""{rank}
Avg Placement - {data['avg']} 
Top% - {data['top%']}% 
Win% - {data['win%']}%
Total damage to players - {data['player_damage']}
Total players eliminated - {data['players_eliminated']}
Time spent ingame - {data['time_spent']}h""", inline=False)

    embed.set_footer(text=f'Games since: {data["display_date"]}')
    return embed

def error_embed(message, error_type, author):
    embed=discord.Embed(title=error_type, description=message, color=0x7011d0,)
    embed.set_thumbnail(url='https://www.seekpng.com/png/detail/334-3345964_error-icon-download-attention-symbol.png')
    embed.set_footer(text=f"Requested by {author}")
    return embed

def server_embed(author):
    embed = discord.Embed(title = 'Server', color=0x7011d0)

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