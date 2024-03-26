import requests
from math import ceil

#api_key = 'RGAPI-9d604ae6-f3b8-4b44-90e6-cd5bd957eea5'

def get_stats(riot, count, api_key):

    traits_dict = {'Set9_Bastion': {'name': 'Bastion', 'placements': []}, 'Set9_Bruiser': {'name': 'Bruiser', 'placements': []}, 'Set9_Deadeye': {'name': 'Deadeye', 'placements': []}, 'Set9_Freljord': {'name': 'Freljord', 'placements': []}, 'Set9_Ionia': {'name': 'Ionia', 'placements': []}, 'Set9_Multicaster': {'name': 'Multicaster', 'placements': []}, 'Set9_Preserver': {'name': 'Invoker', 'placements': []}, 'Set9_Shurima': {'name': 'Shurima', 'placements': []}, 'Set9_Strategist': {'name': 'Strategist', 'placements': []}, 'Set9_Armorclad': {'name': 'Juggernaut', 'placements': []}, 'Set9_BandleCity': {'name': 'Yordle', 'placements': []}, 'Set9_Darkin': {'name': 'Darkin', 'placements': []}, 'Set9_Noxus': {'name': 'Noxus', 'placements': []}, 'Set9_Piltover': {'name': 'Piltover', 'placements': []}, 'Set9_Rogue': {'name': 'Rogue', 'placements': []}, 'Set9_Slayer': {'name': 'Slayer', 'placements': []}, 'Set9_Sorcerer': {'name': 'Sorcerer', 'placements': []}, 'Set9_Zaun': {'name': 'Zaun', 'placements': []}, 'Set9_Wanderer': {'name': 'Wanderer', 'placements': []}, 'Set9_Demacia': {'name': 'Demacia', 'placements': []}, 'Set9_Empress': {'name': 'Empress', 'placements': []}, 'Set9_Void': {'name': 'Void', 'placements': []}, 'Set9_Challenger': {'name': 'Challenger', 'placements': []}, 'Set9_ShadowIsles': {'name': 'Shadow Isles', 'placements': []}, 'Set9_Technogenius': {'name': 'Technogenius', 'placements': []}, 'Set9_Targon': {'name': 'Targon', 'placements': []}, 'Set9_Marksman': {'name': 'Gunner', 'placements': []}, 'Set9_Redeemer': {'name': 'Redeemer', 'placements': []}}
    modes_dict ={'standard': {'name': 'Standard', 'placements': [], 'time_spent': 0}, 'turbo': {'name': 'Hyper Roll', 'placements': [], 'time_spent': 0}, 'pairs': {'name': 'Double Up', 'placements': [], 'time_spent': 0}}
    info = {'placements': [],'time_spent': 0, 'player_damage': 0, 'players_eliminated': 0}
    processed = {'info': {}, 'modes': {}, 'traits': {}, 'best_traits': []}
    '''
    profile = requests.get(f'https://{riot[1]}.api.riotgames.com/tft/summoner/v1/summoners/by-name/{riot[0]}?api_key={api_key}').json()
    puuid = profile['puuid']
    summoner_name = profile['name']
    icon_id = profile['profileIconId']
    processed.update({'name': summoner_name})
    processed.update({'icon_id': icon_id})

    match_ids = requests.get(f'https://europe.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?start=0&count={count}&api_key={api_key}').json()

    for match_id in match_ids:
        match = requests.get(f'https://europe.api.riotgames.com/tft/match/v1/matches/{match_id}?api_key={api_key}').json()
        index = match['metadata']['participants'].index(puuid)      #gets participant number of player

        #get different information out of .json
        placement = match['info']['participants'][index]['placement']
        gamemode = match['info']['tft_game_type']
        time_spent = match['info']['participants'][index]['time_eliminated']
        player_damage = match['info']['participants'][0]['total_damage_to_players']
        players_eliminated = match['info']['participants'][0]['players_eliminated']

        #reformatting placement to placement of team instead of single player if game was Double Up
        if gamemode == 'pairs':
            pair_placement = ceil(int(placement) / 2)
        else: pair_placement = placement

        #add information to 'info' list (line 8)
        info['placements'].append(int(placement))
        info['time_spent'] += time_spent
        info['player_damage'] += player_damage
        info['players_eliminated'] += players_eliminated

        if gamemode == 'pairs':
            placement = ceil(placement/2)

        #add information to 'modes_dict' for gamemode specific information
        modes_dict[gamemode]['placements'].append(int(pair_placement))
        modes_dict[gamemode]['time_spent'] += time_spent

        #append placement to every trait fielded
        all_traits = match['info']['participants'][index]['traits']
        for trait in all_traits:
            if trait['tier_current'] > 0:
                traits_dict[trait['name']]['placements'] += [int(placement)]'''




    #process all collected data

    trait_avgs = []

    #function to calculate avg placement, top4%, win%, taking a list of placements
    def process_placements(placements, mode):
        #making sure to get top 2 for double up games
        if mode == 'pairs':
            set_range = 2
        else: 
            set_range = 4

        #setting avg as 10 so the best traits can be calculated with min() but leaving it at 0 for others so unplayed modes don't get displayed as 10
        if mode == 'traits':
            avg = 10 
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


    #calculate avg placement, top4%, win% overall and for all gamemodes and traits
    length_all, avg_all, top_4_percent_all, win_percent_all = process_placements(info['placements'], '')
    processed.update({'info': {'count': length_all, 'avg': avg_all, 'top4%': top_4_percent_all, 'win%': win_percent_all}})

    for mode in modes_dict:
        length_mode, avg_mode, top_4_percent_mode, win_percent_mode = process_placements(modes_dict[mode]['placements'], mode)
        #making sure to set avg back to 0 if mode wasn#t played
        if length_mode == 10:
            avg_mode, top_4_percent_mode, win_percent_mode = 0 
        name_mode = modes_dict[mode]['name']
        processed['modes'].update({name_mode: {'count': length_mode, 'avg': avg_mode, 'top4%': top_4_percent_mode, 'win%': win_percent_mode}})

    for trait in traits_dict:
        length_trait, avg_trait, top_4_percent_trait, win_percent_trait = process_placements(traits_dict[trait]['placements'], 'traits')
        name_trait = traits_dict[trait]['name']
        processed['traits'].update({name_trait: {'count': length_trait, 'avg': avg_trait, 'top4%': top_4_percent_trait, 'win%': win_percent_trait}})

        trait_avgs.append(avg_trait)


    #get best traits
    trait_list = list(processed['traits'])
    number_of_traits = 4        #number of traits added to 'best_traits'
    for i in range (0, number_of_traits):
        best_trait_index = trait_avgs.index(min(trait_avgs))
        trait_avgs[best_trait_index] = 10
        processed['best_traits'].append(trait_list[best_trait_index])


    #reformat time spent ingame from seconds to hours
    time_spent = round(info['time_spent'] / 3600, 1)
    processed['info'].update({'time_spent': time_spent})


    #add players eliminated and player damage
    processed['info'].update({'player_damage': info['player_damage']})
    processed['info'].update({'players_eliminated': info['players_eliminated']})

    return processed