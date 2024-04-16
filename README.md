# Winter's Claw
**All the Stats you need.** <br>
**Right where you need them.** <br> <br>
Useful links:
- [Add the Bot](https://discord.com/oauth2/authorize?client_id=1137848588521713674)
- [Official Website](https://wintersclaw-lol.vercel.app)
- Join the official [support server](https://discord.com/invite/Z3nc6b4nWv)
## 📝 Description
Welcome to Winter's Claw, a Discord Bot showing you all kinds of personal and global statistics for Riot Games' Teamfight Tactics, utilizing the discord.py library.
You can add the Bot [here](https://discord.com/oauth2/authorize?client_id=1137848588521713674) or host it yourself as explained in the [Installation](#installation).
- **Motivation:** When I first started this Bot as my first bigger project I was just looking for a fun way to engage more into programming, while combining it with something I already loved. 
It started out as just a nice little tool for me and a few friends to keep track of all our statistics inside the Discord 
server we were always in anyways and after Set 9 ended and we stopped playing it also ended as that.

- **Why I picked it back up:** When Set 11 released and looked as fun as Tft had ever been, I remembered this project and brought it up-to-date. 
After looking around a bit, I realised that there was no actively running Bot, offering what I originally planned to do with this project, so I decided to add more features and documentation to make it public.

- **Problem solved:** Winter's Claw removes the need of using third party websites and offers all the stats people need, right in their Discord server.

- **What I learned:** While building this project I learned a lot about programming and Python in general, while also getting deeper insights into how to use API requests and Coroutines.

- **Future Plans:** I plan to add more features to the bot by displaying more detailed personal stats and also offering current meta builds and other global statistics.

## 🤖 Commands
All stat commands have an optional input of specified Riot Id and Server. If not specified, it defaults to the summoner linked to your discord account with /link. <br>
This is a brief overview of commands the bot has to offer:
- `/help` - >
If you ever need help

- `/commands [command]` - >
Shows a list of all commands or more detailed information on given command

- `/link [riotId] [server]` -> 
Link a summoner to your discord username to quickly use all other commands

- `/linked` -> 
Shows the summoner linked to your discord username

- `/unlink` -> 
Delete all information linked to your discord username

- `/update [riotId] [server]` -> 
Download games of given or linked summoner into database (currently just downloading games from Set 11)

- `/stats [days] [count] [set] [riotId] [server]` -> 
Shows all your statistics for gamemodes, traits, units and augments. <br>
Information is navigatable through the buttons provided. Arguments offer to display data only from recent x games/days or a specified set (defaults to all games of current set).

- `/matchhistory [riotId] [server]` -> 
Shows information about the last 6 games

- `/singlematch [matchId] [riotId] [server]` -> 
Shows details about a specfic match for given or linked summoner. Match IDs are obtainable through /match_history (defaults to last match played)

## Installation
If you want to self host the Bot, follow these steps:
1. Create a `.env` file like shown in the .env.example and start filling the values as detailed below:
2. Sign Up or Login into Riot Games' [Developer Portal](https://developer.riotgames.com/), request a developer API Key and add insert it into `RGAPI`. This key will have to be renewed every 24h. <br>
If you want it to be permanent, submit a personal application [here](https://developer.riotgames.com/app-type)
3. Go to the Discord [Developer Portal](https://discord.com/developers) and create a new application. Insert the bot token to `DISCORD_TOKEN` <br>
- **Note:** By default your Bot will not be able to use any of the emoji. A command to set this up easily will be added in the future.

## 📜 License
This project is licensed under the GPL-3.0 license. For more information view the [License](LICENSE)
