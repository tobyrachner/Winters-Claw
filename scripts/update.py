from scripts import api
from scripts.settings import SET_START_DATE
from scripts.settings import ranked_tiers as tiers

async def get_matchids(session, riot, server, region, puuid, cur):
    rank_translation = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 'I': 1, 'II': 2, 'III': 3, 'IV': 4}

    data = cur.execute("SELECT last_processed FROM profile WHERE puuid = ?", (puuid,)).fetchall()
    last_processed = ''
    if len(data) > 0:
        last_processed = data[0][0]

    profile = await api.request(session, f'https://{server}.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/{puuid}?api_key=')
    icon_id = profile['profileIconId']
    summoner_id = profile['id']

    league = await api.request(session, f'https://{server}.api.riotgames.com/tft/league/v1/entries/by-summoner/{summoner_id}?api_key=')

    ranks = {'standard': '', 'pairs': '', 'turbo': ''}
    highest_rank = []
    for queue in league:
        if queue['queueType'] == 'RANKED_TFT_TURBO': 
            queue_id = 'turbo'
            tier  = queue['ratedTier']
            rating = queue['ratedRating']
            ranks['turbo'] = f"{tiers[tier]['emoji']} {tiers[tier]['name']} {rating}"

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
    elif ranks['turbo']:
        rank = ranks['turbo']
    else:
        rank = ''

    start = 0
    match_ids = []

    loop = True
    while loop:
        resp = await api.request(session, f'https://{region}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?start={start}&startTime={SET_START_DATE}&count=200&api_key=')

        #check if requested list of matches is empty
        if resp == []:
            break

        #reverse list of match ids and also remove all match ids which have been processed in earlier commands
        for match_id in resp:
            if match_id == last_processed:
                loop = False
                break
            else:
                match_ids.insert(0, match_id)
        start += 200

    if match_ids == []:
        if not last_processed:
            last_processed = ''
    else:
        last_processed = match_ids[-1]

    if len(data) == 0:

        cur.execute("""
            INSERT INTO profile ('riot', 'server', 'region', 'puuid', 'icon_id', 'rank', 'standard', 'pairs', 'turbo', 'last_processed')
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (riot, server, region, puuid, icon_id, rank, ranks['standard'], ranks['pairs'], ranks['turbo'], last_processed))

    else:
        cur.execute("UPDATE profile SET icon_id = ?, rank = ?, standard = ?, pairs = ?, turbo = ?, last_processed = ? WHERE puuid = ?", (icon_id, rank, ranks['standard'], ranks['pairs'], ranks['turbo'], last_processed, puuid))

    if match_ids == []:
        raise NameError(f"No new games from {riot}.")

    data = (region, puuid, riot, server, match_ids)
    return icon_id, len(match_ids), data

async def update_games(session, cur, data):
    region, puuid, riot, server, match_ids = data

    for match_id in match_ids:
        match = await api.request(session, f'https://{region}.api.riotgames.com/tft/match/v1/matches/{match_id}?api_key=')

        index = match['metadata']['participants'].index(puuid)      #gets participant number of player

        #get different information out of .json
        set_number = match['info']['tft_set_number']
        timestamp = match['info']['game_datetime']
        placement = match['info']['participants'][index]['placement']
        gamemode = match['info']['tft_game_type']
        level = match['info']['participants'][index]['level']
        time_spent = match['info']['participants'][index]['time_eliminated']
        player_damage = match['info']['participants'][0]['total_damage_to_players']
        players_eliminated = match['info']['participants'][0]['players_eliminated']

        if gamemode == 'standard':
            if match['info']['queue_id'] == 1100:
                gamemode = 'ranked'
            elif match['info']['queue_id'] == 1090:
                gamemode = 'normal'

        traits = []
        for trait in match['info']['participants'][index]['traits']:
            if trait['tier_current'] > 0:
                traits.append(f"{trait['name']}/{trait['tier_current']}/{trait['num_units']}")

        augments = '-'.join(match['info']['participants'][index]['augments'])

        units = []
        for unit in match['info']['participants'][index]['units']:
            units.append(f"{unit['character_id']}/{unit['tier']}/{unit['rarity']}/{'.'.join(unit['itemNames'])}")


        cur.execute("""INSERT INTO matches ('puuid', 'set_number', 'timestamp', 'placement', 'gamemode', 'level', 'time_spent', 'player_damage', 'players_eliminated', 'traits', 'units', 'augments')
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (puuid, set_number, timestamp, placement, gamemode, level, time_spent, player_damage, players_eliminated, '-'.join(traits), '-'.join(units), augments))
        
    return