from django.core.management.base import BaseCommand
from authentication.models import Job
from django.db.models import Count
from django.db.models.functions import Concat
from django.db.models import Value
from django.db.models import F

class Command(BaseCommand):
    help = 'Merges identical jobs that only differ in location into a single job with multiple locations'

    def handle(self, *args, **options):
        # Process all jobs with multiple locations (containing commas)
        jobs_with_multiple_locations = Job.objects.filter(location__contains=',')
        
        updated_count = 0
        for job in jobs_with_multiple_locations:
            # Split and clean locations
            locations = [loc.strip() for loc in job.location.split(',')]
            
            # Limit to 15 locations
            if len(locations) > 15:
                locations = locations[:15]
                job.location = ', '.join(locations)
                job.save()
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Limited locations for job: {job.title} at {job.company} '
                        f'(limited to 15 locations)'
                    )
                )

        # Now process any new duplicates
        jobs = Job.objects.values('title', 'company').annotate(
            count=Count('id')
        ).filter(count__gt=1)  # Only get jobs that have duplicates

        merged_count = 0
        for job in jobs:
            # Get all instances of this job
            job_instances = Job.objects.filter(
                title=job['title'],
                company=job['company']
            ).order_by('id')

            # Get the first instance as the base
            base_job = job_instances.first()
            
            # Get all locations (limit to 15)
            locations = list(job_instances.values_list('location', flat=True).distinct())[:15]
            
            # Update the base job with all locations
            base_job.location = ', '.join(locations)
            base_job.save()
            
            # Delete other instances
            job_instances.exclude(id=base_job.id).delete()
            
            # Count total locations before limiting
            total_locations = len(locations)
            
            merged_count += 1
            if total_locations > 15:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully merged job: {base_job.title} at {base_job.company} '
                        f'(limited from {total_locations} to 15 locations)'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully merged {len(locations)} instances of job: {base_job.title} at {base_job.company}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {updated_count} existing jobs and merged {merged_count} groups of duplicate jobs'
            )
        ) 