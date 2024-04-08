import requests
import time
import aiohttp
import asyncio

from scripts.settings import RGAPI

async def request(session, url):
    while True:
        async with session.get(url + RGAPI) as resp:
            if resp.status == 429:
                print('rate limit')
                await asyncio.sleep(5)
                continue
            elif resp.status == 200:
                data = await resp.json()
            else:
                 raise Exception()
            break
    return data