import json

with open('data/ranked_tiers.json') as f:
    ranked_tiers = json.load(f)
with open('data/traits.json', 'r') as f:
    trait_list = json.load(f)
with open('data/trait_emoji.json', 'r') as f:
    trait_emoji = json.load(f)

unique_traits = ['Artist', 'Great', 'Lovers', 'Spirit Walker', 'Trickshot/Altruist']

TOKEN = 'MTEzNzg0ODU4ODUyMTcxMzY3NA.G2u05R.Qt525bo2c9uV614g-FyBmqsw9r4amvxnUgkW5M'
RGAPI = 'RGAPI-c19360cd-03cc-4f45-b5c9-ec37d5ff4e63'
TESTSERVER_ID = '1137866058867425340'
CURRENT_SET = 11.0
SET_START_DATE = 1710932400         # March 20th, 2024, 11:00:00 GMT 