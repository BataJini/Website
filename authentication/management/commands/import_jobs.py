import json
from django.core.management.base import BaseCommand
from authentication.models import Job
from django.utils import timezone
from datetime import datetime
import requests
from io import BytesIO
from django.core.files import File
import re
import string

class Command(BaseCommand):
    help = 'Import jobs from NoFluffJobs JSON files'

    def add_arguments(self, parser):
        parser.add_argument('--nofluff', type=str, help='Path to nofluff_data.json')
        parser.add_argument('--desc', type=str, help='Path to desc_data.json')
        parser.add_argument('--response', type=str, help='Path to nofluff_response.json')
        parser.add_argument('--justjoin', type=str, help='Path to justjoin_it.json')

    def is_polish_text(self, text):
        """
        Detect if text is likely in Polish by checking for Polish-specific characters
        and common Polish words, ignoring company names, locations, and URLs.
        """
        if not text:
            return False

        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove common location patterns
        text = re.sub(r'\b(?:ul\.|ulica|al\.|aleja)\s+[^,]+,?\s*\d*(?:-\d+)?', '', text)
        
        # Remove company legal suffixes
        text = re.sub(r'\b(?:Sp\. z o\.o\.|S\.A\.|sp\. j\.|sp\. k\.)\b', '', text)
        
        # Polish specific characters
        polish_chars = set('ąćęłńóśźż')
        
        # Common Polish words that indicate Polish language content
        polish_words = [
            'stanowisko', 'praca', 'oferta', 'umowa', 'zlecenie', 
            'specjalista', 'kierownik', 'oraz', 'obowiązki', 'wymagania',
            'pracownik', 'firma', 'spółka', 'ogłoszenie', 'zatrudni',
            'kandydat', 'doświadczenie', 'wykształcenie'
        ]
        
        # Convert to lowercase for comparison
        text_lower = text.lower()
        
        # Count Polish characters (requiring multiple to reduce false positives)
        polish_char_count = sum(1 for char in text_lower if char in polish_chars)
        if polish_char_count > 2:  # Only flag if multiple Polish characters are found
            return True
            
        # Check for common Polish words (exact matches only)
        for word in polish_words:
            if f" {word} " in f" {text_lower} ":
                return True
                
        # Check for very specific Polish word endings that don't appear in English
        if re.search(r'\b\w+(ość|ąc|ęć|ść)\b', text_lower):
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
                return "Undisclosed"
                    
            # Default fallback - return as simple string
            if isinstance(salary_data, str):
                return salary_data
                
            return str(salary_data)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Error formatting salary: {str(e)}'))
            
            # Try to extract currency from the dictionary if possible
            if isinstance(salary_data, dict) and 'currency' in salary_data:
                return "Undisclosed"
            
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

    def format_justjoin_salary(self, salary_data):
        """Format JustJoin.it salary data"""
        if not salary_data:
            return "Salary not specified"
            
        try:
            if isinstance(salary_data, list):
                # JustJoin.it typically provides salary as a list of strings
                salary_str = ' '.join(salary_data)
                # Clean up the salary string
                salary_str = salary_str.replace('PLN', 'PLN').strip()
                return salary_str
            return str(salary_data)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Error formatting JustJoin.it salary: {str(e)}'))
            return "Salary not specified"

    def format_justjoin_description(self, description_data):
        """Format JustJoin.it description data"""
        if not description_data:
            return ""
            
        try:
            if isinstance(description_data, list):
                # Join all description items with proper HTML formatting
                description = "<div class='job-description'>"
                for item in description_data:
                    if item.strip():
                        description += f"<p>{item}</p>"
                description += "</div>"
                return description
            return str(description_data)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Error formatting JustJoin.it description: {str(e)}'))
            return ""

    def format_tech_stack(self, tech_stack):
        """Format tech stack as JSON array"""
        if not tech_stack:
            return None
            
        try:
            if isinstance(tech_stack, list):
                return json.dumps(tech_stack)
            return None
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Error formatting tech stack: {str(e)}'))
        return None

    def clear_json_file(self, file_path):
        """Clear the contents of a JSON file by writing an empty array"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump([], f)
            self.stdout.write(self.style.SUCCESS(f'Cleared contents of {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error clearing {file_path}: {str(e)}'))

    def handle(self, *args, **options):
        try:
            # Read nofluff_data.json which contains an array of job listings
            with open(options['nofluff'], 'r', encoding='utf-8') as f:
                nofluff_data = json.load(f)

            # Counter for tracking
            jobs_created = 0
            jobs_updated = 0
            jobs_skipped_polish = 0  # Counter for skipped Polish jobs
            jobs_skipped_non_tech = 0  # Counter for skipped non-tech jobs

            for job_data in nofluff_data:
                # Get title and description
                title = job_data.get('title', '')
                description = job_data.get('full_description', '')
                
                # Skip jobs with Polish content
                if self.is_polish_text(title) or self.is_polish_text(description):
                    self.stdout.write(self.style.WARNING(
                        f'Skipping job with Polish content: {title}'
                    ))
                    jobs_skipped_polish += 1
                    continue
                
                # Skip non-tech jobs
                if not self.is_tech_job(title, description):
                    self.stdout.write(self.style.WARNING(
                        f'Skipping non-tech job: {title}'
                    ))
                    jobs_skipped_non_tech += 1
                    continue
                
                # Get location
                location = "Remote"
                if isinstance(job_data.get('location'), dict) and 'places' in job_data.get('location', {}):
                    places = job_data['location']['places']
                    if places and len(places) > 0:
                        location = places[0].get('city', 'Remote')
                
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
                    'is_remote': 'Remote' in str(location),
                    'type': job_data.get('employment_type', 'Full-time'),
                    'posted_date': timezone.now(),
                }

                # Try to get or create the job
                job, created = Job.objects.get_or_create(
                    title=job_data.get('title', ''),
                    company=job_data.get('company', ''),
                    location=location,
                    defaults=job_defaults
                )

                # Update specific fields
                if not created:
                    for key, value in job_defaults.items():
                        setattr(job, key, value)
                
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

            # Print summary with added counters
            self.stdout.write(self.style.SUCCESS(
                    f'\nImport completed:\n'
                    f'Created: {jobs_created} jobs\n'
                f'Updated: {jobs_updated} jobs\n'
                f'Skipped Polish jobs: {jobs_skipped_polish}\n'
                f'Skipped non-tech jobs: {jobs_skipped_non_tech}'
            ))

            # Process JustJoin.it data
            if options['justjoin']:
                try:
                    with open(options['justjoin'], 'r', encoding='utf-8') as file:
                        justjoin_data = json.load(file)
                        
                    for job_data in justjoin_data:
                        title = job_data['title'][0] if isinstance(job_data['title'], list) and job_data['title'] else ''
                        description = ' '.join(job_data.get('description', []))
                        
                        # Skip Polish content
                        if self.is_polish_text(title) or self.is_polish_text(description):
                            self.stdout.write(f'Skipping job with Polish content: {title}')
                            jobs_skipped_polish += 1
                            continue
                            
                        # Skip non-tech jobs
                        if not self.is_tech_job(title, description):
                            jobs_skipped_non_tech += 1
                            continue
                            
                        # Format job data
                        formatted_description = self.format_justjoin_description(job_data.get('description', []))
                        formatted_salary = self.format_justjoin_salary(job_data.get('salary', []))
                        tech_stack = self.format_tech_stack(job_data.get('tech_stack', []))
                        
                        # Download company logo
                        logo = self.download_logo(job_data.get('logo', ''))
                        
                        # Prepare job data
                        job_fields = {
                            'title': title,
                            'company': job_data.get('company', 'Unknown Company'),
                            'location': job_data.get('location', 'Remote'),
                            'job_type': job_data.get('type_of_work', 'Not specified'),
                            'experience_level': job_data.get('experience', 'Not specified'),
                            'employment_type': job_data.get('employment_type', 'Not specified'),
                            'salary': formatted_salary,
                            'description': formatted_description,
                            'tech_stack': tech_stack,
                            'source': 'justjoin.it',
                            'job_url': job_data.get('job_post_url', ''),
                            'posted_date': timezone.now(),
                            'operating_mode': job_data.get('operating_type', 'Not specified')
                        }
                        
                        # Try to get existing job
                        existing_job = Job.objects.filter(
                            title=title,
                            company=job_fields['company'],
                            source='justjoin.it'
                        ).first()
                        
                        if existing_job:
                            # Update existing job
                            for key, value in job_fields.items():
                                setattr(existing_job, key, value)
                            if logo:
                                existing_job.company_logo = logo
                            existing_job.save()
                            jobs_updated += 1
                            self.stdout.write(f'Updated job: {title} at {job_fields["company"]}')
                        else:
                            # Create new job
                            job = Job(**job_fields)
                            if logo:
                                job.company_logo = logo
                            job.save()
                            jobs_created += 1
                            self.stdout.write(f'Created job: {title} at {job_fields["company"]}')
                            
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing JustJoin.it data: {str(e)}')
                    )

            # Print final summary
            self.stdout.write('\nImport completed:')
            self.stdout.write(f'Created: {jobs_created} jobs')
            self.stdout.write(f'Updated: {jobs_updated} jobs')
            self.stdout.write(f'Skipped Polish jobs: {jobs_skipped_polish}')
            self.stdout.write(f'Skipped non-tech jobs: {jobs_skipped_non_tech}')

            # After successful import, clear the JSON files
            if options['nofluff']:
                self.clear_json_file(options['nofluff'])
            if options['desc']:
                self.clear_json_file(options['desc'])
            if options['response']:
                self.clear_json_file(options['response'])
            if options['justjoin']:
                self.clear_json_file(options['justjoin'])

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