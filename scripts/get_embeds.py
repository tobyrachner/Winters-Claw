import discord

def linked_embed(riot, icon_id, rank, text):
    name = riot.replace('%20', ' ')
    embed=discord.Embed(title=f"{name} {rank.split(' ')[0]}", description='', color=0x7011d0, url=f'https://lolchess.gg/profile/euw/{riot}')
    embed.set_author(name=f'{text} linked:')
    embed.set_thumbnail(url=f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{icon_id}.jpg')
    embed.add_field(name='to your Discord account.', value='')
    return embed

def updating_embed(riot, icon_id, count):
    name = riot.replace('%20', ' ')
    embed=discord.Embed(title=name, description='', color=0x7011d0, url=f'https://lolchess.gg/profile/euw/{riot}')
    embed.set_thumbnail(url=f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{icon_id}.jpg')
    embed.set_author(name=f'Downloading {count} games ...')
    embed.add_field(name='(This might take a while)', value='')
    return embed

def update_embed(riot, icon_id, count):
    name = riot.replace('%20', ' ')
    embed=discord.Embed(title=name, description='', color=0x7011d0, url=f'https://lolchess.gg/profile/euw/{riot}')
    embed.set_thumbnail(url=f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{icon_id}.jpg')
    if count == 0:
        embed.set_author(name=f'No new games to add to:')
    else:
        embed.set_author(name=f'Succesfully added {count} games to:')
    embed.add_field(name='Your profile is up to date.', value='')
    return embed

def traits_embed(data, author):
    lolchess_name = data['name'].replace(' ', '')
    lolchess_name = lolchess_name.lower()

    embed=discord.Embed(title=data['name'], description='', color=0x7011d0, url=f'https://lolchess.gg/profile/euw/{lolchess_name}')
    embed.set_thumbnail(url=f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{data["icon_id"]}.jpg')
    embed.add_field(name='Best Traits:', value='',inline=False)
    for trait in data['best_traits']:
        embed.add_field(name=f"{trait} - {data['traits'][trait]['count']} games",
                        value=f"""Avg Placement - {data['traits'][trait]['avg']}
                        Top 4% - {data['traits'][trait]['top4%']}%
                        Win% - {data['traits'][trait]['win%']}%""",
                        inline=False)
    embed.set_footer(text=f"Requested by {author}")
    return embed

def stats_embed(data, author, riot, icon_id, rank, display_mode, mode_name='All Modes'):
    rank_icon = rank.split(' ')[0]
    name = riot.replace('%20', ' ')
    
    embed=discord.Embed(title=name + ' ' + rank_icon, description='', color=0x7011d0, url=f'https://lolchess.gg/profile/euw/{riot}')
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
Europe West         - > EUW 
Europe Northeast    - > EUNE
Turkey              - > TR
Russia              - > RU```""")
    
    embed.add_field(name='America', inline=True, value="""
```fix
North America       - > NA
Latinamerica North  - > LAN
Latinamerica South  - > LAS
Brasil              - > BR```""")
    
    embed.add_field(name='', value='', inline=True)
    
    embed.add_field(name='Asia', inline=True, value="""
```fix
Japan               - > JP
Korea               - > KR```""")
    
    embed.add_field(name='Sea', inline=True, value="""
```fix
Oceania             - > OC
Philippines         - > PH
Singapoure          - > SG
Taiwan              - > TW
Thailand            - > TH```""")
    
    embed.add_field(name='', value='', inline=True)
    return embed