from django.core.management.base import BaseCommand
from authentication.models import PolishCity
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Deletes all cities and repopulates them'

    def handle(self, *args, **options):
        # Delete all existing cities
        count = PolishCity.objects.all().count()
        PolishCity.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} existing cities'))
        
        # Run the populate command
        call_command('populate_polish_cities')
        
        # Confirm completion
        new_count = PolishCity.objects.all().count()
        self.stdout.write(self.style.SUCCESS(f'Successfully populated {new_count} cities')) 