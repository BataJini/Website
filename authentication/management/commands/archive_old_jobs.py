from django.core.management.base import BaseCommand
from authentication.models import Job
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Archives jobs that are more than 2 months old'

    def handle(self, *args, **options):
        # Calculate the date 2 months ago
        two_months_ago = timezone.now() - timedelta(days=60)  # 60 days = ~2 months
        
        # Get all active jobs older than 2 months
        old_jobs = Job.objects.filter(
            is_archived=False,
            posted_date__lt=two_months_ago
        )
        
        # Count of jobs to be archived
        jobs_count = old_jobs.count()
        
        if jobs_count > 0:
            # Archive the jobs
            old_jobs.update(is_archived=True)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully archived {jobs_count} jobs that were more than 2 months old.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('No jobs found that need to be archived.')
            ) 