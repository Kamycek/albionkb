import requests
import discord
from discord import Embed
from PIL import Image


class Killboard:
    # TODO Kolejnosc eventow
    __showed_events = [None] * 51

    @staticmethod
    def get_data(events_quantity):
        """Pobiera dane z api"""
        r = requests.get('https://gameinfo.albiononline.com/api/gameinfo/events?limit={0}&offset=0'
                         .format(events_quantity))
        data = r.json()
        return data

    @staticmethod
    async def validate_data(data, tracked_guilds, tracked_alliances, tracked_players, channel, client):
        """Przetwarza dane i przekazuje do show_data dane do wyświetleniaw postaci pojedynczych eventów"""
        events = []
        for single_event in data:
            if (single_event['EventId'] not in Killboard.__showed_events
                    and (single_event['Killer']['GuildName'] in tracked_guilds
                         or single_event['Victim']['GuildName'] in tracked_guilds
                         or single_event['Killer']['Name'] in tracked_players
                         or single_event['Victim']['Name'] in tracked_players
                         or (single_event['Killer']['AllianceName'] != ""
                             and single_event['Killer']['AllianceName'] in tracked_alliances)
                         or (single_event['Victim']['AllianceName'] != ""
                             and single_event['Victim']['AllianceName'] in tracked_alliances))):
                Killboard.__showed_events.append(single_event['EventId'])
                Killboard.__showed_events.pop(0)
                events.append(single_event)
            for event in events:
                await Killboard.show_data(event, channel, client)
                print(event)
            events = []

    @staticmethod
    def __round_ip(ip):
        """Przyjmujes string ip zaokragla i zwraca jako string"""
        ip = round(float(ip))
        return str(ip)

    @staticmethod
    def __merge_img(img1, img2, event, color, kg, vg, client, channel):
        """Przyjmuej url 2 img, łączy je i zwraca"""
        img1 = Image.open(requests.get(img1, stream=True).raw)
        img1 = img1.resize((55, 55))
        img2 = Image.open(requests.get(img2, stream=True).raw)
        img2 = img2.resize((55, 55))
        bg = Image.new('RGBA', (360, 62), (0, 0, 0, 0))
        bg.paste(img1, (3, 4))
        bg.paste(img2, (242, 4))
        bg.save('./kill.png')

        embed = Embed(title='{0} zabił {1}'.format(event['Killer']['Name'], event['Victim']['Name']),
                      description='Zabójstwo asystowane przez {0} graczy.'.format(
                          event['numberOfParticipants']),
                      url='https://www.albiononline2d.com/en/scoreboard/events/{0}'.format(
                          event['EventId']),
                      color=color)
        embed.set_thumbnail(
            url='https://images-ext-2.discordapp.net/external/GnRbnzo76l06gqCQldieMDQitXEu6ahWoNVjOaAANGQ/https/albiononline2d.ams3.cdn.digitaloceanspaces.com/images/SA_COLLECTION_HITPOINTS_UNLOCKED.png')
        embed.set_image(url='attachment://kill.png')
        embed.add_field(
            name='Sława', value=event['TotalVictimKillFame'], inline=False)
        embed.add_field(name='Gildia Zabójcy', value=kg, inline=True)
        embed.add_field(name='Gildia Ofiary', value=vg, inline=True)
        embed.add_field(name='MP Zabójcy', value=Killboard.__round_ip(
            event['Killer']['AverageItemPower']), inline=True)
        embed.add_field(name='MP Ofiary', value=Killboard.__round_ip(
            event['Victim']['AverageItemPower']), inline=True)
        return embed

    @staticmethod
    async def show_data(event, channel, client):
        """Przyjmuje 1 event i wyświetla dane"""
        color = 0x0000ff
        # TODO Pobrać nazwę gildii z configu (zrobić przyjazne gildie)
        # TODO 1 gracza zamaist graczy w opisie
        # TODO Za długie nazwy gildii
        if event['Killer']['GuildName'] == 'Zakon Bialego Wilka':
            color = 0x00ff00
        elif event['Victim']['GuildName'] == 'Zakon Bialego Wilka':
            color = 0xff0000
        # TODO Uprościć
        k_guild = event['Killer']['GuildName']
        k_alliance = event['Killer']['AllianceName']
        v_guild = event['Victim']['GuildName']
        v_alliance = event['Victim']['AllianceName']
        kg = '[{0} - {1}]'.format(k_alliance, k_guild)
        if kg.startswith('[ -'):
            kg = kg.replace(' - ', '')
            kg = kg.replace('[]', '—')
        vg = '[{0} - {1}]\n'.format(v_alliance, v_guild)
        if vg.startswith('[ -'):
            vg = vg.replace(' - ', '')
            vg = vg.replace('[]', '—')
        embed = Killboard.__merge_img('https://albiononline2d.ams3.cdn.digitaloceanspaces.com/thumbnails/orig/{0}'.format(event['Killer']['Equipment']['MainHand']['Type']),
                                      'https://albiononline2d.ams3.cdn.digitaloceanspaces.com/thumbnails/orig/{0}'.format(
                                          event['Victim']['Equipment']['MainHand']['Type']),
                                      event, color, kg, vg, client, channel)
        await channel.send(embed=embed, file=discord.File('./kill.png'))
