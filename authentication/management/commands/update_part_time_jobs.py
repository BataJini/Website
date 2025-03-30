from django.core.management.base import BaseCommand
from authentication.models import Job
from django.db.models import Q

class Command(BaseCommand):
    help = 'Updates job types to Part-time based on title and description content'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        # First, let's see all jobs with 'part' in the title or description
        jobs_with_part = Job.objects.filter(
            Q(title__icontains='part') |
            Q(description__icontains='part time') |
            Q(description__icontains='part-time')
        )
        
        self.stdout.write("\nJobs containing 'part' in title or description:")
        for job in jobs_with_part:
            self.stdout.write(f"\nID: {job.id}")
            self.stdout.write(f"Title: {job.title}")
            self.stdout.write(f"Current type: {job.type}")
            if 'part' in job.title.lower():
                self.stdout.write("Found in: title")
            if job.description and ('part time' in job.description.lower() or 'part-time' in job.description.lower()):
                self.stdout.write("Found in: description")
            self.stdout.write("-" * 50)

        # Now check for various part-time variations
        part_time_variations = [
            'part time',
            'part-time',
            'parttime',
            'part_time',
            'ptime',
            'p/t',
            'part timer',
            'part-timer'
        ]
        
        # Build the query
        query = Q()
        for variation in part_time_variations:
            query |= Q(title__icontains=variation)
            query |= Q(description__icontains=variation)
            
        # Find matching jobs
        jobs = Job.objects.filter(query)

        self.stdout.write("\nJobs that should be part-time:")
        updated_count = 0
        for job in jobs:
            if job.type != 'Part-time':
                self.stdout.write(f"\nFound job to update:")
                self.stdout.write(f"ID: {job.id}")
                self.stdout.write(f"Title: {job.title}")
                self.stdout.write(f"Current type: {job.type}")
                
                if not options['dry_run']:
                    job.type = 'Part-time'
                    job.save()
                    self.stdout.write(self.style.SUCCESS("Updated to Part-time"))
                    updated_count += 1
                else:
                    self.stdout.write(self.style.WARNING("Would update to Part-time (dry run)"))

        self.stdout.write(self.style.SUCCESS(f'\nTotal jobs that would be updated: {updated_count}')) 