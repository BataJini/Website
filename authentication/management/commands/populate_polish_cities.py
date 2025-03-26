from django.core.management.base import BaseCommand
from authentication.models import PolishCity

class Command(BaseCommand):
    help = 'Populates the database with Polish cities'

    def handle(self, *args, **options):
        # List of major Polish cities with their voivodeships
        cities_data = [
            {"name": "Warszawa", "voivodeship": "Mazowieckie", "population": 1793579},
            {"name": "Kraków", "voivodeship": "Małopolskie", "population": 779115},
            {"name": "Łódź", "voivodeship": "Łódzkie", "population": 679941},
            {"name": "Wrocław", "voivodeship": "Dolnośląskie", "population": 643782},
            {"name": "Poznań", "voivodeship": "Wielkopolskie", "population": 534813},
            {"name": "Gdańsk", "voivodeship": "Pomorskie", "population": 470907},
            {"name": "Szczecin", "voivodeship": "Zachodniopomorskie", "population": 401907},
            {"name": "Bydgoszcz", "voivodeship": "Kujawsko-Pomorskie", "population": 348190},
            {"name": "Lublin", "voivodeship": "Lubelskie", "population": 339682},
            {"name": "Białystok", "voivodeship": "Podlaskie", "population": 297554},
            {"name": "Katowice", "voivodeship": "Śląskie", "population": 294510},
            {"name": "Gdynia", "voivodeship": "Pomorskie", "population": 246348},
            {"name": "Częstochowa", "voivodeship": "Śląskie", "population": 222292},
            {"name": "Radom", "voivodeship": "Mazowieckie", "population": 211371},
            {"name": "Toruń", "voivodeship": "Kujawsko-Pomorskie", "population": 201447},
            {"name": "Sosnowiec", "voivodeship": "Śląskie", "population": 199974},
            {"name": "Rzeszów", "voivodeship": "Podkarpackie", "population": 196208},
            {"name": "Kielce", "voivodeship": "Świętokrzyskie", "population": 195774},
            {"name": "Gliwice", "voivodeship": "Śląskie", "population": 178603},
            {"name": "Olsztyn", "voivodeship": "Warmińsko-Mazurskie", "population": 171979},
            {"name": "Zabrze", "voivodeship": "Śląskie", "population": 171661},
            {"name": "Bielsko-Biała", "voivodeship": "Śląskie", "population": 170663},
            {"name": "Bytom", "voivodeship": "Śląskie", "population": 165263},
            {"name": "Zielona Góra", "voivodeship": "Lubuskie", "population": 141222},
            {"name": "Rybnik", "voivodeship": "Śląskie", "population": 138098},
            {"name": "Ruda Śląska", "voivodeship": "Śląskie", "population": 137360},
            {"name": "Opole", "voivodeship": "Opolskie", "population": 127792},
            {"name": "Tychy", "voivodeship": "Śląskie", "population": 127307},
            {"name": "Gorzów Wielkopolski", "voivodeship": "Lubuskie", "population": 123609},
            {"name": "Płock", "voivodeship": "Mazowieckie", "population": 119425},
        ]

        for city_data in cities_data:
            PolishCity.objects.get_or_create(
                name=city_data["name"],
                defaults={
                    "voivodeship": city_data["voivodeship"],
                    "population": city_data["population"]
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated Polish cities')) 