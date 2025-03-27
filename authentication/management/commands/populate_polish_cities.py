from django.core.management.base import BaseCommand
from authentication.models import PolishCity

class Command(BaseCommand):
    help = 'Populates the database with Polish cities'

    def handle(self, *args, **options):
        # List of major Polish cities with their voivodeships and Polish names
        cities_data = [
            {"name": "Warsaw", "name_pl": "Warszawa", "voivodeship": "Mazowieckie", "population": 1793579},
            {"name": "Krakow", "name_pl": "Kraków", "voivodeship": "Małopolskie", "population": 779115},
            {"name": "Lodz", "name_pl": "Łódź", "voivodeship": "Łódzkie", "population": 679941},
            {"name": "Wroclaw", "name_pl": "Wrocław", "voivodeship": "Dolnośląskie", "population": 643782},
            {"name": "Poznan", "name_pl": "Poznań", "voivodeship": "Wielkopolskie", "population": 534813},
            {"name": "Gdansk", "name_pl": "Gdańsk", "voivodeship": "Pomorskie", "population": 470907},
            {"name": "Szczecin", "name_pl": "Szczecin", "voivodeship": "Zachodniopomorskie", "population": 401907},
            {"name": "Bydgoszcz", "name_pl": "Bydgoszcz", "voivodeship": "Kujawsko-Pomorskie", "population": 348190},
            {"name": "Lublin", "name_pl": "Lublin", "voivodeship": "Lubelskie", "population": 339682},
            {"name": "Bialystok", "name_pl": "Białystok", "voivodeship": "Podlaskie", "population": 297554},
            {"name": "Katowice", "name_pl": "Katowice", "voivodeship": "Śląskie", "population": 294510},
            {"name": "Gdynia", "name_pl": "Gdynia", "voivodeship": "Pomorskie", "population": 246348},
            {"name": "Czestochowa", "name_pl": "Częstochowa", "voivodeship": "Śląskie", "population": 222292},
            {"name": "Radom", "name_pl": "Radom", "voivodeship": "Mazowieckie", "population": 211371},
            {"name": "Torun", "name_pl": "Toruń", "voivodeship": "Kujawsko-Pomorskie", "population": 201447},
            {"name": "Sosnowiec", "name_pl": "Sosnowiec", "voivodeship": "Śląskie", "population": 199974},
            {"name": "Rzeszow", "name_pl": "Rzeszów", "voivodeship": "Podkarpackie", "population": 196208},
            {"name": "Kielce", "name_pl": "Kielce", "voivodeship": "Świętokrzyskie", "population": 195774},
            {"name": "Gliwice", "name_pl": "Gliwice", "voivodeship": "Śląskie", "population": 178603},
            {"name": "Olsztyn", "name_pl": "Olsztyn", "voivodeship": "Warmińsko-Mazurskie", "population": 171979},
            {"name": "Zabrze", "name_pl": "Zabrze", "voivodeship": "Śląskie", "population": 171661},
            {"name": "Bielsko-Biala", "name_pl": "Bielsko-Biała", "voivodeship": "Śląskie", "population": 170663},
            {"name": "Bytom", "name_pl": "Bytom", "voivodeship": "Śląskie", "population": 165263},
            {"name": "Zielona Gora", "name_pl": "Zielona Góra", "voivodeship": "Lubuskie", "population": 141222},
            {"name": "Rybnik", "name_pl": "Rybnik", "voivodeship": "Śląskie", "population": 138098},
            {"name": "Ruda Slaska", "name_pl": "Ruda Śląska", "voivodeship": "Śląskie", "population": 137360},
            {"name": "Opole", "name_pl": "Opole", "voivodeship": "Opolskie", "population": 127792},
            {"name": "Tychy", "name_pl": "Tychy", "voivodeship": "Śląskie", "population": 127307},
            {"name": "Gorzow Wielkopolski", "name_pl": "Gorzów Wielkopolski", "voivodeship": "Lubuskie", "population": 123609},
            {"name": "Plock", "name_pl": "Płock", "voivodeship": "Mazowieckie", "population": 119425},
        ]

        # Update existing cities or create new ones
        for city_data in cities_data:
            city, created = PolishCity.objects.update_or_create(
                name=city_data["name"],
                defaults={
                    "name_pl": city_data["name_pl"],
                    "voivodeship": city_data["voivodeship"],
                    "population": city_data["population"]
                }
            )
            if created:
                action = "Created"
            else:
                action = "Updated"
            self.stdout.write(f"{action} city: {city.name} (PL: {city.name_pl})")

        self.stdout.write(self.style.SUCCESS('Successfully populated Polish cities')) 