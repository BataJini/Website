from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from taggit.managers import TaggableManager

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    salary = models.CharField(max_length=100, blank=True, null=True)
    job_url = models.URLField(blank=True, null=True)
    is_remote = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    type = models.CharField(max_length=50, choices=[
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Temporary', 'Temporary')
    ], default='Full-time')
    posted_date = models.DateTimeField(default=timezone.now)
    requirements = models.TextField(blank=True, null=True)
    nice_to_have = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='jobs', null=True, blank=True)
    
    # Add company logo field
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    
    # Add skills as tags
    tags = TaggableManager(blank=True, verbose_name="Skills")

    def __str__(self):
        return f"{self.title} at {self.company}"

    class Meta:
        unique_together = ('title', 'company', 'location')
        ordering = ['-posted_date']