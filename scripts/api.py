import requests
import time
from scripts import settings

API_KEY = settings.RGAPI

def request(url):
    while True:
        resp = requests.get(url + API_KEY)
        if resp.status_code == 429:
            print('rate limit')
            time.sleep(5)
            continue
        break
    if resp.status_code == 401:
        raise PermissionError('Api key expired')
    return resp