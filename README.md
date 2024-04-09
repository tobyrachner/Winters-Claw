# Winter's Claw

## 📝 Description
Welcome to Winter's Claw, a Discord Bot showing you all kinds of personal and global statistics for Riot Games' Teamfight Tactics, utilizing the discord.py library.
To host the bot yourself see [Installation](https://github.com/tobyrachner/Winter-s-Claw/edit/main/README.md#installation). Official hosting might be added in the future
- **Motivation:** When I first started this Bot as my first bigger project I was just looking for a fun way to engage more into programming, while combining it with something I already loved. 
It started out as just a nice little tool for me and a few friends to keep track of all our statistics inside the Discord 
server we were always in anyways and after Set 9 ended and we stopped playing it also ended as that.

- **Why I picked it back up:** When Set 11 released and looked as fun as Tft had ever been, I remembered this project and brought it up-to-date. 
After looking around a bit, I realised that there was no actively running Bot, offering what I originally planned to do with this project, so I decided to add more features and documentation to make it public.

- **Problem solved:** Winter's Claw makes all the stats people want to see about their own performance accessible directly in their own Discord Server without the need of opening an additional webpage.

- **What I learned:** While building this project I learned a lot about programming and Python in general, while also getting deeper insights into how to use API requests and Coroutines.

- **Future Plans:** I plan to add more features to the bot by displaying more detailed personal stats and also offering current meta builds and other global statistics.

## 🤖 Commands
All stat commands have an optional input of specified Riot Id and Server. If not specified, it defaults to the summoner linked to your discord account with /link. <br>
This is a brief overview of commands the bot has to offer:
- `/link [riotId] [server]` -> 
Link a summoner to your discord username to quickly use all other commands

- `/update [riotId] [server]` -> 
Download games of given or linked summoner into database (May take 1-2 minutes if there are 100+ undownloaded games)

- `/stats [days] [count] [set] [riotId] [server]` -> 
Shows all your statistics for gamemodes, traits, units and augments. <br>
Information is navigatable through the buttons provided. Arguments offer to display data only from recent x games/days or a specified set (defaults to all games of current set).

- `/match_history [riotId] [server]` -> 
Shows information about the last 6 games

- `/single_match [matchId] [riotId] [server]` -> 
Shows details about a specfic match for given or linked summoner. Match IDs are obtainable through /match_history (defaults to last match played)

- `/linked` -> 
Shows the summoner linked to your discord username

- `/unlink` -> 
Delete all information linked to your discord username

## Installation
1. Rename `.env.example` to `.env` and start filling the values as detailed below:
2. Sign Up or Login with your Riot account in their [Developer Portal](https://developer.riotgames.com/), request a developer API Key and add insert it into `RGAPI`. This key will have to be renewed every 24h.
