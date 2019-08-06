import json


class Config:
    """Klasa operuje na pliku konfiguracyjnym i przechowuej pobrane z niego wartości"""
    def __init__(self, data):
        """Inicjalizuje klasę config danymi z pliku konifguracyjnego  i nazwą pliku konfiguracyjnego"""
        self.config_data = data['config_data']
        self.config_file = data['config_file']

    @staticmethod
    def load_config(file):
        """Wczytuje dane z pliku i zwraca je w formie json"""
        with open(file) as config_file:
            data = {'config_data': json.load(config_file), 'config_file': file}
            return data

    async def update_config(self, channel):
        """Aktualizuje zmienne konfiguracyjne"""
        with open('config.json') as config_file:
            self.config_data = json.load(config_file)
        await channel.send('Wcztano nowy plik konfiguracyjny.')

    async def set_config(self, key, value, channel):
        """Ustawia w pliku config.json klucz na key i wartosć na value"""
        # TODO Dodawanie i odejmowanie z tablic w config.json, zabezpieczenie tokenu i tablic.
        if key in self.config_data:
            with open(self.config_file, 'r+') as config_file:
                data = json.load(config_file)
                data[key] = value
                config_file.seek(0)
                json.dump(data, config_file, indent=4)
                config_file.truncate()
                await channel.send('Ustawiono "{0}" na wartość "{1}".'.format(key, value))
                self.load_config(self.config_file)
        else:
            await channel.send('Brak klucza "{0}".'.format(key))

    def get(self, key):
        """Zwraca wartość konfigruacji dla klucza"""
        return self.config_data[key]
