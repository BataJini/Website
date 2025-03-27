from django.core.management.base import BaseCommand
from authentication.models import Job
from django.db.models import Count
from django.db.models.functions import Lower, Trim

class Command(BaseCommand):
    help = 'Removes duplicate jobs based on title, company, and location (case-insensitive)'

    def handle(self, *args, **options):
        # Find duplicates based on normalized title, company, and location
        duplicates = Job.objects.annotate(
            normalized_title=Trim(Lower('title')),
            normalized_company=Trim(Lower('company')),
            normalized_location=Trim(Lower('location'))
        ).values('normalized_title', 'normalized_company', 'normalized_location').annotate(
            count=Count('id')
        ).filter(count__gt=1)

        total_duplicates = 0
        for duplicate in duplicates:
            # Get all jobs with this combination (case-insensitive)
            jobs = Job.objects.filter(
                title__iexact=duplicate['normalized_title'],
                company__iexact=duplicate['normalized_company'],
                location__iexact=duplicate['normalized_location']
            ).order_by('-posted_date')

            # Keep the most recent job and delete others
            jobs_to_delete = jobs[1:]
            for job in jobs_to_delete:
                self.stdout.write(
                    self.style.WARNING(
                        f'Deleting duplicate job: {job.title} at {job.company} in {job.location}'
                    )
                )
                job.delete()
                total_duplicates += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully removed {total_duplicates} duplicate jobs'
            )
        ) 