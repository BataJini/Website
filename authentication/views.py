from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import Job, CustomUser  # Import the Job model and CustomUser model
from django.utils import timezone
from datetime import timedelta
from django.contrib.admin.views.decorators import staff_member_required
import logging
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string

logger = logging.getLogger('django')

def home(request):
    # Get search parameters from the request
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    remote = request.GET.get('remote', False)
    fulltime = request.GET.get('fulltime', False)
    parttime = request.GET.get('parttime', False)

    # Filter jobs based on search parameters
    jobs = Job.objects.filter(is_archived=False).order_by('-is_featured', '-posted_date')

    if query:
        # Split the query into individual terms
        search_terms = query.replace('"', '').split()
        
        query_filter = Q()
        
        for term in search_terms:
            # Search in title, description, and requirements
            query_filter |= (
                Q(title__icontains=term) |
                Q(description__icontains=term) |
                Q(requirements__icontains=term)
            )
        
        jobs = jobs.filter(query_filter)

    if location:
        jobs = jobs.filter(location__icontains=location)

    if remote:
        jobs = jobs.filter(is_remote=True)

    if fulltime:
        jobs = jobs.filter(type='Full-time')

    if parttime:
        jobs = jobs.filter(type='Part-time')

    # Group jobs by title and company, combining locations
    job_groups = {}
    
    # Mark jobs as new if they were posted within the last 2 days
    now = timezone.now()
    two_days_ago = now - timedelta(days=2)

    for job in jobs:
        key = (job.title.lower(), job.company.lower())
        if key not in job_groups:
            # Use this job as the base
            job.is_new = job.posted_date >= two_days_ago
            if Job.objects.filter(id=job.id, is_featured=True).exists():
                job.is_featured = True
            
            # Initialize combined locations
            job.combined_locations = {job.location}
            if job.is_remote:
                job.combined_locations.add('Remote')
            
            job_groups[key] = job
        else:
            # Update existing job with additional location
            base_job = job_groups[key]
            base_job.combined_locations.add(job.location)
            if job.is_remote:
                base_job.combined_locations.add('Remote')
            
            # Keep featured status if either job is featured
            if Job.objects.filter(id=job.id, is_featured=True).exists():
                base_job.is_featured = True
            
            # Keep newer posted date
            if job.posted_date > base_job.posted_date:
                base_job.posted_date = job.posted_date
                base_job.is_new = job.posted_date >= two_days_ago

    # Convert combined locations to string
    jobs_list = []
    for job in job_groups.values():
        job.location = ' / '.join(sorted(job.combined_locations))
        jobs_list.append(job)

    # Sort the final list by featured status and posted date
    jobs_list.sort(key=lambda x: (-x.is_featured, -x.posted_date.timestamp()))

    context = {
        'query': query,
        'location': location,
        'remote': remote,
        'fulltime': fulltime,
        'parttime': parttime,
        'jobs': jobs_list
    }

    return render(request, 'index.html', context)

def job_detail(request, job_id):
    logger.debug(f'Accessing job_detail view with job_id: {job_id}')
    try:
        job = Job.objects.get(id=job_id, is_archived=False)
        logger.debug(f'Found job: {job.title}')
        
        # Handle job application submission
        if request.method == 'POST':
            # Redirect to the company's application website if available
            if job.job_url:
                return redirect(job.job_url)
            else:
                # If no URL is available, just show a success message
                messages.success(request, 'Your application has been submitted successfully!')
                return redirect('authentication:job_detail', job_id=job_id)
        
        # Find similar jobs based on tags, title keywords, and job type
        similar_jobs = Job.objects.filter(
            is_archived=False
        ).exclude(id=job_id).order_by('-is_featured', '-posted_date')
        
        # First priority: Match by tags
        if job.tags.exists():
            tagged_jobs = similar_jobs.filter(tags__in=job.tags.all()).distinct()
            if tagged_jobs.count() >= 5:
                similar_jobs = tagged_jobs[:5]
            else:
                # Second priority: Match by title keywords
                title_words = [word.lower() for word in job.title.split() if len(word) > 3]
                title_filter = Q()
                for word in title_words:
                    title_filter |= Q(title__icontains=word)
                
                # Combine tag matches with title matches
                keyword_jobs = similar_jobs.filter(title_filter).exclude(id__in=tagged_jobs.values_list('id', flat=True))
                similar_jobs = list(tagged_jobs) + list(keyword_jobs)
                
                # Third priority: Match by job type if we still need more
                if len(similar_jobs) < 5:
                    type_jobs = Job.objects.filter(
                        type=job.type, is_archived=False
                    ).exclude(id=job_id).exclude(
                        id__in=[j.id for j in similar_jobs]
                    ).order_by('-is_featured', '-posted_date')
                    
                    similar_jobs = similar_jobs + list(type_jobs)
        
        # Fallback: If no similar jobs found by tags or keywords, use job type
        else:
            title_words = [word.lower() for word in job.title.split() if len(word) > 3]
            title_filter = Q()
            for word in title_words:
                title_filter |= Q(title__icontains=word)
            
            keyword_jobs = similar_jobs.filter(title_filter)
            if keyword_jobs.count() >= 5:
                similar_jobs = keyword_jobs[:5]
            else:
                # Use job type as fallback
                type_jobs = similar_jobs.filter(type=job.type).exclude(
                    id__in=keyword_jobs.values_list('id', flat=True)
                )
                similar_jobs = list(keyword_jobs) + list(type_jobs)
        
        # Limit to maximum 5 jobs
        similar_jobs = similar_jobs[:5]
        
    except Job.DoesNotExist:
        logger.error(f'Job with id {job_id} not found')
        return render(request, '404.html', {'message': 'Job not found'}, status=404)
    except Exception as e:
        logger.error(f'Error retrieving job {job_id}: {str(e)}')
        return render(request, '404.html', {'message': 'An error occurred'}, status=404)
    
    context = {
        'job': job,
        'similar_jobs': similar_jobs
    }
    return render(request, 'authentication/job_detail.html', context)

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('authentication:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'authentication/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('authentication:home')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'authentication/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('authentication:home')

@login_required
def post_job_view(request):
    if request.method == 'POST':
        # This is a placeholder for actual job posting logic
        # You would typically use a form to validate and save the data
        try:
            title = request.POST.get('title')
            company = request.POST.get('company')
            description = request.POST.get('description')
            location = request.POST.get('location')
            salary = request.POST.get('salary')
            job_type = request.POST.get('type')  # Changed from job_type to type
            is_remote = request.POST.get('is_remote') == 'on'
            is_featured = request.POST.get('is_featured') == 'on'
            
            # Get skills data
            skills_json = request.POST.get('skills', '[]')
            required_skills = request.POST.get('required_skills', '[]')
            
            # Process company logo if provided
            company_logo = None
            if 'company_logo' in request.FILES:
                company_logo = request.FILES['company_logo']
                
                # Validate logo size (max 2MB)
                if company_logo.size > 2 * 1024 * 1024:  # 2MB
                    messages.error(request, 'Company logo must be less than 2MB.')
                    return render(request, 'authentication/post_job.html')
                
                # Validate logo type
                allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
                if company_logo.content_type not in allowed_types:
                    messages.error(request, 'Invalid logo file type. Please upload JPEG, PNG, GIF, or WebP.')
                    return render(request, 'authentication/post_job.html')

            # Create a new job
            job = Job(
                title=title,
                company=company,
                description=description,
                location=location,
                salary=salary,
                type=job_type,
                is_remote=is_remote,
                is_featured=is_featured,
                posted_date=timezone.now(),
                created_by=request.user
            )
            
            # Save skills in the requirements field
            if skills_json:
                try:
                    import json
                    skills_list = json.loads(skills_json)
                    if skills_list:
                        # Add skills to requirements field for display in job detail
                        job.requirements = json.dumps(skills_list)
                except json.JSONDecodeError:
                    pass
                    
            # Save the job
            job.save()
            
            # Handle company logo upload
            if company_logo:
                job.company_logo = company_logo
                job.save()
                
                # Debug logging
                print(f"Logo uploaded: {job.company_logo}")
                print(f"Logo URL: {job.company_logo.url if job.company_logo else 'No logo'}")
                logger.debug(f"Company logo uploaded for job {job.id}: {job.company_logo}")
                logger.debug(f"Company logo URL: {job.company_logo.url if job.company_logo else 'No logo'}")

            messages.success(request, 'Job posted successfully!')
            return redirect('authentication:home')
        except Exception as e:
            messages.error(request, f'Error posting job: {str(e)}')

    return render(request, 'authentication/post_job.html')

@login_required
def my_jobs(request):
    jobs = Job.objects.filter(created_by=request.user, is_archived=False)
    return render(request, 'authentication/my_jobs.html', {'jobs': jobs})

@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if job.created_by == request.user or request.user.is_staff:
        job.delete()
        messages.success(request, 'Job posting deleted successfully.')
        return redirect('authentication:home')  # Changed from my_jobs to home
    else:
        messages.error(request, 'You do not have permission to delete this job.')
        return redirect('authentication:home')

@staff_member_required
def user_list(request):
    """View to display all registered users (only accessible to staff members)"""
    users = CustomUser.objects.all().order_by('-date_joined')
    return render(request, 'authentication/user_list.html', {'users': users})

def search_jobs_ajax(request):
    """AJAX view for searching jobs without page reload"""
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    remote = request.GET.get('remote', False)
    fulltime = request.GET.get('fulltime', False)
    parttime = request.GET.get('parttime', False)
    min_salary = request.GET.get('min_salary', None)
    max_salary = request.GET.get('max_salary', None)

    # Filter jobs based on search parameters
    jobs = Job.objects.filter(is_archived=False).order_by('-is_featured', '-posted_date')

    if query:
        # Split the query into individual terms
        search_terms = query.replace('"', '').split()
        
        query_filter = Q()
        
        for term in search_terms:
            # Search in title, description, and requirements
            query_filter |= (
                Q(title__icontains=term) |
                Q(description__icontains=term) |
                Q(requirements__icontains=term)
            )
        
        jobs = jobs.filter(query_filter)

    if location:
        jobs = jobs.filter(location__icontains=location)

    if remote:
        jobs = jobs.filter(is_remote=True)

    if fulltime:
        jobs = jobs.filter(type='Full-time')

    if parttime:
        jobs = jobs.filter(type='Part-time')
    
    # Handle salary range filtering
    if min_salary is not None or max_salary is not None:
        # Convert to integers
        min_salary = int(min_salary) if min_salary is not None else 0
        max_salary = int(max_salary) if max_salary is not None else float('inf')
        
        # Filter jobs that have a salary field first
        jobs_with_salary = []
        
        for job in jobs:
            # Only process jobs with salary information
            if job.salary:
                # Extract numeric values from salary string using regex
                # Common formats: "30000-40000", "30k-40k", "30,000 - 40,000", etc.
                import re
                # Extract all numbers from the salary string
                salary_numbers = re.findall(r'\d+[k,]?\d*', job.salary.lower())
                
                if salary_numbers:
                    # Process each extracted number
                    parsed_numbers = []
                    for num in salary_numbers:
                        # Remove commas
                        num = num.replace(',', '')
                        # Handle 'k' suffix (multiply by 1000)
                        if 'k' in num:
                            num = int(float(num.replace('k', '')) * 1000)
                        else:
                            num = int(num)
                        parsed_numbers.append(num)
                    
                    # If we have at least one number
                    if parsed_numbers:
                        # If there's only one number, assume it's the minimum
                        if len(parsed_numbers) == 1:
                            job_min_salary = parsed_numbers[0]
                            job_max_salary = parsed_numbers[0]
                        else:
                            # Sort the numbers to find min and max
                            job_min_salary = min(parsed_numbers)
                            job_max_salary = max(parsed_numbers)
                        
                        # Check if the job's salary range overlaps with the requested range
                        if (job_max_salary >= min_salary and job_min_salary <= max_salary):
                            jobs_with_salary.append(job)
                else:
                    # No numbers found in salary string, skip this job
                    continue
            else:
                # No salary information
                continue
        
        # Replace the original jobs queryset with the filtered list
        jobs = jobs_with_salary

    # Group jobs by title and company, combining locations
    job_groups = {}
    
    # Mark jobs as new if they were posted within the last 2 days
    now = timezone.now()
    two_days_ago = now - timedelta(days=2)

    for job in jobs:
        key = (job.title.lower(), job.company.lower())
        if key not in job_groups:
            # Use this job as the base
            job.is_new = job.posted_date >= two_days_ago
            if Job.objects.filter(id=job.id, is_featured=True).exists():
                job.is_featured = True
            
            # Initialize combined locations
            job.combined_locations = {job.location}
            if job.is_remote:
                job.combined_locations.add('Remote')
            
            job_groups[key] = job
        else:
            # Update existing job with additional location
            base_job = job_groups[key]
            base_job.combined_locations.add(job.location)
            if job.is_remote:
                base_job.combined_locations.add('Remote')
            
            # Keep featured status if either job is featured
            if Job.objects.filter(id=job.id, is_featured=True).exists():
                base_job.is_featured = True
            
            # Keep newer posted date
            if job.posted_date > base_job.posted_date:
                base_job.posted_date = job.posted_date
                base_job.is_new = job.posted_date >= two_days_ago

    # Convert combined locations to string
    jobs_list = []
    for job in job_groups.values():
        job.location = ' / '.join(sorted(job.combined_locations))
        jobs_list.append(job)

    # Sort the final list by featured status and posted date
    jobs_list.sort(key=lambda x: (-x.is_featured, -x.posted_date.timestamp()))

    # Render just the job listings HTML
    html = render_to_string('job_listings_partial.html', {'jobs': jobs_list})
    
    return JsonResponse({
        'html': html,
        'count': len(jobs_list)
    })

