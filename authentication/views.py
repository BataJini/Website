from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import Job, CustomUser, PolishCity, JobApplication  # Import the JobApplication model
from django.utils import timezone
from datetime import timedelta
from django.contrib.admin.views.decorators import staff_member_required
import logging
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import ValidationError

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

    # Get total number of unique active jobs (after grouping)
    total_jobs = len(job_groups)

    context = {
        'jobs': jobs_list,
        'query': query,
        'location': location,
        'remote': remote,
        'fulltime': fulltime,
        'parttime': parttime,
        'total_jobs': total_jobs,
    }
    return render(request, 'index.html', context)

def job_detail(request, job_slug):
    logger.debug(f'Accessing job_detail view with job_slug: {job_slug}')
    try:
        # Find the job by matching the slug - include archived jobs for viewing
        jobs = Job.objects.all()  # Include all jobs, even archived ones
        job = None
        for j in jobs:
            if j.get_url_slug() == job_slug:
                job = j
                break
        
        if not job:
            raise Job.DoesNotExist
            
        logger.debug(f'Found job: {job.title}')
        
        # Add a warning message if the job is archived
        if job.is_archived:
            messages.warning(request, 'This job posting has been archived and may no longer be active.')
        
        # Handle job application submission
        if request.method == 'POST':
            # First record the application if the user is a logged-in candidate
            application_recorded = False
            if request.user.is_authenticated and request.user.user_type == 'candidate':
                # Create or update application
                application, created = JobApplication.objects.get_or_create(
                    user=request.user,
                    job=job,
                    defaults={'status': 'applied'}
                )
                application_recorded = True
                
                if created:
                    messages.success(request, f'Your application for {job.title} has been recorded!')
                else:
                    messages.info(request, f'You have already applied for this job on {application.applied_date.strftime("%B %d, %Y")}.')
            
            # Then handle the redirect, regardless of whether we recorded an application
            if job.job_url:
                return redirect(job.job_url)
            else:
                # If no URL is available, just show a success message for anonymous users
                if not application_recorded:
                    messages.success(request, 'Your application has been submitted successfully!')
                return redirect('authentication:job_detail', job_slug=job.get_url_slug())
        
        # Check if the user has already applied for this job
        has_applied = False
        if request.user.is_authenticated and request.user.user_type == 'candidate':
            has_applied = JobApplication.objects.filter(user=request.user, job=job).exists()
        
        # Find similar jobs based on tags, title keywords, and job type
        similar_jobs = Job.objects.filter(
            is_archived=False
        ).exclude(id=job.id).order_by('-is_featured', '-posted_date')
        
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
                    ).exclude(id=job.id).exclude(
                        id__in=[j.id for j in similar_jobs]
                    ).order_by('-is_featured', '-posted_date')
                    
                    similar_jobs = similar_jobs + list(type_jobs)
        
        # Limit to maximum 5 jobs
        similar_jobs = similar_jobs[:5]
        
    except Job.DoesNotExist:
        logger.error(f'Job with slug {job_slug} not found')
        return render(request, '404.html', {'message': 'Job not found'}, status=404)
    except Exception as e:
        logger.error(f'Error retrieving job with slug {job_slug}: {str(e)}')
        return render(request, '404.html', {'message': 'An error occurred'}, status=404)
    
    context = {
        'job': job,
        'similar_jobs': similar_jobs,
        'has_applied': has_applied
    }
    return render(request, 'authentication/job_detail.html', context)

def signup_view(request):
    # Determine user_type from GET on initial load, or POST on submission
    if request.method == 'POST':
        user_type = request.POST.get('user_type', 'candidate')
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if user.user_type == 'recruiter':
                messages.success(request, 'Company account created successfully! You can now post jobs.')
            else:
                messages.success(request, 'Candidate account created successfully! You can now apply for jobs.')
            return redirect('authentication:home')
        else:
            # Ensure the correct user_type is passed back on validation error
            messages.error(request, 'Please correct the errors below.')
    else: # GET request
        user_type = request.GET.get('type', 'candidate')
        if user_type not in ['candidate', 'recruiter']:
            user_type = 'candidate'
        form = CustomUserCreationForm(initial={'user_type': user_type})
    
    context = {
        'form': form,
        'user_type': user_type, # Use the determined user_type here
        'title': 'Create Company Account' if user_type == 'recruiter' else 'Create Candidate Account'
    }
    return render(request, 'authentication/signup.html', context)

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
    # Check if the user is a recruiter, if not redirect with error message
    if request.user.user_type != 'recruiter':
        messages.error(request, 'Only company users can post jobs. Please switch to a company account.')
        return redirect('authentication:home')
        
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
def archived_jobs(request):
    jobs = Job.objects.filter(created_by=request.user, is_archived=True)
    return render(request, 'authentication/archived_jobs.html', {'jobs': jobs})

@login_required
def archive_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if job.created_by == request.user or request.user.is_staff:
        job.is_archived = True
        job.save()
        messages.success(request, 'Job posting archived successfully.')
        return redirect('authentication:my_jobs')
    else:
        messages.error(request, 'You do not have permission to archive this job.')
        return redirect('authentication:home')

@login_required
def unarchive_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if job.created_by == request.user or request.user.is_staff:
        job.is_archived = False
        job.save()
        messages.success(request, 'Job posting unarchived successfully.')
        return redirect('authentication:archived_jobs')
    else:
        messages.error(request, 'You do not have permission to unarchive this job.')
        return redirect('authentication:home')

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

@login_required
def profile_view(request):
    user = request.user
    
    if request.method == 'POST':
        # Handle form submission to update profile
        user.full_name = request.POST.get('full_name', user.full_name)
        user.email = request.POST.get('email', user.email)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        
        # Handle company_name for recruiters
        if user.user_type == 'recruiter':
            user.company_name = request.POST.get('company_name', user.company_name)
        
        # Set password if provided
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password and password == password_confirm:
            user.set_password(password)
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, 'Password updated successfully.')
        elif password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'authentication/profile.html', {'user': user})
        
        try:
            user.full_clean()  # Validate the model
            user.save()
            messages.success(request, 'Profile updated successfully.')
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return render(request, 'authentication/profile.html', {'user': user})
            
        return redirect('authentication:profile')
    
    return render(request, 'authentication/profile.html', {'user': user})

@login_required
def my_applications(request):
    """View for candidates to see their job applications"""
    # Ensure the user is a candidate
    if request.user.user_type != 'candidate':
        messages.error(request, 'This feature is only available for candidate accounts.')
        return redirect('authentication:home')
    
    # Get all applications for the user
    applications = JobApplication.objects.filter(user=request.user).select_related('job')
    
    # Handle application status updates
    if request.method == 'POST':
        application_id = request.POST.get('application_id')
        new_status = request.POST.get('status')
        notes = request.POST.get('notes')
        
        if application_id and new_status:
            try:
                application = JobApplication.objects.get(id=application_id, user=request.user)
                application.status = new_status
                if notes:
                    application.notes = notes
                application.save()
                messages.success(request, 'Application status updated successfully.')
                return redirect('authentication:my_applications')
            except JobApplication.DoesNotExist:
                messages.error(request, 'Application not found.')
    
    context = {
        'applications': applications,
        'status_choices': JobApplication.STATUS_CHOICES
    }
    return render(request, 'authentication/my_applications.html', context)

@login_required
def delete_application(request, application_id):
    """View to delete a job application"""
    application = get_object_or_404(JobApplication, id=application_id, user=request.user)
    
    if request.method == 'POST':
        application.delete()
        messages.success(request, 'Application removed successfully.')
        return redirect('authentication:my_applications')
        
    return redirect('authentication:my_applications')

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
        # Split the query into individual terms, preserving quoted phrases
        import re
        search_terms = re.findall(r'"([^"]+)"|(\S+)', query)
        search_terms = [term[0] or term[1] for term in search_terms]
        
        # Start with a base Q object that matches everything
        query_filter = Q()
        
        for term in search_terms:
            # For each term, search in title, description, and requirements
            term_filter = (
                Q(title__icontains=term) |
                Q(description__icontains=term) |
                Q(requirements__icontains=term)
            )
            # Use AND logic between terms
            query_filter &= term_filter
        
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

def search_cities(request):
    query = request.GET.get('q', '')
    cities = PolishCity.objects.all().order_by('name')
    
    if query:
        # When searching, check in both English and Polish names
        cities = cities.filter(
            Q(name__icontains=query) | Q(name_pl__icontains=query)
        )
    
    # Limit to first 100 cities if no query to prevent overwhelming the dropdown
    if not query:
        cities = cities[:100]
    
    # Get the current language code
    language_code = request.LANGUAGE_CODE
    
    # Return city data with name in appropriate language
    data = [
        {
            'id': city.id, 
            'name': city.get_display_name(language_code)
        } 
        for city in cities
    ]
    return JsonResponse(data, safe=False)

def cookie_policy(request):
    """View for the cookie policy page"""
    return render(request, 'cookie_policy.html')

def privacy_policy(request):
    """View for the privacy policy page"""
    return render(request, 'privacy_policy.html')

def handle_404(request):
    """
    Handle 404 errors at the app level
    """
    return render(request, '404.html', {'message': 'Page not found'}, status=404)

