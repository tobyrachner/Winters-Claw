import api

def get_matchids(riot, server, region, cur):
    
    tiers = {'BRONZE': {'name': 'Bronze', 'emoji': '<:bronze:1146825503710392502>', 'show_tier': True}, 'SILVER': {'name': 'Silver', 'emoji': '<:silver:1146826645332824217>', 'show_tier': True}, 
         'GOLD': {'name': 'Gold', 'emoji': '<:gold:1146828764211331188>', 'show_tier': True}, 'PLATINUM': {'name': 'Platinum', 'emoji': '<:platinum:1146828808436076656>', 'show_tier': True}, 
         'EMERALD': {'name': 'Emerald', 'emoji': '<:emerald:1146828849523478618>', 'show_tier': True}, 'DIAMOND': {'name': 'Diamond', 'emoji': '<:diamond:1146828846260297961>', 'show_tier': True}, 
         'MASTER': {'name': 'Master', 'emoji': '<:master:1146828806028533760>', 'show_tier': False}, 'GRANDMASTER': {'name': 'Grandmaster', 'emoji': '<:grandmaster:1146828803352559737>', 'show_tier': False}, 
         'CHALLENGER': {'name': 'Challenger', 'emoji': '<:challenger:1146828843085217843>', 'show_tier': False}}

    check = cur.execute("SELECT last_processed FROM profile WHERE riot = ? AND server = ?", (riot, server))
    data = check.fetchall()

    
    profile = api.request(f'https://{server}.api.riotgames.com/tft/summoner/v1/summoners/by-name/{riot}?api_key=').json()
    puuid = profile['puuid']
    icon_id = profile['profileIconId']
    summ_id = profile['id']

    league = api.request(f'https://{server}.api.riotgames.com/tft/league/v1/entries/by-summoner/{summ_id}?api_key=').json()
    tier = league[0]['tier']
    div = league[0]['rank']
    lp = league[0]['leaguePoints']
    
    rank = tiers[tier]['emoji'] + ' ' + tiers[tier]['name']
    if tiers[tier]['show_tier'] == True:
        rank = rank + ' ' + div
    rank = rank + ' - ' + str(lp) + ' LP'

    if len(data) == 0:

        cur.execute("""
            INSERT INTO profile ('riot', 'server', 'puuid', 'icon_id', 'rank')
            VALUES (?, ?, ?, ?, ?)""", (riot, server, puuid, icon_id, rank))
        
        last_processed = ''

    else:

        cur.execute("UPDATE profile SET icon_id = ?, rank = ? WHERE riot = ? and server = ?", (icon_id, rank, riot, server))
        
        last_processed = data[0][0]

    start = 0
    run = True
    matches = []

    resp = api.request(f'https://{region}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?start={start}&startTime=1686780000&count=200&api_key=').json()
    #raise error if account exists but there aren't any games played
    if resp == []:
        raise NameError(f"No games for {riot.replace('%20', ' ')} found.")
    
    #while loop to request more games if none of the first 200 games were already processed
    while run:
        #check if requested list of matches is empty
        if resp == []:
            run = False
        else:
            matches += resp

        latest_match = matches[0]

        #reverse list of match ids and also remove all match ids which have been processed in earlier commands
        match_ids = []
        for match_id in matches:
            if match_id == last_processed:
                run = False
                break
            else:
                match_ids.insert(0, match_id)
        start += 200
        resp = api.request(f'https://{region}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?start={start}&startTime=1686780000&count=200&api_key=').json()

        data = (cur, region, puuid, riot, server, latest_match, match_ids)
        return icon_id, len(match_ids), data

def update_games(data):
    cur, region, puuid, riot, server, latest_match, match_ids = data

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

        traits = ''
        for trait in match['info']['participants'][index]['traits']:
            if trait['tier_current'] > 0:
                traits = traits + trait['name'] + '-'


        cur.execute("""INSERT INTO matches ('riot', 'server', 'set_number', 'timestamp', 'placement', 'gamemode', 'time_spent', 'player_damage', 'players_eliminated', 'traits')
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (riot, server, set_number, timestamp, placement, gamemode, time_spent, player_damage, players_eliminated, traits[:-1]))
        
    cur.execute("UPDATE profile SET last_processed = ? WHERE riot = ? AND server = ?", (latest_match, riot, server))

    return