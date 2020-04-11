import discord
import asyncio
from config import Config
from killboard import Killboard

client = discord.Client()
config = Config(Config.load_config('config.json'))
is_tracking_running = False


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.content == "{0}on".format(config.get('prefix')):
        global is_tracking_running
        is_tracking_running = not is_tracking_running
        print('Przełączono')
        while is_tracking_running:
            await Killboard.validate_data(Killboard.get_data(config.get('events_quantity')),
                                          config.get('tracked_guilds'),
                                          config.get('tracked_alliances'),
                                          config.get('tracked_players'),
                                          message.channel,
                                          client)
            print('Przeanalizowano dane.')
            await asyncio.sleep(config.get('sleep_time'))

    if message.content == "{0}reload".format(config.get('prefix')):
        await config.update_config(message.channel)

    if message.content.startswith("{0}ustaw".format(config.get('prefix'))):
        data = message.content.split()
        await config.set_config(data[1], data[2], message.channel)
        await config.update_config(message.channel)


client.run(config.get('token'))
