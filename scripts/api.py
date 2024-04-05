import requests
import time
from scripts.settings import RGAPI

def request(url):
    while True:
        resp = requests.get(url + RGAPI)
        if resp.status_code == 429:
            print('rate limit')
            time.sleep(5)
            continue
        break
    if resp.status_code == 401:
        print('APi key expired')
        raise PermissionError('Api key expired')
    return resp