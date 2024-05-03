import time
from datetime import datetime
from math import ceil

from scripts.settings import trait_list, unique_traits, augment_list, unit_list, item_list

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

def filter_games(matches, count, days):
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
        #if start date is given instead return the given date
        ts = start_date

        for match in old_matches:
            if not match[0] / 1000 < start_date:
                matches.append(match)

    # the timestamp is currently not displayed in the final embed but still kept in the function if needed for future use
    return matches, int(ts)

def process_stats(cur, riot, server, count, days, set, display_mode=None, filter='count', descending=True):
    if set.is_integer(): set = int(set)

    data = {'time_spent': 0, 'player_damage': 0, 'players_eliminated': 0}
    placements = []
    if display_mode:
        query = cur.execute("SELECT timestamp, placement, gamemode, time_spent, player_damage, players_eliminated FROM matches WHERE riot = ? AND server = ? AND set_number = ? AND gamemode = ?", (riot, server, set, display_mode))
    else:
        query = cur.execute("SELECT timestamp, placement, gamemode, time_spent, player_damage, players_eliminated FROM matches WHERE riot = ? AND server = ? AND set_number = ?", (riot, server, set))
    
    matches = query.fetchall()

    matches, ts = filter_games(matches, count, days)

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
    
def process_traits(cur, riot, server, count, days, set, display_mode=None, filter='count', descending=True):
    if set.is_integer(): set = int(set)

    traits_dict = {}
    if display_mode:
        query = cur.execute("SELECT timestamp, placement, traits, gamemode FROM matches WHERE riot = ? AND server = ? AND set_number = ? AND gamemode = ?", (riot, server, set, display_mode))
    else:
        query = cur.execute("SELECT timestamp, placement, traits, gamemode FROM matches WHERE riot = ? AND server = ? AND set_number = ?", (riot, server, set))
    matches = query.fetchall()
    
    matches, ts = filter_games(matches, count, days)

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
            if trait == '':
                continue
            name, level, num_units = trait.split('/')
            level = int(level)
            if name in unique_traits:
                level = 5
            if name == 'TFT11_Heavenly' and level > 3:
                if level < 6:
                    level = 3
                else:
                    level = 4

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

    traits_dict = sorted(traits_dict.items(), key=lambda x:x[1][filter], reverse=descending)

    if display_mode == 'ranked' or display_mode == 'normal':
        display_mode = 'standard'
    elif not display_mode:
        display_mode = 'rank'
    cur.execute(f"SELECT {display_mode} FROM profile WHERE riot = ? AND server = ?", (riot, server))
    rank = cur.fetchone()[0]

    return {'count': len(matches), 'traits': traits_dict}, rank

def process_units(cur, riot, server, count, days, set, display_mode=None, filter='count', descending=True):
    if set.is_integer(): set = int(set)

    units_dict = {}
    if display_mode:
        query = cur.execute("SELECT timestamp, placement, units, gamemode FROM matches WHERE riot = ? AND server = ? AND set_number = ? AND gamemode = ?", (riot, server, set, display_mode))
    else:
        query = cur.execute("SELECT timestamp, placement, units, gamemode FROM matches WHERE riot = ? AND server = ? AND set_number = ?", (riot, server, set))
    matches = query.fetchall()
    
    matches, ts = filter_games(matches, count, days)

    for match in matches:
        placement = match[1]
        units_fielded = match[2].split('-')
        gamemode = match[3]

        if gamemode == 'pairs':
            if display_mode == 'pairs':
                placement = ceil(int(placement) / 2)
            else:
                if placement == 2: placement = 1

        for unit in units_fielded:
            if unit == '':
                continue
            name, level, rarity, items = unit.split('/')
            level = int(level)

            items = items.split('.')
            if len(items) == 1 and items[0] == '':
                items = []

            if name in units_dict:
                units_dict[name]['placements'].append(placement)

                if level in units_dict[name]['level']:
                    units_dict[name]['level'][level] += 1
                else:
                    units_dict[name]['level'][level] = 1
                
                for item in items:
                    if not item in item_list:
                        with open('missing_data.txt', 'r+') as f:
                            if not 'Item' + item + '\n' in f.readlines():
                                f.write('Item' + item + '\n')
                        continue

                    if item in units_dict[name]['items']:
                        units_dict[name]['items'][item] += 1
                    else:
                        units_dict[name]['items'][item] = 1

            else:
                units_dict[name] = {'placements': [placement], 'level': {}, 'items': {}}
                units_dict[name]['level'][level] = 1
                for item in items:
                    if not item in item_list:
                        with open('missing_data.txt', 'r+') as f:
                            if not 'Item' + item + '\n' in f.readlines():
                                f.write('Item' + item + '\n')
                        continue
                    units_dict[name]['items'][item] = 1

    for unit in units_dict:
        count, avg, top, win = process_placements(units_dict[unit]['placements'], display_mode)
        units_dict[unit].update({'count': count, 'avg': avg, 'top4%': top, 'win%': win})
        units_dict[unit]['level'] = dict(sorted(units_dict[unit]['level'].items(), key=lambda x: x[0], reverse=True))
        units_dict[unit]['items'] = dict(sorted(units_dict[unit]['items'].items(), key=lambda x: x[1], reverse=True)[:3])

    units_dict = sorted(units_dict.items(), key=lambda x:x[1][filter], reverse=descending)

    if display_mode == 'ranked' or display_mode == 'normal':
        display_mode = 'standard'
    elif not display_mode:
        display_mode = 'rank'
    cur.execute(f"SELECT {display_mode} FROM profile WHERE riot = ? AND server = ?", (riot, server))
    rank = cur.fetchone()[0]

    return {'count': len(matches), 'units': units_dict}, rank

def process_augments(cur, riot, server, count, days, set, display_mode=None, filter='count', descending=True):
    if set.is_integer(): set = int(set)

    augment_dict = {}
    if display_mode:
        query = cur.execute("SELECT timestamp, placement, augments, gamemode FROM matches WHERE riot = ? AND server = ? AND set_number = ? AND gamemode = ?", (riot, server, set, display_mode))
    else:
        query = cur.execute("SELECT timestamp, placement, augments, gamemode FROM matches WHERE riot = ? AND server = ? AND set_number = ?", (riot, server, set))
    matches = query.fetchall()
    
    matches, ts = filter_games(matches, count, days)

    for match in matches:
        placement = match[1]
        augments_picked = match[2].split('-')
        gamemode = match[3]

        if gamemode == 'pairs':
            if display_mode == 'pairs':
                placement = ceil(int(placement) / 2)
            else:
                if placement == 2: placement = 1

        for augment in augments_picked:
            if augment == '':
                continue
            if not augment in augment_list:
                print('MISSING', augment)
                with open('missing_data.txt', 'r+') as f:
                    if augment + '\n' not in f.readlines():
                        f.write(augment + '\n')
                continue

            if augment in augment_dict:
                augment_dict[augment]['placements'].append(placement)
            else:
                augment_dict[augment] = {'placements': [placement], 'level': {}}

    for augment in augment_dict:
        count, avg, top, win = process_placements(augment_dict[augment]['placements'], display_mode)
        augment_dict[augment].update({'count': count, 'avg': avg, 'top4%': top, 'win%': win})

    augment_dict = sorted(augment_dict.items(), key=lambda x:x[1][filter], reverse=descending)

    if display_mode == 'ranked' or display_mode == 'normal':
        display_mode = 'standard'
    elif not display_mode:
        display_mode = 'rank'
    cur.execute(f"SELECT {display_mode} FROM profile WHERE riot = ? AND server = ?", (riot, server))
    rank = cur.fetchone()[0]

    return {'count': len(matches), 'augments': augment_dict}, rank

def process_single_match(cur, riot, server, id=None):
    if id:
        match = cur.execute('SELECT gamemode, placement, level, augments, units, traits, timestamp FROM matches WHERE match_id = ? AND riot = ? AND server = ?', (id, riot, server))
        match = match.fetchone()
        if match is None:
            raise IndexError('Could not find match with given id')
    else:
        match = cur.execute('SELECT gamemode, placement, level, augments, units, traits, timestamp FROM matches WHERE riot = ? and server = ? ORDER BY timestamp DESC', (riot, server)).fetchone()

    data = {'timestamp': int(match[6] / 1000)}

    gamemode = match[0]

    data['gamemode'] = gamemode[0].upper() + gamemode[1:]
    data['placement'] = match[1]
    data['level'] = match[2]

    if gamemode == 'ranked' or gamemode == 'normal':
        gamemode = 'standard'
    cur.execute(f"SELECT {gamemode} FROM profile WHERE riot = ? AND server = ?", (riot, server))
    data['rank'] = cur.fetchone()[0]

    data['augments'] = []
    for augment in match[3].split('-'):
        if augment == '':
            continue
        if not augment in augment_list:
            print('MISSING', augment)
            with open('missing_data.txt', 'r+') as f:
                if 'augment: ' + augment + '\n' not in f.readlines():
                    f.write('augment: ' + augment + '\n')
                continue
        data['augments'].append(augment)

    traits = {}
    for trait in match[5].split('-'):
        if trait == '':
            continue
        name, level, num_units = trait.split('/')
        if name in unique_traits:
            level = '5'
        if name == 'TFT11_Heavenly' and int(level) > 3:
            if int(level) < 6:
                level = '3'
            else:
                level = '4'
        traits[name] = {'level': level, 'num_units': num_units}

    data['traits'] = dict(sorted(traits.items(), key=lambda x: (x[1]['level'], x[1]['num_units']), reverse=True))

    units = {}
    for unit in match[4].split('-'):
        if unit == '':
            continue
        name, level, rarity, items = unit.split('/')
        rarity = int(rarity)

        processed_items = []
        for item in items.split('.'):
            if item == '':
                continue
            processed_items.append(item)
        units[name] = {'level': level, 'items': processed_items, 'rarity': rarity}

    data['units'] = dict(sorted(units.items(), key=lambda x: (int(x[1]['level']), x[1]['rarity'], len(x[1]['items'])), reverse=True))

    return data

def process_history(cur, riot, server, stat_type='general', gamemode=None):
    if gamemode:
        matches = cur.execute('SELECT match_id, gamemode, placement, level, timestamp, traits, units, augments FROM matches WHERE gamemode = ? AND riot = ? AND server = ? ORDER BY timestamp DESC', (gamemode, riot, server)).fetchall()
    else:
        matches = cur.execute('SELECT match_id, gamemode, placement, level, timestamp, traits, units, augments FROM matches WHERE riot = ? and server = ? ORDER BY timestamp DESC', (riot, server)).fetchall()
    
    if len(matches) == 0:
        raise NameError()
    
    data = []
    for match in matches:
        match_id, gamemode, placement, level, timestamp, traits, units, augments = match

        game = {'id': match_id, 'placement': placement}
        if stat_type == 'general':
            game = {
                'id': match_id,
                'timestamp': int(timestamp / 1000), 
                'gamemode': gamemode[0].upper() + gamemode[1:],
                'placement': placement,
                'level': level
                }
            
        elif stat_type == 'traits':
            game['traits'] = {}
            for trait in traits.split('-'):
                if trait == '':
                    continue
                name, level, num_units = trait.split('/')
                if name in unique_traits:
                    level = '5'
                if name == 'TFT11_Heavenly' and int(level) > 3:
                    if int(level) < 6:
                        level = '3'
                    else:
                        level = '4'
                game['traits'][name] = {'level': level, 'num_units': num_units}

            game['traits'] = dict(sorted(game['traits'].items(), key=lambda x: (x[1]['level'], x[1]['num_units']), reverse=True))

        elif stat_type == 'units':
            game['units'] = {}
            for unit in units.split('-'):
                if unit == '':
                    continue
                name, level, rarity, items = unit.split('/')
                rarity = int(rarity)
                game['units'][name] = {'level': level, 'rarity': rarity}

            game['units'] = dict(sorted(game['units'].items(), key=lambda x: (int(x[1]['level']), x[1]['rarity']), reverse=True))

        elif stat_type == 'augments':
            game['augments'] = []
            for augment in augments.split('-'):
                if augment == '':
                    continue
                if not augment in augment_list:
                    print('MISSING', augment)
                    with open('missing_data.txt', 'r+') as f:
                        if 'augment: ' + augment + '\n' not in f.readlines():
                            f.write('augment: ' + augment + '\n')
                        continue
                game['augments'].append(augment)
        data.append(game)
        
    return data