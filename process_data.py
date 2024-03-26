import sqlite3
import time
from datetime import datetime
from math import ceil

#function to calculate avg placement, top4%, win%, taking a list of placements
def process_placements(placements, mode):
        #making sure to get top 2% for double up games
        if mode == 'pairs':
            set_range = 2
        else: 
            set_range = 4

        #setting avg as 10 so the best traits can be calculated with min() but leaving it at 0 for others so unplayed modes don't get displayed as 10
        if mode == 'trait':
            avg = None
        else:
            avg = 0

        top_4_count = 0
        win_count = 0
        length = 0      
        top_4_percent = 0
        win_percent = 0
        for n in placements:
            length += 1
            if n in range(0, set_range):
                top_4_count += 1
                if n == 1:
                    win_count += 1
        
        if length != 0:
            avg = sum(placements)/length
            top_4_percent = top_4_count / length * 100
            win_percent = win_count / length * 100
        return length, round(avg, 1), round(top_4_percent), round(win_percent)


def process_stats(cur, riot, server, count, days):

    data = {'all': {'time_spent': 0, 'player_damage': 0, 'players_eliminated': 0}, 'modes': {'standard': {'name': 'Standard', 'time_spent': 0}, 'turbo': {'name': 'Hyper Roll', 'time_spent': 0}, 'pairs': {'name': 'Double Up', 'time_spent': 0}}}
    placements = {'all': [], 'standard': [], 'turbo': [], 'pairs': []}
    query = cur.execute("SELECT timestamp, placement, gamemode, time_spent, player_damage, players_eliminated FROM matches WHERE riot = ? AND server = ? AND set_number = 9", (riot, server))
    matches = query.fetchall()
    

    #get requested count of games
    if count != None:
        matches = matches[-count:]
    

    #returning date of the oldest game to display in message
    ts = matches[0][0] / 1000
    

    #if given filter all games before given date
    if days != None:
        old_matches = matches
        matches = []

        current = round(time.time())
        start_date = current - days * 86400
        #if start date is givne instead return the given date
        ts = start_date

        for match in old_matches:
            if not match[0] / 1000 < start_date:
                matches.append(match)
    
    data.update({'display_date': datetime.utcfromtimestamp(ts).strftime('%m/%d/%Y %H:%M (UTC)')})


    for match in matches:
        placement = match[1]
        gamemode = match[2]

        #reformatting placement to placement of team instead of single player if game was Double Up
        if gamemode == 'pairs':
            mode_placement = ceil(int(placement) / 2)
        else:
            mode_placement = placement

        placements['all'].append(placement)
        placements[gamemode].append(mode_placement)

        data['all']['time_spent'] += match[3]
        data['all']['player_damage'] += match[4]
        data['all']['players_eliminated'] += match[5]
        data['modes'][gamemode]['time_spent'] += match[3]

    data['all']['time_spent'] = round(data['all']['time_spent'] / 3600, 1)
    for mode in data['modes']:
        data['modes'][mode]['time_spent'] = round(data['modes'][mode]['time_spent'] / 3600, 1)

    for mode in placements:
        length, avg, top, win = process_placements(placements[mode], mode)
        if mode == 'all':
            data[mode].update({'count': length, 'avg': avg, 'top%': top, 'win%': win})
        else:
            data['modes'][mode].update({'count': length, 'avg': avg, 'top%': top, 'win%': win})

    return data
    
def process_traits(cur, riot, server, count, days):

    traits_dict = {'trait': {'name': 'trait_name', 'placements': [], 'count': 0, 'avg': 0, 'top4%': 0, 'win%': 0}}
    data = {'best': [{'trait': {'count': 0, 'avg': 0, 'top4%': 0, 'win%': 0}}], 'worst': []}
    query = cur.execute("SELECT timestamp, placement, traits FROM matches WHERE riot = ? AND server = ? AND set_number = 9", (riot, server))
    matches = query.fetchall()
    

    #get requested count of games
    if count != None:
        matches = matches[-count:]
    

    #returning date of the oldest game to display in message
    ts = matches[0][0] / 1000
    

    #if given filter all games before given date
    if days != None:
        old_matches = matches
        matches = []

        current = round(time.time())
        start_date = current - days * 86400
        #if start date is givne instead return the given date
        ts = start_date

        for match in old_matches:
            if not match[0] / 1000 < start_date:
                matches.append(match)

    for match in matches:
        placement = match[0]
        traits_fielded = match[0].split('-')

        for trait in traits_dict.keys():
            if trait in traits_fielded:
                traits_dict[trait]['placements'].append(placement)

    avgs = []
    names = []

    for trait in traits_dict.keys():
        count, avg, top, win = process_placements(traits_dict[trait]['placements'], 'trait')
        traits_dict[trait].update({'count': count, 'avg': avg, 'top4%': top, 'win%': win})

        if avg is not None:
            avgs.append(avg)
            names.append(avg)

    best = []
    worst = []

    for i in range (0, 3):
        highest = max(avgs)
        index = avgs.index(highest)
        name = names[index]
        data['best'].append([name, highest])

        avgs.pop(index)
        names.pop(index)
        

        lowest = min(avgs)
        index = avgs.index(lowest)
        name = names[index]
        data['worst'].append([name, highest])

        avgs.pop(index)
        names.pop(index)

        return data