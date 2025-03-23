import json
from django.core.management.base import BaseCommand
from authentication.models import Job
from django.utils import timezone
from datetime import datetime
import requests
from io import BytesIO
from django.core.files import File

class Command(BaseCommand):
    help = 'Import jobs from NoFluffJobs JSON files'

    def add_arguments(self, parser):
        parser.add_argument('--nofluff', type=str, help='Path to nofluff_data.json')
        parser.add_argument('--desc', type=str, help='Path to desc_data.json')
        parser.add_argument('--response', type=str, help='Path to nofluff_response.json')

    def download_logo(self, logo_url):
        try:
            # Add base URL if it's a relative path
            if not logo_url.startswith(('http://', 'https://')):
                logo_url = f"https://nofluffjobs.com/{logo_url}"
                
            response = requests.get(logo_url)
            if response.status_code == 200:
                # Get the filename from the URL
                filename = logo_url.split('/')[-1]
                # Create a file-like object from the response content
                img_temp = BytesIO(response.content)
                return File(img_temp, name=filename)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Failed to download logo: {str(e)}'))
        return None

    def format_salary(self, salary_data):
        """Format salary information in a human-readable format"""
        if not salary_data:
            return "Salary not specified"
            
        try:
            # If it's already properly formatted as a string with range and currency, return it
            if isinstance(salary_data, str):
                # Check for properly formatted salary strings
                if (('-' in salary_data and ' PLN' in salary_data) or
                    ('From ' in salary_data and ' PLN' in salary_data) or
                    ('Up to ' in salary_data and ' PLN' in salary_data) or
                    ('Salary in ' in salary_data)):
                    return salary_data
                    
                # Try to parse the string as JSON if it looks like a dictionary
                if '{' in salary_data and '}' in salary_data:
                    try:
                        # Try to convert string to dictionary using json
                        salary_data = json.loads(salary_data.replace("'", '"'))
                    except json.JSONDecodeError:
                        pass
            
            # Handle dictionary format
            if isinstance(salary_data, dict):
                # For salary ranges with from/to values
                if 'from' in salary_data and salary_data.get('from'):
                    try:
                        salary_from = int(salary_data.get('from', 0))
                        salary_to = int(salary_data.get('to', 0)) if salary_data.get('to') else 0
                        currency = salary_data.get('currency', 'PLN')
                        
                        # Format the salary range
                        if salary_from and salary_to:
                            return f"{salary_from}-{salary_to} {currency}"
                        elif salary_from:
                            return f"From {salary_from} {currency}"
                        elif salary_to:
                            return f"Up to {salary_to} {currency}"
                    except (ValueError, TypeError):
                        # Handle conversion errors
                        pass
                
                # For other dictionary formats (where 'from'/'to' might not exist)
                currency = salary_data.get('currency', 'PLN')
                return f"Salary in {currency}"
                    
            # Default fallback - return as simple string
            if isinstance(salary_data, str):
                return salary_data
                
            return str(salary_data)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Error formatting salary: {str(e)}'))
            
            # Try to extract currency from the dictionary if possible
            if isinstance(salary_data, dict) and 'currency' in salary_data:
                return f"Salary in {salary_data['currency']}"
            
            return "Salary not specified"

    def format_responsibilities(self, responsibilities):
        """Format responsibilities as HTML"""
        result = ""
        
        if responsibilities and len(responsibilities) > 0:
            result += "<h4>Your Responsibilities:</h4>\n<ul>"
            for task in responsibilities:
                if isinstance(task, dict) and 'value' in task:
                    result += f"\n<li>{task['value']}</li>"
                elif isinstance(task, str):
                    result += f"\n<li>{task}</li>"
            result += "\n</ul>"
            
        return result

    def extract_must_have_skills(self, must_haves):
        """Extract must-have skills as a JSON array for display in the skills card"""
        if not must_haves:
            return None
            
        skills = []
        for skill in must_haves:
            if isinstance(skill, dict) and 'value' in skill:
                skills.append(skill['value'])
            elif isinstance(skill, str):
                skills.append(skill)
                
        if skills:
            return json.dumps(skills)
        return None
        
    def extract_nice_to_have_skills(self, nice_haves):
        """Extract nice-to-have skills as a JSON array for display in the skills card"""
        if not nice_haves:
            return None
            
        skills = []
        for skill in nice_haves:
            if isinstance(skill, dict) and 'value' in skill:
                skills.append(skill['value'])
            elif isinstance(skill, str):
                skills.append(skill)
                
        if skills:
            return json.dumps(skills)
        return None

    def handle(self, *args, **options):
        try:
            # Read nofluff_data.json which contains an array of job listings
            with open(options['nofluff'], 'r', encoding='utf-8') as f:
                nofluff_data = json.load(f)

            # Counter for tracking
            jobs_created = 0
            jobs_updated = 0

            for job_data in nofluff_data:
                # Get location
                location = "Remote"
                is_remote = False
                
                if isinstance(job_data.get('location'), dict) and 'places' in job_data.get('location', {}):
                    places = job_data['location']['places']
                    if places and len(places) > 0:
                        location = places[0].get('city', 'Remote')
                        
                # Check if job is remote
                is_remote = job_data.get('is_remote', False) or 'remote' in str(location).lower()
                
                # If remote, update the location string accordingly
                if is_remote and 'remote' not in str(location).lower():
                    location = f"{location} (Remote)"
                
                # Format responsibilities as HTML for the Your Responsibilities card
                formatted_responsibilities = self.format_responsibilities(
                    job_data.get('responsibilities', [])
                )
                
                # Extract must-have and nice-to-have skills for the respective cards
                must_have_skills = self.extract_must_have_skills(job_data.get('must_haves', []))
                nice_to_have_skills = self.extract_nice_to_have_skills(job_data.get('nice_to_have', []))
                
                # Format salary
                formatted_salary = self.format_salary(job_data.get('salary_range', ''))
                
                # Prepare job data
                job_defaults = {
                    'description': job_data.get('full_description', ''),
                    'salary': formatted_salary,
                    'job_url': job_data.get('job_post_url', ''),
                    'is_remote': is_remote,
                    'type': job_data.get('employment_type', 'Full-time'),
                    'posted_date': timezone.now(),
                }

                # Try to find existing job by title and company
                existing_jobs = Job.objects.filter(
                    title=job_data.get('title', ''),
                    company=job_data.get('company', '')
                )
                
                if existing_jobs.exists():
                    # Update existing job
                    job = existing_jobs.first()
                    # Update job data including location
                    for key, value in job_defaults.items():
                        setattr(job, key, value)
                    job.location = location
                    job.save()
                    created = False
                else:
                    # Create new job
                    job = Job(
                        title=job_data.get('title', ''),
                        company=job_data.get('company', ''),
                        location=location,
                        **job_defaults
                    )
                    job.save()
                    created = True

                # Add must-have skills to requirements field
                if must_have_skills:
                    job.requirements = must_have_skills
                    
                # Save formatted responsibilities to requirements if there are no must-have skills
                # or to description if must-have skills exist
                if formatted_responsibilities:
                    if not must_have_skills:
                        job.requirements = formatted_responsibilities
                    else:
                        # If we have both, append responsibilities to the description
                        current_desc = job.description or ""
                        if not current_desc.endswith(formatted_responsibilities):
                            job.description = current_desc + "\n\n" + formatted_responsibilities
                
                # Add nice-to-have skills field
                if nice_to_have_skills:
                    job.nice_to_have = nice_to_have_skills
                    
                # Save changes
                job.save()

                # Download and save company logo
                if job_data.get('logo'):
                    logo_file = self.download_logo(job_data['logo'])
                    if logo_file:
                        job.company_logo = logo_file
                        job.save()
                        
                # Add skills as tags
                if 'must_haves' in job_data and job_data['must_haves']:
                    # Clear existing tags first to avoid duplicates on updates
                    if hasattr(job, 'tags'):
                        job.tags.clear()
                    
                    # Add each skill as a tag
                    for skill in job_data['must_haves']:
                        try:
                            # Check if skill is a dict or string
                            if isinstance(skill, dict) and 'value' in skill:
                                skill_name = skill['value']
                            elif isinstance(skill, str):
                                skill_name = skill
                            else:
                                continue
                                
                            if skill_name and len(skill_name) > 0:
                                if hasattr(job, 'tags'):
                                    job.tags.add(skill_name)
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'Error adding tag: {str(e)} for skill {skill}'))

                if created:
                    jobs_created += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created job: {job.title} at {job.company}')
                    )
                else:
                    jobs_updated += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Updated job: {job.title} at {job.company}')
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f'\nImport completed:\n'
                    f'Created: {jobs_created} jobs\n'
                    f'Updated: {jobs_updated} jobs'
                )
            )

        except FileNotFoundError as e:
            self.stdout.write(
                self.style.ERROR(f'File not found: {str(e)}')
            )
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f'Invalid JSON in file: {str(e)}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during import: {str(e)}')
            ) 