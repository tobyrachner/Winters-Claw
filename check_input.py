import api

def get_arguments(inputs):
    count = ''
    days = ''
    get_link = True
    content = []

    for i in inputs:
        content.append(i)

    if 'count' in content: #checking if user gave 'count' as argument. If yes, get next object in content as count of games
        index = content.index('count')
        try:
            count = content[index + 1]
        except IndexError:
            raise SyntaxError('Did not enter the number of games')
        if not count.isnumeric():
            raise SyntaxError(f"'{count}' is not a valid number of games.") 
        else:
            count = int(count)  
            content.pop(index)
            content.pop(index)     
    
    if 'days' in content: #checking if user gave 'days' as argument. If yes, get next object in content as count of days
        index = content.index('days')
        try:
            days = content[index + 1]
        except IndexError:
            raise SyntaxError('Did not enter the number of days')
        if not days.isnumeric():
            raise SyntaxError(f"'{days}' is not a valid number of days.")
        else:
            days = int(days)
            content.pop(index)
            content.pop(index)
        
    if len(content) > 0:
        get_link = check_summoner(content)

    return count, days, get_link


def check_summoner(summ_name, server):
    riot = summ_name.replace(' ', '%20')

    server_list = {'br1': {'server': 'br1', 'region': 'americas'}, 'br': {'server': 'br1', 'region': 'americas'}, 'euw1': {'server': 'euw1', 'region': 'europe'}, 'euw': {'server': 'euw1', 'region': 'europe'}, 
                   'jp1': {'server': 'jp1', 'region': 'asia'}, 'jp': {'server': 'jp1', 'region': 'asia'}, 'la1': {'server': 'la1', 'region': 'americas'}, 'lan': {'server': 'la1', 'region': 'americas'}, 
                   'la2': {'server': 'la2', 'region': 'americas'}, 'las': {'server': 'la2', 'region': 'americas'}, 'na1': {'server': 'na1', 'region': 'americas'}, 'na': {'server': 'na1', 'region': 'americas'}, 
                   'oc1': {'server': 'oc1', 'region': 'sea'}, 'oc': {'server': 'oc1', 'region': 'sea'}, 'ph2': {'server': 'ph2', 'region': 'sea'}, 'ph': {'server': 'ph2', 'region': 'sea'}, 
                   'sg2': {'server': 'sg2', 'region': 'sea'}, 'sg': {'server': 'sg2', 'region': 'sea'}, 'th2': {'server': 'th2', 'region': 'sea'}, 'th': {'server': 'th2', 'region': 'sea'}, 
                   'tr1': {'server': 'tr1', 'region': 'europe'}, 'tr': {'server': 'tr1', 'region': 'europe'}, 'tw2': {'server': 'tw2', 'region': 'sea'}, 'tw': {'server': 'tw2', 'region': 'sea'}, 
                   'vn2': {'server': 'vn2', 'region': 'sea'}, 'vn': {'server': 'vn2', 'region': 'sea'}, 'eun1': {'server': 'eun1', 'region': 'europe'}, 'eun': {'server': 'eun1', 'region': 'europe'}, 
                   'eune': {'server': 'eun1', 'region': 'europe'}, 'kr': {'server': 'kr', 'region': 'asia'}, 'ru': {'server': 'ru', 'region': 'europe'}}
    tiers = {'BRONZE': {'name': 'Bronze', 'emoji': '<:bronze:1146825503710392502>', 'show_tier': True}, 'SILVER': {'name': 'Silver', 'emoji': '<:silver:1146826645332824217>', 'show_tier': True}, 
         'GOLD': {'name': 'Gold', 'emoji': '<:gold:1146828764211331188>', 'show_tier': True}, 'PLATINUM': {'name': 'Platinum', 'emoji': '<:platinum:1146828808436076656>', 'show_tier': True}, 
         'EMERALD': {'name': 'Emerald', 'emoji': '<:emerald:1146828849523478618>', 'show_tier': True}, 'DIAMOND': {'name': 'Diamond', 'emoji': '<:diamond:1146828846260297961>', 'show_tier': True}, 
         'MASTER': {'name': 'Master', 'emoji': '<:master:1146828806028533760>', 'show_tier': False}, 'GRANDMASTER': {'name': 'Grandmaster', 'emoji': '<:grandmaster:1146828803352559737>', 'show_tier': False}, 
         'CHALLENGER': {'name': 'Challenger', 'emoji': '<:challenger:1146828843085217843>', 'show_tier': False}}

    if server in server_list.keys():
        server = server_list[server]['server']
        region = server_list[server]['region']
    else:
        raise SyntaxError(f'{server} is not a from the api supported server.\nFor a full list of servers type $servers.')
    
    test = api.request(f'https://{server}.api.riotgames.com/tft/summoner/v1/summoners/by-name/{riot}?api_key=')
    if test.status_code != 200:
        raise SyntaxError(f"'{summ_name}' is not a valid username on {server}.")
    
    profile = test.json()
    summ_id = profile['id']

    league = api.request(f'https://{server}.api.riotgames.com/tft/league/v1/entries/by-summoner/{summ_id}?api_key=').json()
    try:
        tier = league[0]['tier']
        div = league[0]['rank']
        lp = league[0]['leaguePoints']
    except IndexError:
        rank = ''
    else:  
        rank = tiers[tier]['emoji'] + ' ' + tiers[tier]['name']
        if tiers[tier]['show_tier'] == True:
            rank = rank + ' ' + div
        rank = rank + ' - ' + str(lp) + ' LP'


    return riot, server, region, profile['profileIconId'], rank