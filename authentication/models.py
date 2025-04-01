from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager
from django.core.exceptions import ValidationError
from django.utils.text import slugify

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('candidate', 'Candidate'),
        ('recruiter', 'Recruiter'),
    ]
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='candidate')
    company_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.user_type == 'recruiter':
            if not self.company_name:
                raise ValidationError({'company_name': 'Company name is required for recruiters.'})
            if not self.phone_number:
                raise ValidationError({'phone_number': 'Phone number is required for recruiters.'})

class Job(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    company = models.CharField(_('Company'), max_length=255)
    description = models.TextField(_('Description'))
    location = models.CharField(_('Location'), max_length=255)
    salary = models.CharField(_('Salary'), max_length=100, blank=True, null=True)
    job_url = models.URLField(_('Job URL'), blank=True, null=True)
    is_remote = models.BooleanField(_('Remote'), default=False)
    is_featured = models.BooleanField(_('Featured'), default=False)
    is_archived = models.BooleanField(_('Archived'), default=False)
    type = models.CharField(_('Job Type'), max_length=50, choices=[
        ('Full-time', _('Full-time')),
        ('Part-time', _('Part-time')),
        ('Contract', _('Contract')),
        ('Temporary', _('Temporary'))
    ], default='Full-time')
    posted_date = models.DateTimeField(_('Posted Date'), default=timezone.now)
    requirements = models.TextField(_('Requirements'), blank=True, null=True)
    nice_to_have = models.TextField(_('Nice to Have'), blank=True, null=True)
    created_by = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='jobs', null=True, blank=True, verbose_name=_('Created By'))
    
    # Add company logo field
    company_logo = models.ImageField(_('Company Logo'), upload_to='company_logos/', blank=True, null=True)
    
    # Add skills as tags
    tags = TaggableManager(blank=True, verbose_name=_("Skills"))

    def __str__(self):
        return f"{self.title} at {self.company}"

    def get_url_slug(self):
        """
        Returns the URL-friendly slug for the job posting
        """
        # Create slug from title and company
        title_slug = slugify(self.title)
        company_slug = slugify(self.company)
        # Return the combined slug
        return f"{title_slug}-{company_slug}"

    class Meta:
        unique_together = ('title', 'company', 'location')
        ordering = ['-posted_date']
        verbose_name = _('Job')
        verbose_name_plural = _('Jobs')

class PolishCity(models.Model):
    name = models.CharField(_('Name'), max_length=100, unique=True)
    name_pl = models.CharField(_('Polish Name'), max_length=100, blank=True, null=True)
    voivodeship = models.CharField(_('Voivodeship'), max_length=100, blank=True, null=True)  # województwo
    population = models.IntegerField(_('Population'), blank=True, null=True)

    def __str__(self):
        return self.name
    
    def get_display_name(self, language_code='en'):
        if language_code == 'pl' and self.name_pl:
            return self.name_pl
        return self.name

    class Meta:
        verbose_name = _('Polish City')
        verbose_name_plural = _('Polish Cities')
        ordering = ['name']