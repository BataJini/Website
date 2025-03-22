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
    
    # Debug: Print featured jobs to console
    featured_jobs = Job.objects.filter(is_featured=True, is_archived=False)
    print(f"FEATURED JOBS: {featured_jobs.count()}")
    for job in featured_jobs:
        print(f"Featured job: {job.id} - {job.title} - is_featured={job.is_featured}")

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

    # Mark jobs as new if they were posted within the last 2 days
    now = timezone.now()
    two_days_ago = now - timedelta(days=2)

    # Create a new list to ensure featured flag persists
    jobs_list = []
    for job in jobs:
        # Clone the job to make sure properties don't get lost
        job.is_new = job.posted_date >= two_days_ago
        # Explicitly set is_featured
        if Job.objects.filter(id=job.id, is_featured=True).exists():
            job.is_featured = True
            print(f"Setting job {job.id} - {job.title} as featured in template")
        
        jobs_list.append(job)

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
    except Job.DoesNotExist:
        logger.error(f'Job with id {job_id} not found')
        return render(request, '404.html', {'message': 'Job not found'}, status=404)
    except Exception as e:
        logger.error(f'Error retrieving job {job_id}: {str(e)}')
        return render(request, '404.html', {'message': 'An error occurred'}, status=404)
    
    context = {
        'job': job
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
    return render(request, 'admin/user_list.html', {'users': users})

def search_jobs_ajax(request):
    """AJAX view for searching jobs without page reload"""
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

    # Mark jobs as new if they were posted within the last 2 days
    now = timezone.now()
    two_days_ago = now - timedelta(days=2)

    # Create a new list to ensure featured flag persists
    jobs_list = []
    for job in jobs:
        # Clone the job to make sure properties don't get lost
        job.is_new = job.posted_date >= two_days_ago
        # Explicitly set is_featured
        if Job.objects.filter(id=job.id, is_featured=True).exists():
            job.is_featured = True
        
        jobs_list.append(job)

    # Render just the job listings HTML
    html = render_to_string('job_listings_partial.html', {'jobs': jobs_list})
    
    return JsonResponse({
        'html': html,
        'count': len(jobs_list)
    })

