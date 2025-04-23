import re
from django.core.management.base import BaseCommand
from authentication.models import Job

class Command(BaseCommand):
    help = 'Remove jobs with Polish titles from the database'

    def is_polish_text(self, text):
        """
        Detect if text is likely in Polish by checking for Polish-specific characters
        and common Polish words.
        """
        if not text:
            return False
            
        # Polish specific characters
        polish_chars = set('ąćęłńóśźż')
        
        # Common Polish words that indicate Polish language
        polish_words = [
            'stanowisko', 'praca', 'oferta', 'umowa', 'zlecenie', 
            'specjalista', 'kierownik', 'oraz', 'obowiązki', 'wymagania',
            'pracownik', 'firma', 'spółka', 'ogłoszenie', 'zatrudni'
        ]
        
        # Convert to lowercase for comparison
        text_lower = text.lower()
        
        # Check for Polish characters
        if any(char in polish_chars for char in text_lower):
            return True
            
        # Check for common Polish words
        for word in polish_words:
            if word in text_lower:
                return True
                
        # Check for Polish-like word endings
        if re.search(r'\b\w+(ość|cja|anie|enie|cie|ski|cki|czny)\b', text_lower):
            return True
            
        return False

    def is_tech_job(self, title, description):
        """
        Detect if job is in IT/tech/development field
        """
        if not title and not description:
            return False
            
        # Convert to lowercase for comparison
        title_lower = title.lower() if title else ''
        desc_lower = description.lower() if description else ''
        
        # Common IT/tech/development keywords
        tech_keywords = [
            'developer', 'engineer', 'programmer', 'software', 'frontend', 'backend',
            'fullstack', 'full-stack', 'devops', 'sre', 'data', 'analyst', 'architect',
            'qa', 'tester', 'cyber', 'security', 'it', 'tech', 'technical', 'web',
            'mobile', 'ios', 'android', 'cloud', 'aws', 'azure', 'gcp', 'python',
            'java', 'javascript', 'react', 'angular', 'vue', 'node', 'ruby', 'php',
            'c#', 'c++', 'go', 'rust', 'scala', 'kotlin', 'swift', 'sql', 'database',
            'machine learning', 'ai', 'artificial intelligence', 'blockchain',
            'devops', 'sre', 'infrastructure', 'network', 'system', 'admin'
        ]
        
        # Check if any tech keyword is in title or description
        for keyword in tech_keywords:
            if keyword in title_lower or keyword in desc_lower:
                return True
                
        return False

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show which jobs would be deleted without actually deleting them',
        )
        parser.add_argument(
            '--keep-tech-only',
            action='store_true',
            help='Keep only tech jobs and delete all others',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        keep_tech_only = options.get('keep_tech_only', False)
        
        # Get all jobs
        jobs = Job.objects.all()
        jobs_to_delete = []
        
        # Filter jobs based on criteria
        for job in jobs:
            should_delete = False
            
            # Check for Polish content
            if self.is_polish_text(job.title) or self.is_polish_text(job.description):
                should_delete = True
                reason = "Polish content"
            
            # Check for non-tech jobs if keep_tech_only is enabled
            elif keep_tech_only and not self.is_tech_job(job.title, job.description):
                should_delete = True
                reason = "Non-tech job"
            
            if should_delete:
                jobs_to_delete.append((job, reason))
        
        # Print summary
        self.stdout.write(
            self.style.WARNING(f'Found {len(jobs_to_delete)} jobs to delete')
        )
        
        # List jobs that will be deleted
        for job, reason in jobs_to_delete:
            self.stdout.write(f'  - {job.title} at {job.company} ({reason})')
            if self.is_polish_text(job.description):
                self.stdout.write('    (Polish content in description)')
            elif keep_tech_only and not self.is_tech_job(job.title, job.description):
                self.stdout.write('    (Non-tech job)')
        
        # Delete jobs if not in dry run mode
        if not dry_run and jobs_to_delete:
            job_ids = [job.id for job, _ in jobs_to_delete]
            Job.objects.filter(id__in=job_ids).delete()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {len(jobs_to_delete)} jobs')
            )
        elif dry_run:
            self.stdout.write(
                self.style.WARNING('Dry run completed. No jobs were deleted.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('No jobs found to delete.')
            ) 