from scripts import api
from scripts.settings import SET_START_DATE

def get_matchids(riot, server, region, puuid, cur):
    
    tiers = {'BRONZE': {'name': 'Bronze', 'emoji': '<:bronze:1146825503710392502>', 'show_tier': True}, 'SILVER': {'name': 'Silver', 'emoji': '<:silver:1146826645332824217>', 'show_tier': True}, 
         'GOLD': {'name': 'Gold', 'emoji': '<:gold:1146828764211331188>', 'show_tier': True}, 'PLATINUM': {'name': 'Platinum', 'emoji': '<:platinum:1146828808436076656>', 'show_tier': True}, 
         'EMERALD': {'name': 'Emerald', 'emoji': '<:emerald:1146828849523478618>', 'show_tier': True}, 'DIAMOND': {'name': 'Diamond', 'emoji': '<:diamond:1146828846260297961>', 'show_tier': True}, 
         'MASTER': {'name': 'Master', 'emoji': '<:master:1146828806028533760>', 'show_tier': False}, 'GRANDMASTER': {'name': 'Grandmaster', 'emoji': '<:grandmaster:1146828803352559737>', 'show_tier': False}, 
         'CHALLENGER': {'name': 'Challenger', 'emoji': '<:challenger:1146828843085217843>', 'show_tier': False}}
    rank_translation = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 'I': 1, 'II': 2, 'III': 3, 'IV': 4}


    data = cur.execute("SELECT last_processed FROM profile WHERE puuid = ?", (puuid,)).fetchall()

    profile = api.request(f'https://{server}.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/{puuid}?api_key=').json()
    icon_id = profile['profileIconId']
    summoner_id = profile['id']

    league = api.request(f'https://{server}.api.riotgames.com/tft/league/v1/entries/by-summoner/{summoner_id}?api_key=').json()

    ranks = {'standard': '', 'pairs': '', 'turbo': ''}
    highest_rank = []
    for queue in league:
        if queue['queueType'] == 'RANKED_TFT_TURBO': 
            continue

        if queue['queueType'] == 'RANKED_TFT':
            queue_id = 'standard'
        else:
            queue_id = 'pairs'

        tier = queue['tier']
        div = queue['rank']
        lp = queue['leaguePoints']

        if (not highest_rank) or list(tiers).index(tier) > list(tiers).index(highest_rank[0]) or (list(tiers).index(tier) == list(tiers).index(highest_rank[0]) and rank_translation[div] > rank_translation[highest_rank[1]]) or (list(tiers).index(tier) == list(tiers).index(highest_rank[0]) and rank_translation[div] == rank_translation[highest_rank[1]] and lp > highest_rank[2]):
            highest_rank = [tier, div, lp]

        rank = tiers[tier]['emoji'] + ' ' + tiers[tier]['name']
        if tiers[tier]['show_tier'] == True:
            rank = rank + ' ' + div
        rank = rank + ' - ' + str(lp) + ' LP'
        ranks[queue_id] = rank

    if highest_rank:
        rank = tiers[highest_rank[0]]['emoji'] + ' ' + tiers[highest_rank[0]]['name']
        if tiers[highest_rank[0]]['show_tier'] == True:
            rank = rank + ' ' + highest_rank[1]
        rank = rank + ' - ' + str(highest_rank[2]) + ' LP'
    else:
        rank = ''

    cur.execute("UPDATE links SET rank = ? WHERE puuid = ?", (rank, puuid))

    if len(data) == 0:

        cur.execute("""
            INSERT INTO profile ('riot', 'server', 'puuid', 'icon_id', 'rank', 'standard', 'pairs', 'turbo')
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (riot, server, puuid, icon_id, rank, ranks['standard'], ranks['pairs'], ranks['turbo']))
        last_processed = ''

    else:
        cur.execute("UPDATE profile SET icon_id = ?, rank = ?, standard = ?, pairs = ?, turbo = ? WHERE puuid = ?", (icon_id, rank, ranks['standard'], ranks['pairs'], ranks['turbo'], puuid))
        last_processed = data[0][0]

    start = 0
    run = True
    matches = []
    match_ids = []

    while True:
        resp = api.request(f'https://{region}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?start={start}&startTime={SET_START_DATE}&count=200&api_key=').json()

        #check if requested list of matches is empty
        if resp == []:
            break

        #reverse list of match ids and also remove all match ids which have been processed in earlier commands
        for match_id in resp:
            if match_id == last_processed:
                break
            else:
                match_ids.insert(0, match_id)
        start += 200

    if match_ids == []:
        raise NameError(f"No new games from {riot}.")

    data = (region, puuid, riot, server, match_ids[-1], match_ids)
    return icon_id, len(match_ids), data

def update_games(cur, data):
    region, puuid, riot, server, latest_match, match_ids = data

    for match_id in match_ids:
        match = api.request(f'https://{region}.api.riotgames.com/tft/match/v1/matches/{match_id}?api_key=').json()

        index = match['metadata']['participants'].index(puuid)      #gets participant number of player

        #get different information out of .json
        set_number = match['info']['tft_set_number']
        timestamp = match['info']['game_datetime']
        placement = match['info']['participants'][index]['placement']
        gamemode = match['info']['tft_game_type']
        time_spent = match['info']['participants'][index]['time_eliminated']
        player_damage = match['info']['participants'][0]['total_damage_to_players']
        players_eliminated = match['info']['participants'][0]['players_eliminated']

        if gamemode == 'standard':
            if match['info']['queue_id'] == 1100:
                gamemode = 'ranked'
            elif match['info']['queue_id'] == 1090:
                gamemode = 'normal'

        traits = ''
        for trait in match['info']['participants'][index]['traits']:
            if trait['tier_current'] > 0:
                traits = traits + trait['name'] + '-'


        cur.execute("""INSERT INTO matches ('riot', 'server', 'set_number', 'timestamp', 'placement', 'gamemode', 'time_spent', 'player_damage', 'players_eliminated', 'traits')
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (riot, server, set_number, timestamp, placement, gamemode, time_spent, player_damage, players_eliminated, traits[:-1]))
        
    cur.execute("UPDATE profile SET last_processed = ? WHERE puuid = ?", (latest_match, puuid))

    return