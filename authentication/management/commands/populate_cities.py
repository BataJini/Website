from django.core.management.base import BaseCommand
from authentication.models import City

class Command(BaseCommand):
    help = 'Populates the database with Polish cities'

    def handle(self, *args, **kwargs):
        polish_cities = [
            "Warszawa", "Kraków", "Łódź", "Wrocław", "Poznań", "Gdańsk", 
            "Szczecin", "Bydgoszcz", "Lublin", "Katowice", "Białystok",
            "Gdynia", "Częstochowa", "Radom", "Sosnowiec", "Toruń",
            "Kielce", "Rzeszów", "Gliwice", "Zabrze", "Olsztyn",
            "Bielsko-Biała", "Bytom", "Zielona Góra", "Rybnik",
            "Ruda Śląska", "Opole", "Tychy", "Gorzów Wielkopolski",
            "Elbląg", "Płock", "Dąbrowa Górnicza", "Wałbrzych"
        ]

        for city_name in polish_cities:
            City.objects.get_or_create(name=city_name)
            self.stdout.write(self.style.SUCCESS(f'Successfully added city "{city_name}"')) 