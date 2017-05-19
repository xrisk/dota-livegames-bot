import _thread
import asyncio
import config
import discord
import dota2api
import os

from flask import Flask
app = Flask(__name__)

api = dota2api.Initialise(config.get("D2_API_KEY"))
client = discord.Client()

paused = False


def get_games():
    resp = api.get_live_league_games()
    ret = []
    for game in resp['games']:
        if game['league_id'] == 5157:
            ret.append(game)
    return ret


def describe(game, time=False):

    radiant, dire = "Radiant", "Dire"
    try:
        radiant = game['radiant_team']['team_name']
    except:
        pass
    try:
        dire = game['dire_team']['team_name']
    except:
        pass

    num = game.get('game_number', 1)

    if time:
        time = 0
        try:
            time = int(game['scoreboard']['duration']) // 60
        except:
            pass
        return '{} vs {} Game {} ({} mins)'.format(radiant, dire, num, time)
    else:
        return '{} vs {} Game {}'.format(radiant, dire, num)


def get_winner(mid):
    i = api.get_match_details(match_id=mid)

    if i['radiant_win']:
        if 'radiant_team' in i:
            return i['radiant_team']['team_name']
        elif 'radiant_guild_name' in i:
            return i['radiant_guild_name']
        elif 'radiant_name' in i:
            return i['radiant_name']
        else:
            return "Radiant"
    else:
        if 'dire_team' in i:
            return i['radiant_team']['team_name']
        elif 'dire_guild_name' in i:
            return i['dire_guild_name']
        elif 'dire_name' in i:
            return i['dire_name']
        else:
            return "Dire"


@client.event
async def on_message(message):
    global paused
    if message.content.startswith('!live'):
        await client.send_message(message.channel, describe_live_games())
    elif message.content.startswith('!pause'):
        paused = True
        await client.send_message(message.channel, "The bot is paused.")
    elif message.content.startswith('!resume'):
        paused = False
        await client.send_message(message.channel,
                                  "The bot has been unpaused.")


async def update_tracker(last_known):

    if not paused:
        current = get_games()
        msg = []

        print([x.get('match_id', -1) for x in last_known])
        print(list([x['match_id'] for x in current]))

        for i in range(len(last_known)):
            if last_known[i] != {}:
                mid = last_known[i]['match_id']
                if mid not in [x['match_id'] for x in current]:
                    d = describe(last_known[i])
                    print(mid)
                    try:
                        victor = get_winner(mid)
                        msg.append("{} has finished. {} victorious!".
                                   format(d, victor))
                    except:
                        pass
                    last_known[i] = {}  # dirty hack

        for i in current:
            d = describe(i)
            mid = i['match_id']
            if mid not in [x.get('match_id', -1) for x in last_known]:
                msg.append("{} has started!".format(d))
                last_known.append(i)

        if msg:
            await client.send_message(client.get_channel(
                                      config.get("DISCORD_CHANNEL_ID")),
                                      "\n".join(msg))

    await asyncio.sleep(60)
    await update_tracker(last_known)


@client.event
async def on_ready():
    await update_tracker([])
    # loop = asyncio.get_event_loop()
    # loop.call_soon(update_tracker, [], loop)


@app.route('/')
def describe_live_games():
    games = get_games()
    if games:
        return "\n".join([describe(x, True) for x in get_games()])
    else:
        return "No games in progress."

if __name__ == "__main__":
    client.run(config.get("DISCORD_KEY"))
