import sqlite3
import time
from datetime import datetime
from math import ceil

from scripts.settings import trait_list, unique_traits

#function to calculate avg placement, top4%, win%, taking a list of placements
def process_placements(placements, mode):
        #making sure to get top 2% for double up games
        if mode == 'pairs':
            set_range = 3
        else: 
            set_range = 5

        avg = None
        top_4_count = 0
        win_count = 0
        length = 0      
        top_4_percent = 0
        win_percent = 0
        for n in placements:
            length += 1
            if n in range(1, set_range):
                top_4_count += 1
                if n == 1:
                    win_count += 1
        
        if length != 0:
            avg = sum(placements)/length
            top_4_percent = top_4_count / length * 100
            win_percent = win_count / length * 100
        return length, round(avg, 1), round(top_4_percent), round(win_percent)


def process_stats(cur, riot, server, count, days, set, display_mode=None):
    if set.is_integer(): set = int(set)

    data = {'time_spent': 0, 'player_damage': 0, 'players_eliminated': 0}
    placements = []
    if display_mode:
        query = cur.execute("SELECT timestamp, placement, gamemode, time_spent, player_damage, players_eliminated FROM matches WHERE riot = ? AND server = ? AND set_number = ? AND gamemode = ?", (riot, server, set, display_mode))
    else:
        query = cur.execute("SELECT timestamp, placement, gamemode, time_spent, player_damage, players_eliminated FROM matches WHERE riot = ? AND server = ? AND set_number = ?", (riot, server, set))
    
    matches = query.fetchall()

    #get requested count of games
    if count:
        matches = matches[-count:]
    

    #returning date of the oldest game to display in message
    ts = matches[0][0] / 1000
    

    #if given filter all games before given date
    if days:
        old_matches = matches
        matches = []

        current = round(time.time())
        start_date = current - days * 86400
        #if start date is givne instead return the given date
        ts = start_date

        for match in old_matches:
            if not match[0] / 1000 < start_date:
                matches.append(match)
    
    data.update({'display_date': datetime.utcfromtimestamp(ts, ).strftime('%m/%d/%Y %H:%M (UTC)')})


    for match in matches:
        placement = match[1]
        gamemode = match[2]

        #reformatting placement to placement of team instead of single player if game was Double Up
        if gamemode == 'pairs':
            if display_mode == 'pairs':
                placement = ceil(int(placement) / 2)
            else:
                if placement == 2: placement = 1

        placements.append(placement)

        data['time_spent'] += match[3]
        data['player_damage'] += match[4]
        data['players_eliminated'] += match[5]

    data['time_spent'] = round(data['time_spent'] / 3600, 1)

    length, avg, top, win = process_placements(placements, display_mode)
    data.update({'count': length, 'avg': avg, 'top%': top, 'win%': win})

    if display_mode == 'ranked' or display_mode == 'normal':
        display_mode = 'standard'
    elif not display_mode:
        display_mode = 'rank'
    cur.execute(f"SELECT {display_mode} FROM profile WHERE riot = ? AND server = ?", (riot, server))
    rank = cur.fetchone()[0]
    return data, rank
    
def process_traits(cur, riot, server, count, days, set, display_mode=None):
    if set.is_integer(): set = int(set)

    traits_dict = {}
    if display_mode:
        query = cur.execute("SELECT timestamp, placement, traits, gamemode FROM matches WHERE riot = ? AND server = ? AND set_number = ? AND gamemode = ?", (riot, server, set, display_mode))
    else:
        query = cur.execute("SELECT timestamp, placement, traits, gamemode FROM matches WHERE riot = ? AND server = ? AND set_number = ?", (riot, server, set))
    matches = query.fetchall()
    

    if count:
        matches = matches[-count:]

    #returning date of the oldest game to display in message
    ts = matches[0][0] / 1000

    #if given filter all games before given date
    if days:
        old_matches = matches
        matches = []

        current = round(time.time())
        start_date = current - days * 86400
        #if start date is givne instead return the given date
        ts = start_date

        for match in old_matches:
            if not match[0] / 1000 < start_date:
                matches.append(match)
    
    display_date = datetime.utcfromtimestamp(ts, ).strftime('%m/%d/%Y %H:%M (UTC)')

    for match in matches:
        placement = match[1]
        traits_fielded = match[2].split('-')
        gamemode = match[3]

        if gamemode == 'pairs':
            if display_mode == 'pairs':
                placement = ceil(int(placement) / 2)
            else:
                if placement == 2: placement = 1

        for trait in traits_fielded:
            name, level = trait.split('/')
            name = trait_list[name]['name']
            level = int(level)
            if name in unique_traits:
                level = 5

            if name in traits_dict:
                traits_dict[name]['placements'].append(placement)
                if level in traits_dict[name]['level']:
                    traits_dict[name]['level'][level] += 1
                else:
                    traits_dict[name]['level'][level] = 1
            else:
                traits_dict[name] = {'placements': [placement], 'level': {}}
                traits_dict[name]['level'][level] = 1

    for trait in traits_dict:
        count, avg, top, win = process_placements(traits_dict[trait]['placements'], display_mode)
        traits_dict[trait].update({'count': count, 'avg': avg, 'top4%': top, 'win%': win})
        traits_dict[trait]['level'] = dict(sorted(traits_dict[trait]['level'].items(), key=lambda x: x[0], reverse=True))

    traits_dict = sorted(traits_dict.items(), key=lambda x:x[1]['count'], reverse=True)

    if display_mode == 'ranked' or display_mode == 'normal':
        display_mode = 'standard'
    elif not display_mode:
        display_mode = 'rank'
    cur.execute(f"SELECT {display_mode} FROM profile WHERE riot = ? AND server = ?", (riot, server))
    rank = cur.fetchone()[0]

    return {'count': len(matches), 'traits': traits_dict, 'display_date': display_date}, rank